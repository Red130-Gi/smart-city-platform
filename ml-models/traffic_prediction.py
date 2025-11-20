import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Input, Attention, MultiHeadAttention
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import joblib
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TrafficPredictor:
    """Advanced traffic prediction system using ensemble methods"""
    
    def __init__(self, model_type='ensemble'):
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.feature_columns = None
        self.sequence_length = 12  # 1 hour of 5-minute intervals
        self.forecast_horizon = 6   # 30 minutes ahead
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal and spatial features for traffic prediction"""
        df = df.copy()
        
        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Time-based categories
        df['is_rush_hour'] = df['hour'].isin([7, 8, 9, 17, 18, 19]).astype(int)
        df['time_of_day'] = pd.cut(
            df['hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['night', 'morning', 'afternoon', 'evening']
        )
        tod_dummies = pd.get_dummies(df['time_of_day'], prefix='tod')
        df = pd.concat([df, tod_dummies], axis=1)
        df = df.drop(columns=['time_of_day'])
        
        # Lag features
        for lag in [1, 2, 3, 6, 12]:  # 5, 10, 15, 30, 60 minutes
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
            df[f'flow_rolling_sum_{window}'] = df.groupby('sensor_id')['vehicle_flow'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
        
        # Exponential weighted moving average
        df['speed_ewm'] = df.groupby('sensor_id')['speed_kmh'].transform(
            lambda x: x.ewm(span=6, adjust=False).mean()
        )
        
        # Speed change rate
        df['speed_change'] = df.groupby('sensor_id')['speed_kmh'].diff()
        df['speed_change_rate'] = df['speed_change'] / df['speed_kmh'].shift(1)
        
        # Congestion indicators
        df['congestion_score'] = (50 - df['speed_kmh']) / 50  # Normalized congestion
        df['is_congested'] = (df['speed_kmh'] < 25).astype(int)
        
        df = df.fillna(method='ffill')
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
    
    def build_lstm_model(self, input_shape: Tuple) -> tf.keras.Model:
        """Build LSTM model for traffic prediction"""
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def build_transformer_model(self, input_shape: Tuple) -> tf.keras.Model:
        """Build Transformer model for traffic prediction"""
        inputs = Input(shape=input_shape)
        
        # Multi-head attention
        attention = MultiHeadAttention(
            num_heads=4, 
            key_dim=32,
            dropout=0.1
        )(inputs, inputs)
        
        # Skip connection
        x = tf.keras.layers.Add()([inputs, attention])
        x = tf.keras.layers.LayerNormalization(epsilon=1e-6)(x)
        
        # Feed-forward network
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Dense(32, activation='relu')(x)
        x = Dropout(0.2)(x)
        outputs = Dense(1)(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """Train XGBoost model"""
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 8,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        return model
    
    def train_lightgbm(self, X_train, y_train, X_val, y_val):
        """Train LightGBM model"""
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'n_estimators': 200,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'random_state': 42
        }
        
        model = lgb.LGBMRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)],
        )
        
        return model
    
    def train(self, df: pd.DataFrame):
        """Train all models"""
        mlflow.set_experiment("traffic_prediction")
        
        with mlflow.start_run():
            # Feature engineering
            df_features = self.create_features(df)
            
            # Select features
            feature_cols = [col for col in df_features.columns 
                          if col not in ['timestamp', 'sensor_id', 'speed_kmh', 
                                       'road_id', 'road_name', 'zone_id', 'time_of_day']]
            self.feature_columns = feature_cols
            
            X = df_features[feature_cols].values
            y = df_features['speed_kmh'].values
            
            # Split data
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Further split train into train and validation
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scalers['features'] = StandardScaler()
            X_train_scaled = self.scalers['features'].fit_transform(X_train)
            X_val_scaled = self.scalers['features'].transform(X_val)
            X_test_scaled = self.scalers['features'].transform(X_test)
            
            # Train XGBoost
            print("Training XGBoost model...")
            self.models['xgboost'] = self.train_xgboost(
                X_train_scaled, y_train, X_val_scaled, y_val
            )
            xgb_pred = self.models['xgboost'].predict(X_test_scaled)
            xgb_mae = mean_absolute_error(y_test, xgb_pred)
            print(f"XGBoost MAE: {xgb_mae:.2f}")
            
            # Train LightGBM
            print("Training LightGBM model...")
            self.models['lightgbm'] = self.train_lightgbm(
                X_train_scaled, y_train, X_val_scaled, y_val
            )
            lgb_pred = self.models['lightgbm'].predict(X_test_scaled)
            lgb_mae = mean_absolute_error(y_test, lgb_pred)
            print(f"LightGBM MAE: {lgb_mae:.2f}")
            
            # Prepare sequences for LSTM
            X_seq_train, y_seq_train = self.prepare_sequences(X_train_scaled, y_train)
            X_seq_val, y_seq_val = self.prepare_sequences(X_val_scaled, y_val)
            X_seq_test, y_seq_test = self.prepare_sequences(X_test_scaled, y_test)
            
            # Train LSTM
            print("Training LSTM model...")
            self.models['lstm'] = self.build_lstm_model(
                (self.sequence_length, X_train_scaled.shape[1])
            )
            
            early_stop = EarlyStopping(patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(factor=0.5, patience=5)
            
            self.models['lstm'].fit(
                X_seq_train, y_seq_train,
                validation_data=(X_seq_val, y_seq_val),
                epochs=50,
                batch_size=32,
                callbacks=[early_stop, reduce_lr],
                verbose=0
            )
            
            lstm_pred = self.models['lstm'].predict(X_seq_test).flatten()
            lstm_mae = mean_absolute_error(y_seq_test, lstm_pred)
            print(f"LSTM MAE: {lstm_mae:.2f}")
            
            # Log metrics to MLflow
            mlflow.log_param("model_type", self.model_type)
            mlflow.log_param("sequence_length", self.sequence_length)
            mlflow.log_param("forecast_horizon", self.forecast_horizon)
            
            mlflow.log_metric("xgboost_mae", xgb_mae)
            mlflow.log_metric("lightgbm_mae", lgb_mae)
            mlflow.log_metric("lstm_mae", lstm_mae)
            
            # Save models
            mlflow.sklearn.log_model(self.models['xgboost'], "xgboost_model")
            mlflow.sklearn.log_model(self.models['lightgbm'], "lightgbm_model")
            mlflow.tensorflow.log_model(self.models['lstm'], "lstm_model")
            
            print("Training completed!")
            
            return {
                'xgboost_mae': xgb_mae,
                'lightgbm_mae': lgb_mae,
                'lstm_mae': lstm_mae
            }
    
    def predict(self, df: pd.DataFrame, use_ensemble: bool = True) -> np.ndarray:
        """Make predictions using trained models"""
        # Feature engineering
        df_features = self.create_features(df)
        X = df_features[self.feature_columns].values
        
        # Scale features
        X_scaled = self.scalers['features'].transform(X)
        
        predictions = {}
        
        # XGBoost prediction
        if 'xgboost' in self.models:
            predictions['xgboost'] = self.models['xgboost'].predict(X_scaled)
        
        # LightGBM prediction
        if 'lightgbm' in self.models:
            predictions['lightgbm'] = self.models['lightgbm'].predict(X_scaled)
        
        # LSTM prediction (needs sequences)
        if 'lstm' in self.models and len(X_scaled) >= self.sequence_length:
            X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
            predictions['lstm'] = self.models['lstm'].predict(X_seq).flatten()
        
        if use_ensemble and len(predictions) > 1:
            # Weighted ensemble
            weights = {'xgboost': 0.35, 'lightgbm': 0.35, 'lstm': 0.3}
            ensemble_pred = np.zeros_like(list(predictions.values())[0])
            
            for model_name, pred in predictions.items():
                ensemble_pred += weights.get(model_name, 0.33) * pred
            
            return ensemble_pred
        else:
            return list(predictions.values())[0] if predictions else np.array([])
    
    def save_models(self, path: str):
        """Save all models and scalers"""
        import os
        os.makedirs(path, exist_ok=True)
        
        # Save sklearn models
        for name, model in self.models.items():
            if name in ['xgboost', 'lightgbm']:
                joblib.dump(model, f"{path}/{name}.pkl")
            elif name == 'lstm':
                model.save(f"{path}/{name}")
        
        # Save scalers
        joblib.dump(self.scalers, f"{path}/scalers.pkl")
        
        # Save feature columns
        joblib.dump(self.feature_columns, f"{path}/feature_columns.pkl")
        
        print(f"Models saved to {path}")
    
    def load_models(self, path: str):
        """Load saved models and scalers"""
        import os
        
        # Load sklearn models
        if os.path.exists(f"{path}/xgboost.pkl"):
            self.models['xgboost'] = joblib.load(f"{path}/xgboost.pkl")
        
        if os.path.exists(f"{path}/lightgbm.pkl"):
            self.models['lightgbm'] = joblib.load(f"{path}/lightgbm.pkl")
        
        # Load LSTM model
        if os.path.exists(f"{path}/lstm"):
            self.models['lstm'] = tf.keras.models.load_model(f"{path}/lstm")
        
        # Load scalers
        self.scalers = joblib.load(f"{path}/scalers.pkl")
        
        # Load feature columns
        self.feature_columns = joblib.load(f"{path}/feature_columns.pkl")
        
        print(f"Models loaded from {path}")


class AnomalyDetector:
    """Detect anomalies in traffic patterns"""
    
    def __init__(self, contamination=0.1):
        from sklearn.ensemble import IsolationForest
        from sklearn.cluster import DBSCAN
        
        self.contamination = contamination
        self.models = {
            'isolation_forest': IsolationForest(
                contamination=contamination,
                random_state=42
            ),
            'autoencoder': None  # Will be built separately
        }
        self.scaler = StandardScaler()
    
    def build_autoencoder(self, input_dim: int) -> tf.keras.Model:
        """Build autoencoder for anomaly detection"""
        # Encoder
        encoder_input = Input(shape=(input_dim,))
        encoded = Dense(32, activation='relu')(encoder_input)
        encoded = Dense(16, activation='relu')(encoded)
        encoded = Dense(8, activation='relu')(encoded)
        
        # Decoder
        decoded = Dense(16, activation='relu')(encoded)
        decoded = Dense(32, activation='relu')(decoded)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)
        
        autoencoder = Model(encoder_input, decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        
        return autoencoder
    
    def train(self, df: pd.DataFrame):
        """Train anomaly detection models"""
        # Select features for anomaly detection
        features = ['speed_kmh', 'vehicle_flow', 'occupancy_percent']
        X = df[features].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        print("Training Isolation Forest...")
        self.models['isolation_forest'].fit(X_scaled)
        
        # Train Autoencoder
        print("Training Autoencoder...")
        self.models['autoencoder'] = self.build_autoencoder(X_scaled.shape[1])
        self.models['autoencoder'].fit(
            X_scaled, X_scaled,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        print("Anomaly detection training completed!")
    
    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in traffic data"""
        features = ['speed_kmh', 'vehicle_flow', 'occupancy_percent']
        X = df[features].values
        X_scaled = self.scaler.transform(X)
        
        # Isolation Forest predictions
        iso_predictions = self.models['isolation_forest'].predict(X_scaled)
        df['anomaly_isolation'] = (iso_predictions == -1).astype(int)
        
        # Autoencoder predictions
        if self.models['autoencoder']:
            reconstructions = self.models['autoencoder'].predict(X_scaled)
            mse = np.mean((X_scaled - reconstructions) ** 2, axis=1)
            threshold = np.percentile(mse, (1 - self.contamination) * 100)
            df['anomaly_autoencoder'] = (mse > threshold).astype(int)
        
        # Combined anomaly score
        df['is_anomaly'] = (df['anomaly_isolation'] | 
                           df.get('anomaly_autoencoder', 0)).astype(int)
        
        return df


