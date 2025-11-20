from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.types import *
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../ml-models'))
from future_prediction import FutureTrafficPredictor
import pandas as pd
import numpy as np

class TrafficBatchProcessor:
    """Batch processing for historical traffic data and model training"""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("TrafficBatchProcessing") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.streaming.schemaInference", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        self.predictor = FutureTrafficPredictor(model_type='ensemble')
        
    def process_historical_data(self, input_path: str, output_path: str):
        """Process historical traffic data for model training"""
        
        # Read historical data
        df = self.spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(input_path)
        
        # Ensure timestamp is in correct format
        df = df.withColumn("timestamp", to_timestamp(col("timestamp")))
        
        # Create time-based features
        df = df.withColumn("hour", hour(col("timestamp"))) \
            .withColumn("day_of_week", dayofweek(col("timestamp"))) \
            .withColumn("month", month(col("timestamp"))) \
            .withColumn("week_of_year", weekofyear(col("timestamp"))) \
            .withColumn("is_weekend", 
                       when(col("day_of_week").isin(1, 7), 1).otherwise(0))
        
        # Calculate rush hour indicators
        df = df.withColumn("is_morning_rush",
                          when((col("hour") >= 7) & (col("hour") <= 9), 1).otherwise(0)) \
            .withColumn("is_evening_rush",
                       when((col("hour") >= 17) & (col("hour") <= 19), 1).otherwise(0)) \
            .withColumn("is_rush_hour",
                       when((col("is_morning_rush") == 1) | 
                           (col("is_evening_rush") == 1), 1).otherwise(0))
        
        # Window specifications for rolling calculations
        sensor_window = Window.partitionBy("sensor_id").orderBy("timestamp")
        time_window_15min = Window.partitionBy("sensor_id") \
            .orderBy(col("timestamp").cast("long")) \
            .rangeBetween(-900, 0)  # 15 minutes
        time_window_1hour = Window.partitionBy("sensor_id") \
            .orderBy(col("timestamp").cast("long")) \
            .rangeBetween(-3600, 0)  # 1 hour
        
        # Calculate lag features
        for lag in [1, 3, 6, 12, 24]:  # 5min, 15min, 30min, 1hour, 2hours
            df = df.withColumn(f"speed_lag_{lag}",
                              lag(col("speed_kmh"), lag).over(sensor_window)) \
                   .withColumn(f"flow_lag_{lag}",
                              lag(col("vehicle_flow"), lag).over(sensor_window)) \
                   .withColumn(f"occupancy_lag_{lag}",
                              lag(col("occupancy_percent"), lag).over(sensor_window))
        
        # Calculate rolling statistics
        df = df.withColumn("speed_avg_15min",
                          avg(col("speed_kmh")).over(time_window_15min)) \
               .withColumn("speed_std_15min",
                          stddev(col("speed_kmh")).over(time_window_15min)) \
               .withColumn("flow_sum_15min",
                          sum(col("vehicle_flow")).over(time_window_15min)) \
               .withColumn("speed_avg_1hour",
                          avg(col("speed_kmh")).over(time_window_1hour)) \
               .withColumn("flow_sum_1hour",
                          sum(col("vehicle_flow")).over(time_window_1hour))
        
        # Calculate speed change rate
        df = df.withColumn("speed_change",
                          col("speed_kmh") - lag(col("speed_kmh"), 1).over(sensor_window)) \
               .withColumn("speed_change_rate",
                          when(lag(col("speed_kmh"), 1).over(sensor_window) != 0,
                               col("speed_change") / lag(col("speed_kmh"), 1).over(sensor_window))
                          .otherwise(0))
        
        # Congestion scoring
        df = df.withColumn("congestion_score",
                          when(col("speed_kmh") >= 45, 0.0)
                          .when(col("speed_kmh") >= 30, 0.3)
                          .when(col("speed_kmh") >= 15, 0.6)
                          .otherwise(0.9)) \
               .withColumn("congestion_level",
                          when(col("speed_kmh") >= 45, "low")
                          .when(col("speed_kmh") >= 30, "medium")
                          .when(col("speed_kmh") >= 15, "high")
                          .otherwise("severe"))
        
        # Historical patterns - same hour previous days
        for days_back in [1, 7, 14, 28]:
            window_prev = Window.partitionBy("sensor_id", "hour") \
                .orderBy("timestamp") \
                .rowsBetween(-days_back * 288, -days_back * 288)  # 288 = 24h * 12 (5-min intervals)
            
            df = df.withColumn(f"speed_same_hour_{days_back}d_ago",
                              first(col("speed_kmh")).over(window_prev)) \
                   .withColumn(f"flow_same_hour_{days_back}d_ago",
                              first(col("vehicle_flow")).over(window_prev))
        
        # Monthly and day-of-week patterns
        df = df.withColumn("speed_monthly_avg",
                          avg(col("speed_kmh")).over(
                              Window.partitionBy("sensor_id", "month", "hour"))) \
               .withColumn("flow_monthly_avg",
                          avg(col("vehicle_flow")).over(
                              Window.partitionBy("sensor_id", "month", "hour"))) \
               .withColumn("speed_dow_avg",
                          avg(col("speed_kmh")).over(
                              Window.partitionBy("sensor_id", "day_of_week", "hour"))) \
               .withColumn("flow_dow_avg",
                          avg(col("vehicle_flow")).over(
                              Window.partitionBy("sensor_id", "day_of_week", "hour")))
        
        # Fill nulls
        df = df.na.fill(0)
        
        # Save processed data
        df.write \
            .mode("overwrite") \
            .partitionBy("sensor_id", "month") \
            .parquet(output_path)
        
        print(f"Processed data saved to {output_path}")
        
        return df
    
    def prepare_training_data(self, processed_data_path: str):
        """Prepare data for ML model training"""
        
        # Read processed data
        df = self.spark.read.parquet(processed_data_path)
        
        # Sample data for training (to manage memory)
        df = df.sample(fraction=0.1, seed=42)
        
        # Convert to Pandas for ML training
        pd_df = df.toPandas()
        
        # Sort by timestamp
        pd_df = pd_df.sort_values(['sensor_id', 'timestamp'])
        
        return pd_df
    
    def train_prediction_models(self, training_data: pd.DataFrame, model_save_path: str):
        """Train future prediction models"""
        
        print("Training future prediction models...")
        
        # Train the predictor
        self.predictor.train(
            df=training_data,
            target_col='speed_kmh'
        )
        
        # Save models
        self.predictor.save_models(model_save_path)
        
        print(f"Models saved to {model_save_path}")
    
    def generate_future_predictions(self, sensor_ids: list, hours_ahead: int = 24):
        """Generate batch predictions for multiple sensors"""
        
        current_time = datetime.now()
        predictions = []
        
        for sensor_id in sensor_ids:
            for hour in range(1, hours_ahead + 1):
                target_time = current_time + timedelta(hours=hour)
                
                prediction = self.predictor.predict_future(
                    road_id=sensor_id,
                    target_datetime=target_time,
                    current_datetime=current_time
                )
                
                predictions.append({
                    'sensor_id': sensor_id,
                    'prediction_time': current_time.isoformat(),
                    'target_time': target_time.isoformat(),
                    'hours_ahead': hour,
                    **prediction
                })
        
        # Convert to Spark DataFrame
        predictions_df = self.spark.createDataFrame(predictions)
        
        return predictions_df
    
    def calculate_route_metrics(self, routes_data_path: str):
        """Calculate metrics for route optimization"""
        
        # Read routes data
        routes_df = self.spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(routes_data_path)
        
        # Calculate average metrics by route and time
        metrics_df = routes_df.groupBy("route_id", "hour", "day_of_week") \
            .agg(
                avg("travel_time_minutes").alias("avg_travel_time"),
                avg("distance_km").alias("avg_distance"),
                avg("congestion_score").alias("avg_congestion"),
                count("*").alias("sample_count"),
                stddev("travel_time_minutes").alias("travel_time_std")
            )
        
        # Identify optimal times for each route
        window_spec = Window.partitionBy("route_id") \
            .orderBy("avg_travel_time")
        
        metrics_df = metrics_df.withColumn("time_rank",
                                          rank().over(window_spec)) \
            .withColumn("is_optimal_time",
                       when(col("time_rank") <= 5, 1).otherwise(0))
        
        return metrics_df
    
    def update_road_network(self, roads_data_path: str, output_path: str):
        """Update road network graph data for route recommendations"""
        
        # Read road network data
        roads_df = self.spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(roads_data_path)
        
        # Calculate road statistics
        road_stats = roads_df.groupBy("road_id") \
            .agg(
                avg("speed_limit").alias("speed_limit"),
                avg("lanes").alias("lanes"),
                avg("capacity").alias("capacity"),
                first("road_type").alias("road_type"),
                first("start_junction").alias("start_junction"),
                first("end_junction").alias("end_junction"),
                first("distance_km").alias("distance_km")
            )
        
        # Add coordinates if available
        if "start_lat" in roads_df.columns:
            road_stats = road_stats.join(
                roads_df.select("road_id", "start_lat", "start_lon", 
                              "end_lat", "end_lon").distinct(),
                on="road_id"
            )
        
        # Save updated network
        road_stats.write \
            .mode("overwrite") \
            .parquet(output_path)
        
        print(f"Road network saved to {output_path}")
        
        return road_stats
    
    def create_prediction_summary(self, predictions_df):
        """Create summary statistics for predictions"""
        
        summary = predictions_df.groupBy("sensor_id", "hours_ahead") \
            .agg(
                avg("predicted_speed_kmh").alias("avg_predicted_speed"),
                min("predicted_speed_kmh").alias("min_predicted_speed"),
                max("predicted_speed_kmh").alias("max_predicted_speed"),
                avg("confidence").alias("avg_confidence"),
                count("*").alias("prediction_count")
            )
        
        # Add congestion distribution
        congestion_dist = predictions_df.groupBy("sensor_id", "congestion_level") \
            .count() \
            .withColumnRenamed("count", "congestion_count")
        
        return summary, congestion_dist
    
    def close(self):
        """Close Spark session"""
        self.spark.stop()

if __name__ == "__main__":
    # Example usage
    processor = TrafficBatchProcessor()
    
    try:
        # Process historical data
        processed_df = processor.process_historical_data(
            input_path="/data/historical/traffic_data.csv",
            output_path="/data/processed/traffic_features"
        )
        
        # Prepare training data
        training_data = processor.prepare_training_data("/data/processed/traffic_features")
        
        # Train models
        processor.train_prediction_models(
            training_data=training_data,
            model_save_path="/models/saved"
        )
        
        # Generate predictions
        sensor_ids = ["sensor_001", "sensor_002", "sensor_003"]
        predictions_df = processor.generate_future_predictions(sensor_ids, hours_ahead=24)
        
        # Save predictions
        predictions_df.write \
            .mode("overwrite") \
            .json("/data/predictions/batch_predictions.json")
        
        # Create summary
        summary, congestion_dist = processor.create_prediction_summary(predictions_df)
        
        # Save summary
        summary.write.mode("overwrite").parquet("/data/predictions/summary")
        congestion_dist.write.mode("overwrite").parquet("/data/predictions/congestion_distribution")
        
        print("Batch processing completed successfully!")
        
    finally:
        processor.close()
