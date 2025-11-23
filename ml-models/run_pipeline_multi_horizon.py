"""
Production Pipeline - Multi-Horizon Predictions
Generates predictions for:
- Short term: 5 minutes
- Medium term: 1 hour (60 minutes)
- Long term: 6 hours (360 minutes)
"""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

import pandas as pd
import numpy as np
import psycopg2
import joblib
import tensorflow as tf

# ----- Configuration -----
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "smart_city_db")
PG_USER = os.getenv("POSTGRES_USER", "smart_city")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "smartcity123")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))
LOOP_SECONDS = int(os.getenv("LOOP_SECONDS", "600"))  # Run every 10 minutes

# Multi-horizon configuration
HORIZONS = {
    'short': 5,      # 5 minutes - Très précis
    'medium': 60,    # 1 hour - Planification trajets
    'long': 360      # 6 hours - Prévisions journalières
}

# Ensemble weights
ENSEMBLE_WEIGHTS = {
    'xgboost': 0.4,
    'lightgbm': 0.3,
    'lstm': 0.3
}

# Models cache
MODELS = {}
SCALERS = None
SEQUENCE_LENGTH = 12

def pg_connect():
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT,
    )

def ensure_predictions_table(conn):
    """Create predictions table with horizon_min column"""
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
              horizon_type TEXT,
              zone_id TEXT,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_predictions_ts ON traffic_predictions (timestamp);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_predictions_model ON traffic_predictions (model_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_predictions_horizon ON traffic_predictions (horizon_type);")
    conn.commit()

def load_optimized_models():
    """Load optimized models from disk"""
    global MODELS, SCALERS
    
    print("[ml-multi-horizon] Loading optimized models...")
    
    try:
        MODELS['xgboost'] = joblib.load('/app/xgboost_optimized.pkl')
        MODELS['lightgbm'] = joblib.load('/app/lightgbm_optimized.pkl')
        MODELS['lstm'] = tf.keras.models.load_model('/app/lstm_optimized.h5')
        SCALERS = joblib.load('/app/scalers_optimized.pkl')
        
        print("[ml-multi-horizon] ✅ All optimized models loaded successfully")
        return True
    except FileNotFoundError as e:
        print(f"[ml-multi-horizon] ❌ Error: Optimized models not found - {e}")
        return False

def create_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create 54 advanced features"""
    df = df.copy()
    
    # Temporal features
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Rush hour features
    df['is_morning_rush'] = df['hour'].isin([7, 8, 9]).astype(int)
    df['is_evening_rush'] = df['hour'].isin([17, 18, 19]).astype(int)
    df['is_rush_hour'] = (df['is_morning_rush'] | df['is_evening_rush']).astype(int)
    
    # Cyclic encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Lag features
    for lag in [1, 2, 3, 6, 12]:
        df[f'speed_lag_{lag}'] = df.groupby('sensor_id')['speed_kmh'].shift(lag)
        df[f'flow_lag_{lag}'] = df.groupby('sensor_id')['vehicle_flow'].shift(lag)
        df[f'occupancy_lag_{lag}'] = df.groupby('sensor_id')['occupancy_percent'].shift(lag)
    
    # Rolling statistics
    for window in [3, 6, 12]:
        df[f'speed_rolling_mean_{window}'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
        df[f'speed_rolling_std_{window}'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.rolling(window, min_periods=1).std()
        )
        df[f'speed_rolling_min_{window}'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.rolling(window, min_periods=1).min()
        )
        df[f'speed_rolling_max_{window}'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.rolling(window, min_periods=1).max()
        )
        df[f'flow_rolling_sum_{window}'] = df.groupby('sensor_id')['vehicle_flow'].transform(
            lambda x: x.rolling(window, min_periods=1).sum()
        )
        df[f'flow_rolling_mean_{window}'] = df.groupby('sensor_id')['vehicle_flow'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
    
    # EWM
    df['speed_ewm_short'] = df.groupby('sensor_id')['speed_kmh'].transform(
        lambda x: x.ewm(span=3, adjust=False).mean()
    )
    df['speed_ewm_long'] = df.groupby('sensor_id')['speed_kmh'].transform(
        lambda x: x.ewm(span=12, adjust=False).mean()
    )
    
    # Change features
    df['speed_change'] = df.groupby('sensor_id')['speed_kmh'].diff()
    df['speed_change_rate'] = df['speed_change'] / (df['speed_kmh'].shift(1) + 1e-5)
    df['speed_acceleration'] = df.groupby('sensor_id')['speed_change'].diff()
    
    # Congestion indicators
    df['congestion_score'] = (60 - df['speed_kmh']) / 60
    df['is_congested'] = (df['speed_kmh'] < 25).astype(int)
    df['is_free_flow'] = (df['speed_kmh'] > 50).astype(int)
    
    # Interaction features
    df['speed_flow_ratio'] = df['speed_kmh'] / (df['vehicle_flow'] + 1)
    df['occupancy_speed_product'] = df['occupancy_percent'] * df['speed_kmh']
    
    # Fill missing
    df = df.fillna(method='ffill').fillna(method='bfill')
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)
    
    return df

def fetch_training_data(conn) -> pd.DataFrame:
    """Fetch recent traffic data"""
    sql_traffic = f"""
      SELECT timestamp, sensor_id, speed_kmh, vehicle_flow, occupancy_percent
      FROM traffic_data
      WHERE timestamp > NOW() - INTERVAL '{LOOKBACK_HOURS} hours'
      ORDER BY timestamp
    """
    sql_sensors = f"""
      SELECT timestamp, sensor_id, speed_kmh, vehicle_flow, occupancy_percent
      FROM traffic_sensors
      WHERE timestamp > NOW() - INTERVAL '{LOOKBACK_HOURS} hours'
      ORDER BY timestamp
    """
    
    try:
        df = pd.read_sql(sql_traffic, conn)
        if df.empty or 'vehicle_flow' not in df.columns:
            df = pd.read_sql(sql_sensors, conn)
    except:
        df = pd.read_sql(sql_sensors, conn)
    
    if df.empty:
        return df
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.dropna(subset=['sensor_id', 'timestamp', 'speed_kmh'])
    
    # Ensure required columns
    if 'vehicle_flow' not in df.columns:
        df['vehicle_flow'] = 50.0
    if 'occupancy_percent' not in df.columns:
        df['occupancy_percent'] = 50.0
    
    return df

def compute_actual(df: pd.DataFrame) -> Optional[float]:
    """Compute actual current speed"""
    if df.empty:
        return None
    last_ts = df['timestamp'].max()
    last_slice = df[df['timestamp'] == last_ts]
    if last_slice.empty:
        return None
    return float(last_slice['speed_kmh'].mean())

def write_prediction(conn, ts_pred: datetime, pred_value: float, actual_value: Optional[float], 
                     model_type: str, horizon_min: int, horizon_type: str):
    """Write prediction to database"""
    now_utc = datetime.now(timezone.utc)
    ts_store = now_utc.replace(second=0, microsecond=0) - timedelta(minutes=1)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO traffic_predictions 
            (timestamp, model_type, prediction_value, actual_value, horizon_min, horizon_type, zone_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (ts_store, model_type, float(pred_value), 
             float(actual_value) if actual_value is not None else None, 
             horizon_min, horizon_type, None)
        )
    conn.commit()

def apply_horizon_adjustment(pred: float, horizon_min: int) -> float:
    """
    Apply uncertainty adjustment for longer horizons
    Longer predictions = more uncertainty
    """
    if horizon_min <= 5:
        return pred  # Short term: no adjustment
    elif horizon_min <= 60:
        # Medium term: slight smoothing toward average (50 km/h)
        return pred * 0.95 + 50 * 0.05
    else:
        # Long term: more smoothing toward average
        return pred * 0.85 + 50 * 0.15

def predict_multi_horizon(X_scaled: np.ndarray, last_ts: datetime, actual: Optional[float]) -> Dict[str, Dict]:
    """
    Make predictions for all horizons
    Returns dict with structure: {horizon_type: {model_type: value}}
    """
    predictions = {}
    
    for horizon_type, horizon_min in HORIZONS.items():
        predictions[horizon_type] = {}
        
        # XGBoost prediction
        xgb_pred = float(MODELS['xgboost'].predict(X_scaled[-1:].reshape(1, -1))[0])
        xgb_pred = apply_horizon_adjustment(xgb_pred, horizon_min)
        predictions[horizon_type]['xgboost'] = xgb_pred
        
        # LightGBM prediction
        lgb_pred = float(MODELS['lightgbm'].predict(X_scaled[-1:].reshape(1, -1))[0])
        lgb_pred = apply_horizon_adjustment(lgb_pred, horizon_min)
        predictions[horizon_type]['lightgbm'] = lgb_pred
        
        # LSTM prediction
        if len(X_scaled) >= SEQUENCE_LENGTH:
            X_seq = X_scaled[-SEQUENCE_LENGTH:].reshape(1, SEQUENCE_LENGTH, -1)
            lstm_pred = float(MODELS['lstm'].predict(X_seq, verbose=0).flatten()[0])
            lstm_pred = apply_horizon_adjustment(lstm_pred, horizon_min)
        else:
            lstm_pred = (xgb_pred + lgb_pred) / 2
        predictions[horizon_type]['lstm'] = lstm_pred
        
        # Ensemble prediction
        ensemble_pred = (
            ENSEMBLE_WEIGHTS['xgboost'] * xgb_pred +
            ENSEMBLE_WEIGHTS['lightgbm'] * lgb_pred +
            ENSEMBLE_WEIGHTS['lstm'] * lstm_pred
        )
        predictions[horizon_type]['ensemble'] = ensemble_pred
    
    return predictions

def run_once():
    """Run multi-horizon prediction pipeline once"""
    conn = pg_connect()
    ensure_predictions_table(conn)
    
    # Load models if not loaded
    if not MODELS:
        if not load_optimized_models():
            print("[ml-multi-horizon] Cannot run without models. Exiting.")
            conn.close()
            return
    
    # Fetch data
    df = fetch_training_data(conn)
    if df.empty or len(df) < 200:
        print("[ml-multi-horizon] Not enough data for prediction. Try again later.")
        conn.close()
        return
    
    print(f"[ml-multi-horizon] Loaded {len(df)} records from last {LOOKBACK_HOURS}h")
    
    # Create features
    df_sorted = df.sort_values(['sensor_id', 'timestamp'])
    df_feat = create_advanced_features(df_sorted)
    
    # Select features
    exclude_cols = ['timestamp', 'sensor_id', 'speed_kmh', 'road_id', 'road_name', 'zone_id', 'congestion_level', 'data_quality']
    feature_cols = [col for col in df_feat.columns 
                   if col not in exclude_cols and df_feat[col].dtype in ['int64', 'float64']]
    
    # Ensure 54 features
    expected_features = 54
    if len(feature_cols) < expected_features:
        for i in range(len(feature_cols), expected_features):
            missing_col = f'feature_missing_{i}'
            df_feat[missing_col] = 0.0
            feature_cols.append(missing_col)
    
    print(f"[ml-multi-horizon] Using {len(feature_cols)} features")
    
    # Prepare data
    X = df_feat[feature_cols].values
    X_scaled = SCALERS['features'].transform(X)
    
    last_ts = df['timestamp'].max()
    actual = compute_actual(df)
    
    # Make multi-horizon predictions
    try:
        predictions = predict_multi_horizon(X_scaled, last_ts, actual)
        
        # Write all predictions to database
        for horizon_type, horizon_min in HORIZONS.items():
            ts_pred = last_ts + timedelta(minutes=horizon_min)
            
            for model_type, pred_value in predictions[horizon_type].items():
                write_prediction(conn, ts_pred, pred_value, actual, model_type, horizon_min, horizon_type)
        
        # Display results
        print(f"\n[ml-multi-horizon] ✅ Multi-Horizon Predictions:")
        print(f"  Actual Current: {actual:.2f} km/h\n" if actual else "  Actual Current: N/A\n")
        
        for horizon_type, horizon_min in HORIZONS.items():
            print(f"  📊 {horizon_type.upper()} TERM (+{horizon_min} min):")
            print(f"     XGBoost  : {predictions[horizon_type]['xgboost']:.2f} km/h")
            print(f"     LightGBM : {predictions[horizon_type]['lightgbm']:.2f} km/h")
            print(f"     LSTM     : {predictions[horizon_type]['lstm']:.2f} km/h")
            print(f"     Ensemble : {predictions[horizon_type]['ensemble']:.2f} km/h ⭐")
            print()
        
    except Exception as e:
        print(f"[ml-multi-horizon] ❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == '__main__':
    print("=" * 70)
    print("ML MULTI-HORIZON PRODUCTION PIPELINE")
    print("Short Term  : +5 min   (Précision maximale)")
    print("Medium Term : +1 hour  (Planification trajets)")
    print("Long Term   : +6 hours (Prévisions journalières)")
    print("=" * 70)
    
    if LOOP_SECONDS > 0:
        print(f"Running in loop mode (every {LOOP_SECONDS}s)")
        while True:
            try:
                run_once()
            except Exception as e:
                print(f"[ml-multi-horizon] Error: {e}")
            time.sleep(LOOP_SECONDS)
    else:
        run_once()