class RouteOptimizer:
    """Optimize routes based on real-time traffic conditions"""
    
    def __init__(self):
        import networkx as nx
        self.graph = nx.DiGraph()
        self.zones = []
        self.roads = []
        
    def build_road_network(self, zones: List[Dict], roads: List[Dict]):
        """Build road network graph"""
        self.zones = zones
        self.roads = roads
        
        # Add nodes for zones
        for zone in zones:
            self.graph.add_node(zone['id'], **zone)
        
        # Add edges for roads
        for road in roads:
            for i in range(len(road['zones']) - 1):
                self.graph.add_edge(
                    road['zones'][i], 
                    road['zones'][i+1],
                    road_id=road['id'],
                    name=road['name'],
                    weight=1.0  # Default weight
                )
    
    def update_weights(self, traffic_conditions: pd.DataFrame):
        """Update edge weights based on traffic conditions"""
        for _, row in traffic_conditions.iterrows():
            if self.graph.has_edge(row.get('from_zone'), row.get('to_zone')):
                # Calculate weight based on congestion
                weight = 1.0 / (row['speed_kmh'] / 50)  # Inverse of normalized speed
                self.graph[row['from_zone']][row['to_zone']]['weight'] = weight
                self.graph[row['from_zone']][row['to_zone']]['current_speed'] = row['speed_kmh']
    
    def find_optimal_route(self, origin: str, destination: str, 
                          mode: str = 'fastest') -> Dict:
        """Find optimal route between two points"""
        import networkx as nx
        
        try:
            if mode == 'fastest':
                # Use Dijkstra for shortest weighted path
                path = nx.shortest_path(self.graph, origin, destination, weight='weight')
                distance = nx.shortest_path_length(self.graph, origin, destination, weight='weight')
            else:
                # Simple shortest path (fewest hops)
                path = nx.shortest_path(self.graph, origin, destination)
                distance = len(path) - 1
            
            # Calculate estimated time
            total_time = 0
            route_segments = []
            
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i+1]]
                segment_time = edge_data.get('weight', 1) * 5  # 5 minutes base time
                total_time += segment_time
                
                route_segments.append({
                    'from': path[i],
                    'to': path[i+1],
                    'road': edge_data.get('name', 'Unknown'),
                    'estimated_time': segment_time,
                    'current_speed': edge_data.get('current_speed', 50)
                })
            
            return {
                'path': path,
                'segments': route_segments,
                'total_distance': distance,
                'estimated_time': total_time,
                'mode': mode
            }
            
        except nx.NetworkXNoPath:
            return {
                'error': 'No route found',
                'origin': origin,
                'destination': destination
            }
    
    def multi_objective_optimization(self, origin: str, destination: str,
                                   objectives: List[str] = ['time', 'emissions']) -> List[Dict]:
        """Find Pareto-optimal routes considering multiple objectives"""
        import networkx as nx
        
        routes = []
        
        # Find k shortest paths
        try:
            k_paths = list(nx.shortest_simple_paths(
                self.graph, origin, destination, weight='weight'
            ))[:5]  # Get top 5 paths
            
            for path in k_paths:
                # Calculate metrics for each path
                total_time = 0
                total_emissions = 0
                
                for i in range(len(path) - 1):
                    edge_data = self.graph[path[i]][path[i+1]]
                    segment_time = edge_data.get('weight', 1) * 5
                    total_time += segment_time
                    
                    # Estimate emissions based on speed
                    speed = edge_data.get('current_speed', 50)
                    emissions = 150 * (1 + (50 - speed) / 50)  # Higher emissions in congestion
                    total_emissions += emissions
                
                routes.append({
                    'path': path,
                    'time': total_time,
                    'emissions': total_emissions,
                    'score': total_time * 0.6 + total_emissions * 0.4  # Weighted score
                })
            
            # Sort by score
            routes.sort(key=lambda x: x['score'])
            
        except nx.NetworkXNoPath:
            pass
        
        return routes


if __name__ == "__main__":
    # Example usage
    print("Initializing Traffic Prediction System...")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end='2024-01-07', freq='5T')
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'sensor_id': 'sensor-001',
        'speed_kmh': np.random.uniform(20, 60, len(dates)),
        'vehicle_flow': np.random.randint(50, 200, len(dates)),
        'occupancy_percent': np.random.uniform(20, 80, len(dates))
    })
    
    # Initialize and train predictor
    predictor = TrafficPredictor()
    print("Training models...")
    metrics = predictor.train(sample_data)
    print(f"Training metrics: {metrics}")
    
    # Save models
    predictor.save_models("./models")
    
    # Train anomaly detector
    detector = AnomalyDetector()
    detector.train(sample_data)
    
    # Detect anomalies
    anomalies = detector.detect(sample_data.tail(100))
    print(f"Detected {anomalies['is_anomaly'].sum()} anomalies")
    
    print("Traffic prediction system ready!")
