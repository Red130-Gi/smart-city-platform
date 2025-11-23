"""
Optimized Traffic Prediction Models
Target: MAE < 5 km/h (from 6.63 km/h)

Optimizations:
1. Improved XGBoost hyperparameters
2. Bidirectional LSTM with more units
3. Advanced feature engineering
4. Weighted ensemble
5. Better validation strategy
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import joblib
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class OptimizedTrafficPredictor:
    """Optimized traffic prediction system - Target MAE < 5 km/h"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = None
        self.sequence_length = 12  # 1 hour
        self.forecast_horizon = 1   # 5 minutes ahead
        self.ensemble_weights = {'xgboost': 0.4, 'lightgbm': 0.3, 'lstm': 0.3}
        
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering for better MAE"""
        df = df.copy()
        
        # === TEMPORAL FEATURES ===
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_holiday'] = 0  # Can be improved with real holiday data
        
        # === RUSH HOUR FEATURES ===
        df['is_morning_rush'] = df['hour'].isin([7, 8, 9]).astype(int)
        df['is_evening_rush'] = df['hour'].isin([17, 18, 19]).astype(int)
        df['is_rush_hour'] = (df['is_morning_rush'] | df['is_evening_rush']).astype(int)
        
        # === TIME OF DAY (with sine/cosine encoding) ===
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # === LAG FEATURES (1, 2, 3, 6, 12 periods = 5, 10, 15, 30, 60 min) ===
        for lag in [1, 2, 3, 6, 12]:
            df[f'speed_lag_{lag}'] = df.groupby('sensor_id')['speed_kmh'].shift(lag)
            df[f'flow_lag_{lag}'] = df.groupby('sensor_id')['vehicle_flow'].shift(lag)
            df[f'occupancy_lag_{lag}'] = df.groupby('sensor_id')['occupancy_percent'].shift(lag)
        
        # === ROLLING STATISTICS (windows: 3, 6, 12 = 15, 30, 60 min) ===
        for window in [3, 6, 12]:
            # Speed statistics
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
            
            # Flow statistics
            df[f'flow_rolling_sum_{window}'] = df.groupby('sensor_id')['vehicle_flow'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
            df[f'flow_rolling_mean_{window}'] = df.groupby('sensor_id')['vehicle_flow'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
        
        # === EXPONENTIAL WEIGHTED MOVING AVERAGE ===
        df['speed_ewm_short'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.ewm(span=3, adjust=False).mean()
        )
        df['speed_ewm_long'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.ewm(span=12, adjust=False).mean()
        )
        
        # === CHANGE FEATURES ===
        df['speed_change'] = df.groupby('sensor_id')['speed_kmh'].diff()
        df['speed_change_rate'] = df['speed_change'] / (df['speed_kmh'].shift(1) + 1e-5)
        df['speed_acceleration'] = df.groupby('sensor_id')['speed_change'].diff()
        
        # === CONGESTION INDICATORS ===
        df['congestion_score'] = (60 - df['speed_kmh']) / 60  # Normalized 0-1
        df['is_congested'] = (df['speed_kmh'] < 25).astype(int)
        df['is_free_flow'] = (df['speed_kmh'] > 50).astype(int)
        
        # === INTERACTION FEATURES ===
        df['speed_flow_ratio'] = df['speed_kmh'] / (df['vehicle_flow'] + 1)
        df['occupancy_speed_product'] = df['occupancy_percent'] * df['speed_kmh']
        
        # === FILL MISSING VALUES ===
        df = df.fillna(method='ffill').fillna(method='bfill')
        num_cols = df.select_dtypes(include=[np.number]).columns
        df[num_cols] = df[num_cols].fillna(0)
        
        return df
    
    def prepare_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM training"""
        X_seq, y_seq = [], []
        
        for i in range(self.sequence_length, len(X) - self.forecast_horizon):
            X_seq.append(X[i - self.sequence_length:i])
            y_seq.append(y[i + self.forecast_horizon - 1])
        
        return np.array(X_seq), np.array(y_seq)
    
    def build_optimized_lstm(self, input_shape: Tuple) -> tf.keras.Model:
        """Build optimized Bidirectional LSTM model"""
        model = Sequential([
            # First Bidirectional LSTM layer
            Bidirectional(LSTM(150, return_sequences=True), input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.3),
            
            # Second Bidirectional LSTM layer
            Bidirectional(LSTM(100, return_sequences=True)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Third LSTM layer
            LSTM(50, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        optimizer = Adam(learning_rate=0.0005)  # Lower learning rate
        model.compile(
            optimizer=optimizer,
            loss='huber',  # More robust to outliers than MSE
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train_optimized_xgboost(self, X_train, y_train, X_val, y_val):
        """Train XGBoost with optimized hyperparameters"""
        # Optimized parameters for better MAE
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,              # Reduced from 8 for better generalization
            'learning_rate': 0.05,       # Lower learning rate
            'n_estimators': 500,         # More trees
            'subsample': 0.85,           # Slightly higher
            'colsample_bytree': 0.85,    # Slightly higher
            'min_child_weight': 3,       # Regularization
            'gamma': 0.1,                # Regularization
            'reg_alpha': 0.1,            # L1 regularization
            'reg_lambda': 1.0,           # L2 regularization
            'random_state': 42
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=50,
            verbose=False
        )
        
        return model
    
    def train_optimized_lightgbm(self, X_train, y_train, X_val, y_val):
        """Train LightGBM with optimized hyperparameters"""
        params = {
            'objective': 'regression',
            'metric': 'mae',             # Optimize for MAE directly
            'num_leaves': 50,            # Increased from 31
            'learning_rate': 0.03,       # Lower learning rate
            'n_estimators': 500,         # More trees
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_samples': 20,     # Regularization
            'reg_alpha': 0.1,            # L1 regularization
            'reg_lambda': 1.0,           # L2 regularization
            'random_state': 42
        }
        
        model = lgb.LGBMRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
        )
        
        return model
    
    def train(self, df: pd.DataFrame):
        """Train all optimized models"""
        mlflow.set_experiment("traffic_prediction_optimized")
        
        with mlflow.start_run(run_name=f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Advanced feature engineering
            print("Creating advanced features...")
            df_features = self.create_advanced_features(df)
            
            # Select features (exclude non-numeric columns)
            exclude_cols = ['timestamp', 'sensor_id', 'speed_kmh', 
                           'road_id', 'road_name', 'zone_id', 'congestion_level', 'data_quality']
            feature_cols = [col for col in df_features.columns 
                          if col not in exclude_cols and df_features[col].dtype in ['int64', 'float64']]
            self.feature_columns = feature_cols
            print(f"Using {len(feature_cols)} features")
            
            X = df_features[feature_cols].values
            y = df_features['speed_kmh'].values
            
            # Time-based split (80/20)
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Validation split from training
            val_size = int(0.15 * len(X_train))
            X_val = X_train[-val_size:]
            y_val = y_train[-val_size:]
            X_train = X_train[:-val_size]
            y_train = y_train[:-val_size]
            
            # Scale features
            print("Scaling features...")
            self.scalers['features'] = StandardScaler()
            X_train_scaled = self.scalers['features'].fit_transform(X_train)
            X_val_scaled = self.scalers['features'].transform(X_val)
            X_test_scaled = self.scalers['features'].transform(X_test)
            
            # === TRAIN XGBOOST ===
            print("\n=== Training Optimized XGBoost ===")
            self.models['xgboost'] = self.train_optimized_xgboost(
                X_train_scaled, y_train, X_val_scaled, y_val
            )
            xgb_pred = self.models['xgboost'].predict(X_test_scaled)
            xgb_mae = mean_absolute_error(y_test, xgb_pred)
            xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
            xgb_r2 = r2_score(y_test, xgb_pred)
            print(f"XGBoost - MAE: {xgb_mae:.2f} km/h | RMSE: {xgb_rmse:.2f} | R²: {xgb_r2:.4f}")
            mlflow.log_metric("xgboost_mae", xgb_mae)
            mlflow.log_metric("xgboost_rmse", xgb_rmse)
            mlflow.log_metric("xgboost_r2", xgb_r2)
            
            # === TRAIN LIGHTGBM ===
            print("\n=== Training Optimized LightGBM ===")
            self.models['lightgbm'] = self.train_optimized_lightgbm(
                X_train_scaled, y_train, X_val_scaled, y_val
            )
            lgb_pred = self.models['lightgbm'].predict(X_test_scaled)
            lgb_mae = mean_absolute_error(y_test, lgb_pred)
            lgb_rmse = np.sqrt(mean_squared_error(y_test, lgb_pred))
            lgb_r2 = r2_score(y_test, lgb_pred)
            print(f"LightGBM - MAE: {lgb_mae:.2f} km/h | RMSE: {lgb_rmse:.2f} | R²: {lgb_r2:.4f}")
            mlflow.log_metric("lightgbm_mae", lgb_mae)
            mlflow.log_metric("lightgbm_rmse", lgb_rmse)
            mlflow.log_metric("lightgbm_r2", lgb_r2)
            
            # === TRAIN LSTM ===
            print("\n=== Training Optimized Bidirectional LSTM ===")
            X_train_seq, y_train_seq = self.prepare_sequences(X_train_scaled, y_train)
            X_val_seq, y_val_seq = self.prepare_sequences(X_val_scaled, y_val)
            X_test_seq, y_test_seq = self.prepare_sequences(X_test_scaled, y_test)
            
            input_shape = (X_train_seq.shape[1], X_train_seq.shape[2])
            self.models['lstm'] = self.build_optimized_lstm(input_shape)
            
            callbacks = [
                EarlyStopping(monitor='val_mae', patience=15, restore_best_weights=True, mode='min'),
                ReduceLROnPlateau(monitor='val_mae', factor=0.5, patience=5, min_lr=1e-6, mode='min'),
                ModelCheckpoint('best_lstm_model.h5', monitor='val_mae', save_best_only=True, mode='min')
            ]
            
            history = self.models['lstm'].fit(
                X_train_seq, y_train_seq,
                validation_data=(X_val_seq, y_val_seq),
                epochs=100,
                batch_size=64,
                callbacks=callbacks,
                verbose=0
            )
            
            lstm_pred = self.models['lstm'].predict(X_test_seq, verbose=0).flatten()
            lstm_mae = mean_absolute_error(y_test_seq, lstm_pred)
            lstm_rmse = np.sqrt(mean_squared_error(y_test_seq, lstm_pred))
            lstm_r2 = r2_score(y_test_seq, lstm_pred)
            print(f"LSTM - MAE: {lstm_mae:.2f} km/h | RMSE: {lstm_rmse:.2f} | R²: {lstm_r2:.4f}")
            mlflow.log_metric("lstm_mae", lstm_mae)
            mlflow.log_metric("lstm_rmse", lstm_rmse)
            mlflow.log_metric("lstm_r2", lstm_r2)
            
            # === ENSEMBLE WEIGHTED AVERAGE ===
            print("\n=== Creating Weighted Ensemble ===")
            # Align predictions (LSTM has fewer predictions due to sequencing)
            min_len = min(len(xgb_pred), len(lgb_pred), len(lstm_pred))
            xgb_pred_aligned = xgb_pred[-min_len:]
            lgb_pred_aligned = lgb_pred[-min_len:]
            lstm_pred_aligned = lstm_pred[-min_len:]
            y_test_aligned = y_test[-min_len:]
            
            # Weighted ensemble
            ensemble_pred = (
                self.ensemble_weights['xgboost'] * xgb_pred_aligned +
                self.ensemble_weights['lightgbm'] * lgb_pred_aligned +
                self.ensemble_weights['lstm'] * lstm_pred_aligned
            )
            
            ensemble_mae = mean_absolute_error(y_test_aligned, ensemble_pred)
            ensemble_rmse = np.sqrt(mean_squared_error(y_test_aligned, ensemble_pred))
            ensemble_r2 = r2_score(y_test_aligned, ensemble_pred)
            print(f"Ensemble - MAE: {ensemble_mae:.2f} km/h | RMSE: {ensemble_rmse:.2f} | R²: {ensemble_r2:.4f}")
            mlflow.log_metric("ensemble_mae", ensemble_mae)
            mlflow.log_metric("ensemble_rmse", ensemble_rmse)
            mlflow.log_metric("ensemble_r2", ensemble_r2)
            
            # Log best model
            best_mae = min(xgb_mae, lgb_mae, lstm_mae, ensemble_mae)
            if best_mae == ensemble_mae:
                best_model = "Ensemble"
            elif best_mae == xgb_mae:
                best_model = "XGBoost"
            elif best_mae == lgb_mae:
                best_model = "LightGBM"
            else:
                best_model = "LSTM"
            
            print(f"\n🏆 Best Model: {best_model} with MAE: {best_mae:.2f} km/h")
            mlflow.log_param("best_model", best_model)
            mlflow.log_metric("best_mae", best_mae)
            
            # Save models
            joblib.dump(self.models['xgboost'], 'xgboost_optimized.pkl')
            joblib.dump(self.models['lightgbm'], 'lightgbm_optimized.pkl')
            self.models['lstm'].save('lstm_optimized.h5')
            joblib.dump(self.scalers, 'scalers_optimized.pkl')
            
            return {
                'xgboost_mae': xgb_mae,
                'lightgbm_mae': lgb_mae,
                'lstm_mae': lstm_mae,
                'ensemble_mae': ensemble_mae,
                'best_model': best_model,
                'best_mae': best_mae
            }
    
    def predict_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble prediction"""
        # Scale features
        X_scaled = self.scalers['features'].transform(X)
        
        # XGBoost prediction
        xgb_pred = self.models['xgboost'].predict(X_scaled)
        
        # LightGBM prediction
        lgb_pred = self.models['lightgbm'].predict(X_scaled)
        
        # LSTM prediction (requires sequencing)
        if len(X_scaled) >= self.sequence_length:
            X_seq = []
            for i in range(self.sequence_length, len(X_scaled) + 1):
                X_seq.append(X_scaled[i - self.sequence_length:i])
            X_seq = np.array(X_seq)
            lstm_pred_seq = self.models['lstm'].predict(X_seq, verbose=0).flatten()
            
            # Align predictions
            lstm_pred = np.concatenate([np.full(self.sequence_length, lstm_pred_seq[0]), lstm_pred_seq])
        else:
            lstm_pred = np.full(len(X_scaled), np.mean(xgb_pred))
        
        # Weighted ensemble
        ensemble_pred = (
            self.ensemble_weights['xgboost'] * xgb_pred +
            self.ensemble_weights['lightgbm'] * lgb_pred +
            self.ensemble_weights['lstm'] * lstm_pred[:len(xgb_pred)]
        )
        
        return ensemble_pred
