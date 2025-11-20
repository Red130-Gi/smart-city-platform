import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Input, Attention
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from prophet import Prophet
import joblib
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FutureTrafficPredictor:
    """Advanced future traffic prediction system supporting multi-day forecasting"""
    
    def __init__(self, model_type='ensemble'):
        """
        Initialize the future traffic predictor
        
        Args:
            model_type: 'lstm', 'xgboost', 'prophet', or 'ensemble'
        """
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.feature_columns = None
        self.sequence_length = 24  # 2 hours of 5-minute intervals for context
        self.forecast_horizons = {
            '1h': 12,    # 1 hour ahead
            '3h': 36,    # 3 hours ahead
            '6h': 72,    # 6 hours ahead
            '12h': 144,  # 12 hours ahead
            '1d': 288,   # 1 day ahead
            '3d': 864,   # 3 days ahead
            '7d': 2016   # 7 days ahead
        }
        self.historical_data = None
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive temporal features for future prediction"""
        df = df.copy()
        
        # Basic temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['year'] = df['timestamp'].dt.year
        df['week_of_year'] = df['timestamp'].dt.isocalendar().week
        df['quarter'] = df['timestamp'].dt.quarter
        
        # Cyclic encoding for temporal features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Binary features
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_holiday'] = self.is_holiday(df['timestamp']).astype(int)
        
        # Rush hour indicators with more granularity
        morning_rush = df['hour'].isin([7, 8, 9])
        evening_rush = df['hour'].isin([17, 18, 19])
        df['is_morning_rush'] = morning_rush.astype(int)
        df['is_evening_rush'] = evening_rush.astype(int)
        df['is_rush_hour'] = (morning_rush | evening_rush).astype(int)
        
        # Time periods
        df['time_period'] = pd.cut(
            df['hour'],
            bins=[0, 6, 10, 14, 18, 22, 24],
            labels=['night', 'morning', 'midday', 'afternoon', 'evening', 'late_night']
        )
        
        # Season (simplified for demo - in production, use actual seasons)
        df['season'] = pd.cut(
            df['month'],
            bins=[0, 3, 6, 9, 12],
            labels=['winter', 'spring', 'summer', 'fall']
        )
        
        # Create dummy variables
        time_dummies = pd.get_dummies(df['time_period'], prefix='period')
        season_dummies = pd.get_dummies(df['season'], prefix='season')
        df = pd.concat([df, time_dummies, season_dummies], axis=1)
        df = df.drop(columns=['time_period', 'season'])
        
        return df
    
    def create_historical_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract historical patterns for similar time periods"""
        df = df.copy()
        
        # Same hour previous days
        for days_back in [1, 7, 14, 28]:
            col_name = f'same_hour_{days_back}d_ago'
            df[f'speed_{col_name}'] = df.groupby(['sensor_id', 'hour'])['speed_kmh'].shift(days_back * 288)
            df[f'flow_{col_name}'] = df.groupby(['sensor_id', 'hour'])['vehicle_flow'].shift(days_back * 288)
            
        # Same day of week previous weeks
        for weeks_back in [1, 2, 4]:
            col_name = f'same_dow_{weeks_back}w_ago'
            df[f'speed_{col_name}'] = df.groupby(['sensor_id', 'day_of_week', 'hour'])['speed_kmh'].shift(weeks_back * 2016)
            df[f'flow_{col_name}'] = df.groupby(['sensor_id', 'day_of_week', 'hour'])['vehicle_flow'].shift(weeks_back * 2016)
        
        # Monthly patterns
        df['speed_monthly_avg'] = df.groupby(['sensor_id', 'month', 'hour'])['speed_kmh'].transform('mean')
        df['flow_monthly_avg'] = df.groupby(['sensor_id', 'month', 'hour'])['vehicle_flow'].transform('mean')
        
        # Day of week patterns
        df['speed_dow_avg'] = df.groupby(['sensor_id', 'day_of_week', 'hour'])['speed_kmh'].transform('mean')
        df['flow_dow_avg'] = df.groupby(['sensor_id', 'day_of_week', 'hour'])['vehicle_flow'].transform('mean')
        
        return df
    
    def is_holiday(self, dates: pd.Series) -> pd.Series:
        """Check if dates are holidays (simplified for demo)"""
        # In production, use actual holiday calendar
        holidays = [
            '2024-01-01', '2024-05-01', '2024-07-14', '2024-08-15',
            '2024-11-01', '2024-11-11', '2024-12-25'
        ]
        holiday_dates = pd.to_datetime(holidays)
        return dates.dt.date.isin(holiday_dates)
    
    def build_lstm_model(self, input_shape: Tuple[int, int]) -> Model:
        """Build LSTM model for multi-horizon forecasting"""
        inputs = Input(shape=input_shape)
        
        # First LSTM layer with return sequences
        x = LSTM(128, return_sequences=True, dropout=0.2)(inputs)
        x = LSTM(64, return_sequences=True, dropout=0.2)(x)
        
        # Attention mechanism
        attention = Attention()([x, x])
        x = tf.keras.layers.Add()([x, attention])
        
        # Final LSTM layer
        x = LSTM(32, dropout=0.2)(x)
        
        # Dense layers for each forecast horizon
        outputs = {}
        for horizon_name, horizon_steps in self.forecast_horizons.items():
            horizon_output = Dense(64, activation='relu')(x)
            horizon_output = Dropout(0.2)(horizon_output)
            horizon_output = Dense(32, activation='relu')(horizon_output)
            outputs[horizon_name] = Dense(1, name=f'output_{horizon_name}')(horizon_output)
        
        model = Model(inputs=inputs, outputs=list(outputs.values()))
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def build_xgboost_model(self) -> Dict[str, xgb.XGBRegressor]:
        """Build XGBoost models for each forecast horizon"""
        models = {}
        
        for horizon_name, horizon_steps in self.forecast_horizons.items():
            models[horizon_name] = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
        
        return models
    
    def build_prophet_model(self, df: pd.DataFrame, road_id: str) -> Prophet:
        """Build Prophet model for long-term forecasting"""
        # Prepare data for Prophet
        prophet_df = df[df['sensor_id'] == road_id][['timestamp', 'speed_kmh']].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Create Prophet model with custom seasonalities
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10
        )
        
        # Add custom seasonalities
        model.add_seasonality(name='rush_hour', period=1, fourier_order=8)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Add holidays (in production, use actual holidays)
        holidays = pd.DataFrame({
            'holiday': ['holiday'] * 7,
            'ds': pd.to_datetime(['2024-01-01', '2024-05-01', '2024-07-14', 
                                 '2024-08-15', '2024-11-01', '2024-11-11', '2024-12-25']),
            'lower_window': 0,
            'upper_window': 1,
        })
        
        model.holidays = holidays
        model.fit(prophet_df)
        
        return model
    
    def train(self, df: pd.DataFrame, target_col: str = 'speed_kmh'):
        """Train all models"""
        print(f"Training {self.model_type} model(s)...")
        
        # Store historical data for future predictions
        self.historical_data = df.copy()
        
        # Create features
        df = self.create_temporal_features(df)
        df = self.create_historical_patterns(df)
        
        # Prepare features and target
        feature_cols = [col for col in df.columns if col not in 
                       ['timestamp', 'sensor_id', 'road_id', target_col, 'location']]
        self.feature_columns = feature_cols
        
        X = df[feature_cols].values
        y = df[target_col].values
        
        # Scale features
        self.scalers['features'] = StandardScaler()
        X_scaled = self.scalers['features'].fit_transform(X)
        
        self.scalers['target'] = MinMaxScaler()
        y_scaled = self.scalers['target'].fit_transform(y.reshape(-1, 1)).ravel()
        
        if self.model_type in ['lstm', 'ensemble']:
            # Prepare sequences for LSTM
            X_seq, y_seq = self.prepare_multivariate_sequences(X_scaled, y_scaled)
            
            # Train LSTM
            model = self.build_lstm_model(X_seq.shape[1:])
            
            # Prepare multi-horizon targets
            y_multi = {}
            for horizon_name, horizon_steps in self.forecast_horizons.items():
                y_horizon = []
                for i in range(len(X_seq)):
                    if i + horizon_steps < len(y_scaled):
                        y_horizon.append(y_scaled[i + horizon_steps])
                    else:
                        y_horizon.append(y_scaled[-1])  # Use last value for edge cases
                y_multi[horizon_name] = np.array(y_horizon)
            
            # Train model
            early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(factor=0.5, patience=5)
            
            model.fit(
                X_seq,
                list(y_multi.values()),
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                callbacks=[early_stopping, reduce_lr],
                verbose=1
            )
            
            self.models['lstm'] = model
        
        if self.model_type in ['xgboost', 'ensemble']:
            # Train XGBoost models
            xgb_models = self.build_xgboost_model()
            
            for horizon_name, model in xgb_models.items():
                horizon_steps = self.forecast_horizons[horizon_name]
                
                # Create lagged target
                y_horizon = np.roll(y_scaled, -horizon_steps)
                y_horizon[-horizon_steps:] = y_scaled[-horizon_steps:].mean()
                
                # Train model
                model.fit(X_scaled, y_horizon)
                
            self.models['xgboost'] = xgb_models
        
        if self.model_type in ['prophet', 'ensemble']:
            # Train Prophet models for each road
            prophet_models = {}
            for road_id in df['sensor_id'].unique():
                prophet_models[road_id] = self.build_prophet_model(df, road_id)
            
            self.models['prophet'] = prophet_models
        
        print("Training completed!")
    
    def prepare_multivariate_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM training"""
        X_seq, y_seq = [], []
        
        max_horizon = max(self.forecast_horizons.values())
        for i in range(self.sequence_length, len(X) - max_horizon):
            X_seq.append(X[i - self.sequence_length:i])
            y_seq.append(y[i])
        
        return np.array(X_seq), np.array(y_seq)
    
    def predict_future(self, 
                       road_id: str, 
                       target_datetime: datetime,
                       current_datetime: Optional[datetime] = None) -> Dict:
        """
        Predict traffic conditions at a specific future time
        
        Args:
            road_id: ID of the road/sensor to predict
            target_datetime: Target datetime for prediction
            current_datetime: Current datetime (defaults to now)
        
        Returns:
            Dictionary with predictions and confidence scores
        """
        if current_datetime is None:
            current_datetime = datetime.now()
        
        # Calculate time difference
        time_diff = target_datetime - current_datetime
        hours_ahead = time_diff.total_seconds() / 3600
        
        # Select appropriate horizon
        if hours_ahead <= 1:
            horizon = '1h'
        elif hours_ahead <= 3:
            horizon = '3h'
        elif hours_ahead <= 6:
            horizon = '6h'
        elif hours_ahead <= 12:
            horizon = '12h'
        elif hours_ahead <= 24:
            horizon = '1d'
        elif hours_ahead <= 72:
            horizon = '3d'
        else:
            horizon = '7d'
        
        predictions = {}
        confidences = {}
        
        # Get historical context
        context_data = self.get_historical_context(road_id, current_datetime)
        
        if 'lstm' in self.models and context_data is not None:
            # LSTM prediction
            X_context = self.prepare_context_features(context_data)
            X_scaled = self.scalers['features'].transform(X_context)
            X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
            
            lstm_pred = self.models['lstm'].predict(X_seq)[self.forecast_horizons[horizon]]
            predictions['lstm'] = self.scalers['target'].inverse_transform(lstm_pred.reshape(-1, 1))[0, 0]
            confidences['lstm'] = self.calculate_confidence(hours_ahead, 'lstm')
        
        if 'xgboost' in self.models and context_data is not None:
            # XGBoost prediction
            X_context = self.prepare_context_features(context_data)
            X_scaled = self.scalers['features'].transform(X_context[-1:])
            
            xgb_pred = self.models['xgboost'][horizon].predict(X_scaled)
            predictions['xgboost'] = self.scalers['target'].inverse_transform(xgb_pred.reshape(-1, 1))[0, 0]
            confidences['xgboost'] = self.calculate_confidence(hours_ahead, 'xgboost')
        
        if 'prophet' in self.models and road_id in self.models['prophet']:
            # Prophet prediction
            future_df = self.models['prophet'][road_id].make_future_dataframe(
                periods=int(hours_ahead * 12),  # 5-minute intervals
                freq='5T'
            )
            prophet_pred = self.models['prophet'][road_id].predict(future_df)
            
            # Find the closest prediction to target time
            closest_idx = (prophet_pred['ds'] - target_datetime).abs().argmin()
            predictions['prophet'] = prophet_pred.iloc[closest_idx]['yhat']
            confidences['prophet'] = self.calculate_confidence(hours_ahead, 'prophet')
        
        # Ensemble prediction
        if len(predictions) > 0:
            weights = {model: conf for model, conf in confidences.items()}
            total_weight = sum(weights.values())
            
            ensemble_pred = sum(
                predictions[model] * weights[model] / total_weight 
                for model in predictions
            )
            
            # Calculate congestion level
            congestion_level = self.calculate_congestion_level(ensemble_pred)
            
            return {
                'road_id': road_id,
                'target_datetime': target_datetime.isoformat(),
                'predicted_speed_kmh': float(ensemble_pred),
                'congestion_level': congestion_level,
                'confidence': float(sum(confidences.values()) / len(confidences)),
                'prediction_horizon_hours': hours_ahead,
                'model_predictions': predictions,
                'model_confidences': confidences
            }
        
        return {
            'road_id': road_id,
            'target_datetime': target_datetime.isoformat(),
            'error': 'Unable to generate prediction',
            'reason': 'No trained models available or insufficient data'
        }
    
    def get_historical_context(self, road_id: str, current_datetime: datetime) -> Optional[pd.DataFrame]:
        """Get historical data context for prediction"""
        if self.historical_data is None:
            return None
        
        # Filter data for the specific road
        road_data = self.historical_data[self.historical_data['sensor_id'] == road_id].copy()
        
        if road_data.empty:
            return None
        
        # Get recent data up to current datetime
        road_data = road_data[road_data['timestamp'] <= current_datetime]
        
        # Sort by timestamp
        road_data = road_data.sort_values('timestamp')
        
        # Return last sequence_length records
        return road_data.tail(self.sequence_length * 2)
    
    def prepare_context_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features from context data"""
        df = self.create_temporal_features(df)
        df = self.create_historical_patterns(df)
        
        if self.feature_columns:
            return df[self.feature_columns].values
        
        return df.select_dtypes(include=[np.number]).values
    
    def calculate_confidence(self, hours_ahead: float, model_type: str) -> float:
        """Calculate confidence score based on prediction horizon and model type"""
        # Base confidence scores
        base_confidence = {
            'lstm': 0.85,
            'xgboost': 0.80,
            'prophet': 0.75
        }
        
        # Decay factor based on hours ahead
        if hours_ahead <= 1:
            decay = 0.95
        elif hours_ahead <= 6:
            decay = 0.90
        elif hours_ahead <= 24:
            decay = 0.80
        elif hours_ahead <= 72:
            decay = 0.65
        else:
            decay = 0.50
        
        return base_confidence.get(model_type, 0.70) * decay
    
    def calculate_congestion_level(self, speed_kmh: float) -> str:
        """Calculate congestion level from speed"""
        if speed_kmh >= 45:
            return 'low'
        elif speed_kmh >= 30:
            return 'medium'
        elif speed_kmh >= 15:
            return 'high'
        else:
            return 'severe'
    
    def save_models(self, path: str):
        """Save all trained models"""
        import os
        os.makedirs(path, exist_ok=True)
        
        if 'lstm' in self.models:
            self.models['lstm'].save(f"{path}/lstm_model.h5")
        
        if 'xgboost' in self.models:
            for horizon, model in self.models['xgboost'].items():
                joblib.dump(model, f"{path}/xgboost_{horizon}.pkl")
        
        if 'prophet' in self.models:
            for road_id, model in self.models['prophet'].items():
                joblib.dump(model, f"{path}/prophet_{road_id}.pkl")
        
        # Save scalers
        joblib.dump(self.scalers, f"{path}/scalers.pkl")
        
        # Save feature columns
        joblib.dump(self.feature_columns, f"{path}/feature_columns.pkl")
        
        print(f"Models saved to {path}")
    
    def load_models(self, path: str):
        """Load saved models"""
        import os
        
        if os.path.exists(f"{path}/lstm_model.h5"):
            self.models['lstm'] = tf.keras.models.load_model(f"{path}/lstm_model.h5")
        
        # Load XGBoost models
        xgb_models = {}
        for horizon in self.forecast_horizons.keys():
            if os.path.exists(f"{path}/xgboost_{horizon}.pkl"):
                xgb_models[horizon] = joblib.load(f"{path}/xgboost_{horizon}.pkl")
        if xgb_models:
            self.models['xgboost'] = xgb_models
        
        # Load Prophet models
        prophet_models = {}
        for file in os.listdir(path):
            if file.startswith('prophet_') and file.endswith('.pkl'):
                road_id = file.replace('prophet_', '').replace('.pkl', '')
                prophet_models[road_id] = joblib.load(f"{path}/{file}")
        if prophet_models:
            self.models['prophet'] = prophet_models
        
        # Load scalers and feature columns
        if os.path.exists(f"{path}/scalers.pkl"):
            self.scalers = joblib.load(f"{path}/scalers.pkl")
        
        if os.path.exists(f"{path}/feature_columns.pkl"):
            self.feature_columns = joblib.load(f"{path}/feature_columns.pkl")
        
        print(f"Models loaded from {path}")
