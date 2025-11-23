"""
Script to train optimized ML models
Goal: Reduce MAE from 6.63 km/h to < 5 km/h
"""

import sys
import os
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from traffic_prediction_optimized import OptimizedTrafficPredictor

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'smart_city_db'),
    'user': os.getenv('POSTGRES_USER', 'smart_city'),
    'password': os.getenv('POSTGRES_PASSWORD', 'smartcity123')
}

def load_training_data(hours=48):
    """Load traffic data from PostgreSQL for training"""
    print(f"Loading last {hours} hours of traffic data...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = f"""
    SELECT 
        timestamp,
        sensor_id,
        road_id,
        road_name,
        zone_id,
        speed_kmh,
        vehicle_flow,
        occupancy_percent,
        congestion_level
    FROM traffic_data
    WHERE timestamp > NOW() - INTERVAL '{hours} hours'
    ORDER BY timestamp ASC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Loaded {len(df):,} records")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Sensors: {df['sensor_id'].nunique()}")
    print(f"Avg speed: {df['speed_kmh'].mean():.2f} km/h")
    
    return df

def main():
    """Main training function"""
    print("=" * 60)
    print("OPTIMIZED ML MODEL TRAINING")
    print("Target: MAE < 5 km/h (Current: 6.63 km/h)")
    print("=" * 60)
    print()
    
    # Load data (48 hours for better patterns)
    df = load_training_data(hours=48)
    
    if len(df) < 1000:
        print("❌ Not enough data for training (minimum 1000 records)")
        print(f"   Found: {len(df)} records")
        print("   Waiting for more data generation...")
        return
    
    # Initialize optimized predictor
    print("\n" + "=" * 60)
    print("Initializing Optimized Traffic Predictor...")
    print("=" * 60)
    predictor = OptimizedTrafficPredictor()
    
    # Train models
    print("\nStarting training...")
    print("-" * 60)
    results = predictor.train(df)
    
    # Display results
    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    print(f"XGBoost MAE   : {results['xgboost_mae']:.2f} km/h")
    print(f"LightGBM MAE  : {results['lightgbm_mae']:.2f} km/h")
    print(f"LSTM MAE      : {results['lstm_mae']:.2f} km/h")
    print(f"Ensemble MAE  : {results['ensemble_mae']:.2f} km/h ⭐")
    print("=" * 60)
    print(f"\n🏆 Best Model: {results['best_model']}")
    print(f"📊 Best MAE: {results['best_mae']:.2f} km/h")
    
    # Check if target achieved
    if results['ensemble_mae'] < 5.0:
        print("\n✅ TARGET ACHIEVED! MAE < 5 km/h")
        improvement = ((6.63 - results['ensemble_mae']) / 6.63) * 100
        print(f"   Improvement: {improvement:.1f}% from baseline")
    else:
        gap = results['ensemble_mae'] - 5.0
        print(f"\n⚠️  Almost there! Gap: {gap:.2f} km/h from target")
        
    # Save confirmation
    print("\n📁 Models saved:")
    print("   - xgboost_optimized.pkl")
    print("   - lightgbm_optimized.pkl")
    print("   - lstm_optimized.h5")
    print("   - scalers_optimized.pkl")
    
    print("\n✅ Training completed successfully!")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
