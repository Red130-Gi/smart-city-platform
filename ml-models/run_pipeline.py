import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import numpy as np
import psycopg2
import xgboost as xgb

from traffic_prediction import TrafficPredictor

# ----- Configuration (env overrides) -----
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "smart_city_db")
PG_USER = os.getenv("POSTGRES_USER", "smart_city")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "smartcity123")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))
FORECAST_HORIZON_MIN = int(os.getenv("FORECAST_HORIZON_MIN", "30"))  # minutes ahead (default 30)
LOOP_SECONDS = int(os.getenv("LOOP_SECONDS", "0"))  # 0 => run once

# TrafficPredictor uses sequence_length=12 (12 x 5min = 60min) and forecast_horizon=6 (30min) by default.
# We will rely on its internal horizon for LSTM.


def pg_connect():
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT,
    )


def ensure_predictions_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS traffic_predictions (
              id SERIAL PRIMARY KEY,
              timestamp TIMESTAMPTZ NOT NULL,
              model_type TEXT NOT NULL,
              prediction_value DOUBLE PRECISION NOT NULL,
              actual_value DOUBLE PRECISION,
              horizon_min INTEGER DEFAULT 0,
              zone_id TEXT,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_predictions_ts ON traffic_predictions (timestamp);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_predictions_model ON traffic_predictions (model_type);")
    conn.commit()


def quick_xgb_write(conn, df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    df_sorted = df.copy().sort_values(['sensor_id', 'timestamp'])
    predictor = TrafficPredictor()
    df_feat = predictor.create_features(df_sorted)
    feature_cols = [c for c in df_feat.columns if c not in ['timestamp', 'sensor_id', 'speed_kmh', 'road_id', 'road_name', 'zone_id']]
    mask = df_feat[feature_cols].notna().all(axis=1) & df_feat['speed_kmh'].notna()
    if mask.sum() < 50:
        return False
    X = df_feat.loc[mask, feature_cols].values
    y = df_feat.loc[mask, 'speed_kmh'].values
    model = xgb.XGBRegressor(objective='reg:squarederror', max_depth=6, learning_rate=0.1, n_estimators=120, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=2, verbosity=0)
    model.fit(X, y)
    last_row = df_feat.iloc[mask[mask].index[-1]:mask[mask].index[-1]+1][feature_cols].values
    pred = float(model.predict(last_row)[0])
    last_ts = df_sorted['timestamp'].max()
    ts_pred = last_ts + timedelta(minutes=FORECAST_HORIZON_MIN)
    actual = compute_actual(df_sorted)
    write_prediction(conn, ts_pred, pred, actual, 'xgboost')
    print(f"[ml-models] Quick XGBoost write ts={ts_pred.isoformat()} value={pred:.2f}")
    return True


def fetch_training_data(conn) -> pd.DataFrame:
    sql = f"""
      SELECT timestamp, sensor_id, speed_kmh, vehicle_flow, occupancy_percent
      FROM traffic_sensors
      WHERE timestamp > NOW() - INTERVAL '{LOOKBACK_HOURS} hours'
      ORDER BY timestamp
    """
    df = pd.read_sql(sql, conn)
    if df.empty:
        return df
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    # Basic cleaning
    df = df.dropna(subset=['sensor_id', 'timestamp', 'speed_kmh'])
    return df


def compute_actual(df: pd.DataFrame) -> Optional[float]:
    if df.empty:
        return None
    last_ts = df['timestamp'].max()
    last_slice = df[df['timestamp'] == last_ts]
    if last_slice.empty:
        return None
    return float(last_slice['speed_kmh'].mean())


def _round_minute(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0)


def write_prediction(conn, ts_pred: datetime, pred_value: float, actual_value: Optional[float], model_type: str):
    # Store slightly in the past to ensure $__timeFilter (to=now) includes it reliably
    now_utc = datetime.now(timezone.utc)
    ts_store = _round_minute(now_utc - timedelta(minutes=1))
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO traffic_predictions (timestamp, model_type, prediction_value, actual_value, horizon_min, zone_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (ts_store, model_type, float(pred_value), float(actual_value) if actual_value is not None else None, FORECAST_HORIZON_MIN, None)
        )
    conn.commit()


def run_once():
    conn = pg_connect()
    ensure_predictions_table(conn)

    df = fetch_training_data(conn)
    if df.empty or len(df) < 200:
        print("[ml-models] Not enough data for training. Try again later.")
        conn.close()
        return

    try:
        quick_xgb_write(conn, df)
    except Exception as e:
        print(f"[ml-models] Quick XGBoost write error: {e}")

    # Train complete models using TrafficPredictor
    predictor = TrafficPredictor(model_type='ensemble')
    print("[ml-models] Training full models (XGBoost, LightGBM, LSTM)...")
    metrics = predictor.train(df)
    print(f"[ml-models] Training metrics: {metrics}")

    # Prepare features for inference (both XGB and LSTM)
    df_feat = predictor.create_features(df.copy().sort_values(['sensor_id', 'timestamp']))
    X_all = df_feat[predictor.feature_columns].values
    X_scaled = predictor.scalers['features'].transform(X_all)

    last_ts = df['timestamp'].max()
    ts_pred = last_ts + timedelta(minutes=predictor.forecast_horizon * 5)
    actual = compute_actual(df)

    # XGBoost prediction (matches Grafana panel filter model_type='xgboost')
    try:
        xgb_pred = float(predictor.models['xgboost'].predict(X_scaled[-1:].copy())[0])
        write_prediction(conn, ts_pred, xgb_pred, actual, 'xgboost')
        print(f"[ml-models] Wrote XGBoost prediction ts={ts_pred.isoformat()} value={xgb_pred:.2f}")
    except Exception as e:
        print(f"[ml-models] XGBoost predict error: {e}")

    # Optionally also persist LSTM (not required by Grafana panel)
    try:
        if X_scaled.shape[0] >= predictor.sequence_length:
            X_seq = X_scaled[-predictor.sequence_length:].reshape(1, predictor.sequence_length, -1)
            lstm_pred = float(predictor.models['lstm'].predict(X_seq).flatten()[0])
            write_prediction(conn, ts_pred, lstm_pred, actual, 'lstm')
            print(f"[ml-models] Wrote LSTM prediction ts={ts_pred.isoformat()} value={lstm_pred:.2f}")
    except Exception as e:
        print(f"[ml-models] LSTM predict error: {e}")
    conn.close()


if __name__ == '__main__':
    if LOOP_SECONDS > 0:
        while True:
            try:
                run_once()
            except Exception as e:
                print(f"[ml-models] Error: {e}")
            time.sleep(LOOP_SECONDS)
    else:
        run_once()
