from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, window, avg, count, max, min, 
    stddev, when, current_timestamp, to_timestamp,
    expr, udf, lit, sum as spark_sum
)
from pyspark.sql.types import *
import os
import json

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:smartcity123@localhost:27017")
CHECKPOINT_LOCATION = "/tmp/spark-checkpoints"

# Define schemas for different data types
traffic_schema = StructType([
    StructField("sensor_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("road_id", StringType(), True),
    StructField("road_name", StringType(), True),
    StructField("zone_id", StringType(), True),
    StructField("location", StructType([
        StructField("lat", DoubleType(), True),
        StructField("lon", DoubleType(), True)
    ]), True),
    StructField("speed_kmh", DoubleType(), True),
    StructField("vehicle_flow", IntegerType(), True),
    StructField("occupancy_percent", DoubleType(), True),
    StructField("congestion_level", StringType(), True),
    StructField("data_quality", StringType(), True)
])

transport_schema = StructType([
    StructField("vehicle_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("line_id", StringType(), True),
    StructField("line_number", StringType(), True),
    StructField("location", StructType([
        StructField("lat", DoubleType(), True),
        StructField("lon", DoubleType(), True)
    ]), True),
    StructField("speed_kmh", DoubleType(), True),
    StructField("passenger_count", IntegerType(), True),
    StructField("capacity", IntegerType(), True),
    StructField("occupancy_rate", DoubleType(), True),
    StructField("delay_minutes", DoubleType(), True),
    StructField("status", StringType(), True)
])

incident_schema = StructType([
    StructField("incident_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("type", StringType(), True),
    StructField("severity", StringType(), True),
    StructField("location", StructType([
        StructField("road_id", StringType(), True),
        StructField("road_name", StringType(), True),
        StructField("zone_id", StringType(), True),
        StructField("lat", DoubleType(), True),
        StructField("lon", DoubleType(), True)
    ]), True),
    StructField("description", StringType(), True),
    StructField("estimated_duration_min", IntegerType(), True),
    StructField("status", StringType(), True)
])

class SmartCityStreamProcessor:
    def __init__(self):
        """Initialize Spark session and configurations"""
        self.spark = SparkSession.builder \
            .appName("SmartCityStreamProcessor") \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
                   "org.mongodb.spark:mongo-spark-connector_2.12:10.2.0") \
            .config("spark.mongodb.write.connection.uri", MONGODB_URI) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print("Spark session initialized")
    
    def process_traffic_stream(self):
        """Process real-time traffic data stream"""
        # Read from Kafka
        traffic_stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", "traffic-sensors") \
            .option("startingOffsets", "latest") \
            .load()
        
        # Parse JSON data
        traffic_df = traffic_stream \
            .select(from_json(col("value").cast("string"), traffic_schema).alias("data")) \
            .select("data.*") \
            .withColumn("timestamp", to_timestamp(col("timestamp")))
        
        # Calculate windowed aggregations (5-minute windows)
        traffic_aggregations = traffic_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(
                window(col("timestamp"), "5 minutes", "1 minute"),
                col("zone_id"),
                col("road_id")
            ) \
            .agg(
                avg("speed_kmh").alias("avg_speed"),
                spark_sum("vehicle_flow").alias("total_vehicles"),
                avg("occupancy_percent").alias("avg_occupancy"),
                count("*").alias("sensor_readings"),
                min("speed_kmh").alias("min_speed"),
                max("speed_kmh").alias("max_speed")
            ) \
            .withColumn("congestion_score", 
                       when(col("avg_speed") < 20, 1.0)
                       .when(col("avg_speed") < 35, 0.7)
                       .when(col("avg_speed") < 50, 0.4)
                       .otherwise(0.1))
        
        # Detect anomalies
        anomaly_detection = traffic_df \
            .filter(
                (col("speed_kmh") < 5) | 
                (col("occupancy_percent") > 95) |
                (col("data_quality") != "good")
            ) \
            .withColumn("anomaly_type", 
                       when(col("speed_kmh") < 5, "severe_congestion")
                       .when(col("occupancy_percent") > 95, "overcapacity")
                       .otherwise("data_quality_issue"))
        
        # Write aggregations to console (for debugging)
        query_console = traffic_aggregations \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="30 seconds") \
            .start()
        
        # Write to MongoDB for persistence
        def write_to_mongodb(df, epoch_id):
            df.write \
                .format("mongodb") \
                .mode("append") \
                .option("database", "smart_city") \
                .option("collection", "traffic_aggregations") \
                .save()
        
        query_mongodb = traffic_aggregations \
            .writeStream \
            .outputMode("update") \
            .foreachBatch(write_to_mongodb) \
            .option("checkpointLocation", f"{CHECKPOINT_LOCATION}/traffic") \
            .trigger(processingTime="1 minute") \
            .start()
        
        # Write anomalies to separate stream
        query_anomalies = anomaly_detection \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="10 seconds") \
            .start()
        
        return [query_console, query_mongodb, query_anomalies]
    
    def process_transport_stream(self):
        """Process public transport data stream"""
        transport_stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", "public-transport") \
            .option("startingOffsets", "latest") \
            .load()
        
        transport_df = transport_stream \
            .select(from_json(col("value").cast("string"), transport_schema).alias("data")) \
            .select("data.*") \
            .withColumn("timestamp", to_timestamp(col("timestamp")))
        
        # Calculate line performance metrics
        line_performance = transport_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(
                window(col("timestamp"), "10 minutes", "5 minutes"),
                col("line_id"),
                col("line_number")
            ) \
            .agg(
                avg("delay_minutes").alias("avg_delay"),
                avg("occupancy_rate").alias("avg_occupancy"),
                count("*").alias("vehicle_count"),
                spark_sum("passenger_count").alias("total_passengers")
            ) \
            .withColumn("punctuality_score",
                       when(col("avg_delay") < 2, 1.0)
                       .when(col("avg_delay") < 5, 0.7)
                       .otherwise(0.3))
        
        # Detect overcrowded vehicles
        overcrowded = transport_df \
            .filter(col("occupancy_rate") > 90) \
            .select(
                col("vehicle_id"),
                col("line_id"),
                col("timestamp"),
                col("occupancy_rate"),
                col("location")
            )
        
        # Write line performance
        query_performance = line_performance \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="1 minute") \
            .start()
        
        return [query_performance]
    
    def process_incidents_stream(self):
        """Process incident reports stream"""
        incidents_stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", "incidents") \
            .option("startingOffsets", "latest") \
            .load()
        
        incidents_df = incidents_stream \
            .select(from_json(col("value").cast("string"), incident_schema).alias("data")) \
            .select("data.*") \
            .withColumn("timestamp", to_timestamp(col("timestamp")))
        
        # Count incidents by zone and severity
        incident_stats = incidents_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(
                window(col("timestamp"), "15 minutes", "5 minutes"),
                col("location.zone_id"),
                col("severity")
            ) \
            .count() \
            .withColumn("alert_level",
                       when((col("severity") == "critical") & (col("count") > 0), "red")
                       .when((col("severity") == "high") & (col("count") > 2), "orange")
                       .otherwise("yellow"))
        
        # Critical incidents for immediate alerts
        critical_incidents = incidents_df \
            .filter(col("severity").isin(["critical", "high"])) \
            .select(
                col("incident_id"),
                col("type"),
                col("severity"),
                col("location"),
                col("description"),
                col("timestamp")
            )
        
        # Write incident statistics
        query_stats = incident_stats \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="30 seconds") \
            .start()
        
        return [query_stats]
    
    def calculate_mobility_index(self):
        """Calculate real-time mobility index for the city"""
        # Join multiple streams for comprehensive mobility index
        # This would combine traffic, transport, and incident data
        # For demonstration, using traffic data
        
        traffic_stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", "traffic-sensors") \
            .option("startingOffsets", "latest") \
            .load()
        
        traffic_df = traffic_stream \
            .select(from_json(col("value").cast("string"), traffic_schema).alias("data")) \
            .select("data.*") \
            .withColumn("timestamp", to_timestamp(col("timestamp")))
        
        # Calculate city-wide mobility index
        mobility_index = traffic_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(window(col("timestamp"), "5 minutes")) \
            .agg(
                avg("speed_kmh").alias("city_avg_speed"),
                avg("occupancy_percent").alias("city_avg_occupancy"),
                count("*").alias("total_readings")
            ) \
            .withColumn("mobility_index",
                       (col("city_avg_speed") / 50 * 0.6 +  # Speed component
                        (100 - col("city_avg_occupancy")) / 100 * 0.4) * 100)  # Occupancy component
            .withColumn("index_category",
                       when(col("mobility_index") > 80, "excellent")
                       .when(col("mobility_index") > 60, "good")
                       .when(col("mobility_index") > 40, "moderate")
                       .when(col("mobility_index") > 20, "poor")
                       .otherwise("critical"))
        
        query_index = mobility_index \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="1 minute") \
            .start()
        
        return query_index
    
    def run(self):
        """Run all stream processing pipelines"""
        print("Starting Smart City Stream Processing...")
        
        try:
            # Start all processing pipelines
            traffic_queries = self.process_traffic_stream()
            transport_queries = self.process_transport_stream()
            incident_queries = self.process_incidents_stream()
            mobility_query = self.calculate_mobility_index()
            
            # Combine all queries
            all_queries = traffic_queries + transport_queries + incident_queries + [mobility_query]
            
            print(f"Started {len(all_queries)} streaming queries")
            
            # Wait for all streams to finish
            for query in all_queries:
                if query:
                    query.awaitTermination()
            
        except KeyboardInterrupt:
            print("Stopping stream processing...")
            self.spark.stop()
        except Exception as e:
            print(f"Error in stream processing: {e}")
            self.spark.stop()

if __name__ == "__main__":
    processor = SmartCityStreamProcessor()
    processor.run()
