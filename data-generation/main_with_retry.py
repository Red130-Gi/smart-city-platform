#!/usr/bin/env python3
"""
Smart City Data Generator with Kafka retry logic
Generates simulated IoT data for the Smart City platform
"""

import os
import sys
import json
import time
import psycopg2
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from data_generators import (
    TrafficGenerator,
    PublicTransportGenerator,
    TaxiGenerator,
    ParkingGenerator,
    BikeShareGenerator,
    IncidentGenerator,
    WeatherGenerator,
    PollutionGenerator,
    CITY_ZONES
)

class SmartCityDataGenerator:
    def __init__(self, max_retries=10, retry_delay=5):
        """Initialize with retry logic for Kafka connection"""
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093')
        self.generation_interval = int(os.getenv('GENERATION_INTERVAL', '5'))
        self.pg_host = os.getenv('POSTGRES_HOST', 'postgres')
        self.pg_db = os.getenv('POSTGRES_DB', 'smart_city_db')
        self.pg_user = os.getenv('POSTGRES_USER', 'smart_city')
        self.pg_password = os.getenv('POSTGRES_PASSWORD', 'smartcity123')
        self.pg_port = int(os.getenv('POSTGRES_PORT', '5432'))
        
        # Initialize Kafka producer with retry logic
        print(f"Connecting to Kafka at {self.kafka_servers}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Connection attempt {attempt}/{max_retries}...")
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda v: json.dumps(v).encode('utf-8') if v else None,
                    max_block_ms=3000  # Timeout de 3 secondes
                )
                print("✅ Successfully connected to Kafka!")
                break
            except NoBrokersAvailable:
                if attempt == max_retries:
                    print(f"❌ Failed to connect to Kafka after {max_retries} attempts")
                    raise
                print(f"⚠️ Kafka not available, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        # Initialize PostgreSQL connection with retry
        print(f"Connecting to PostgreSQL at {self.pg_host}:{self.pg_port}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"PostgreSQL connection attempt {attempt}/{max_retries}...")
                self.pg_conn = psycopg2.connect(
                    host=self.pg_host,
                    dbname=self.pg_db,
                    user=self.pg_user,
                    password=self.pg_password,
                    port=self.pg_port,
                )
                self.pg_conn.autocommit = False
                print("✅ Successfully connected to PostgreSQL!")
                break
            except psycopg2.OperationalError as e:
                if attempt == max_retries:
                    print(f"❌ Failed to connect to PostgreSQL after {max_retries} attempts")
                    raise
                print(f"⚠️ PostgreSQL not available: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        self.init_pg_tables()
        
        # Initialize all generators
        self.traffic_gen = TrafficGenerator()
        self.transport_gen = PublicTransportGenerator()
        self.taxi_gen = TaxiGenerator()
        self.parking_gen = ParkingGenerator()
        self.bike_gen = BikeShareGenerator()
        self.incident_gen = IncidentGenerator()
        self.weather_gen = WeatherGenerator()
        self.pollution_gen = PollutionGenerator()
        
        print("✅ All generators initialized successfully!")
    
    def init_pg_tables(self):
        """Create PostgreSQL tables if they don't exist"""
        cursor = self.pg_conn.cursor()
        
        tables = [
            """
            CREATE TABLE IF NOT EXISTS traffic_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sensor_id VARCHAR(50),
                road_id VARCHAR(50),
                road_name VARCHAR(100),
                zone_id VARCHAR(50),
                lat DECIMAL(10, 6),
                lon DECIMAL(10, 6),
                speed_kmh DECIMAL(5, 1),
                vehicle_flow INTEGER,
                occupancy_percent DECIMAL(5, 1),
                congestion_level VARCHAR(20),
                data_quality VARCHAR(20)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS public_transport (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                vehicle_id VARCHAR(50),
                line_id VARCHAR(50),
                line_number VARCHAR(20),
                current_stop INTEGER,
                next_stop INTEGER,
                direction VARCHAR(20),
                lat DECIMAL(10, 6),
                lon DECIMAL(10, 6),
                speed_kmh DECIMAL(5, 1),
                passenger_count INTEGER,
                capacity INTEGER,
                occupancy_rate DECIMAL(5, 1),
                delay_minutes DECIMAL(5, 1),
                status VARCHAR(20)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS parking_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                parking_id VARCHAR(50),
                name VARCHAR(100),
                zone_id VARCHAR(50),
                type VARCHAR(20),
                lat DECIMAL(10, 6),
                lon DECIMAL(10, 6),
                total_spaces INTEGER,
                occupied_spaces INTEGER,
                available_spaces INTEGER,
                occupancy_rate DECIMAL(5, 1),
                hourly_rate DECIMAL(5, 2),
                status VARCHAR(20)
            )
            """
        ]
        
        for table in tables:
            try:
                cursor.execute(table)
            except psycopg2.Error as e:
                print(f"Warning: Error creating table: {e}")
                self.pg_conn.rollback()
            else:
                self.pg_conn.commit()
        
        cursor.close()
    
    def send_to_kafka(self, topic: str, data: Any, key: str = None):
        """Send data to Kafka topic with error handling"""
        try:
            future = self.producer.send(topic, key=key, value=data)
            # Wait for confirmation (optional)
            # future.get(timeout=10)
        except Exception as e:
            print(f"Error sending to Kafka topic {topic}: {e}")
    
    def store_in_postgres(self, table: str, data: Dict):
        """Store data in PostgreSQL with error handling"""
        cursor = self.pg_conn.cursor()
        
        try:
            if table == 'traffic_data':
                cursor.execute("""
                    INSERT INTO traffic_data 
                    (timestamp, sensor_id, road_id, road_name, zone_id, lat, lon,
                     speed_kmh, vehicle_flow, occupancy_percent, congestion_level, data_quality)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['timestamp'], data['sensor_id'], data['road_id'],
                    data['road_name'], data['zone_id'], 
                    data['location']['lat'], data['location']['lon'],
                    data['speed_kmh'], data['vehicle_flow'], data['occupancy_percent'],
                    data['congestion_level'], data['data_quality']
                ))
            elif table == 'public_transport':
                cursor.execute("""
                    INSERT INTO public_transport
                    (timestamp, vehicle_id, line_id, line_number, current_stop, next_stop,
                     direction, lat, lon, speed_kmh, passenger_count, capacity,
                     occupancy_rate, delay_minutes, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['timestamp'], data['vehicle_id'], data['line_id'],
                    data['line_number'], data['current_stop'], data['next_stop'],
                    data['direction'], data['location']['lat'], data['location']['lon'],
                    data['speed_kmh'], data['passenger_count'], data['capacity'],
                    data['occupancy_rate'], data['delay_minutes'], data['status']
                ))
            elif table == 'parking_data':
                cursor.execute("""
                    INSERT INTO parking_data
                    (timestamp, parking_id, name, zone_id, type, lat, lon,
                     total_spaces, occupied_spaces, available_spaces,
                     occupancy_rate, hourly_rate, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['timestamp'], data['parking_id'], data['name'],
                    data['zone_id'], data['type'],
                    data['location']['lat'], data['location']['lon'],
                    data['total_spaces'], data['occupied_spaces'], data['available_spaces'],
                    data['occupancy_rate'], data['hourly_rate'], data['status']
                ))
            elif table == 'taxis':
                cursor.execute("""
                    INSERT INTO taxis
                    (timestamp, taxi_id, type, status, lat, lon, current_zone, speed_kmh, battery_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['timestamp'], data['taxi_id'], data['type'], data['status'],
                    data['location']['lat'], data['location']['lon'],
                    data['current_zone'], data.get('speed_kmh', 0), data.get('battery_level')
                ))
            
            self.pg_conn.commit()
        except psycopg2.Error as e:
            print(f"Error storing in PostgreSQL table {table}: {e}")
            self.pg_conn.rollback()
        finally:
            cursor.close()
    
    def run(self):
        """Main loop to generate and send data"""
        print(f"Starting data generation every {self.generation_interval} seconds...")
        print("Press Ctrl+C to stop")
        
        iteration = 0
        while True:
            try:
                timestamp = datetime.now()
                iteration += 1
                
                print(f"\n--- Iteration {iteration} at {timestamp.isoformat()} ---")
                
                # Generate and send traffic data
                traffic_data = self.traffic_gen.generate_traffic_data(timestamp)
                for data in traffic_data:
                    self.send_to_kafka('traffic-sensors', data, key=data['sensor_id'])
                    self.store_in_postgres('traffic_data', data)
                print(f"✓ Sent {len(traffic_data)} traffic records")
                
                # Generate and send public transport data
                transport_data = self.transport_gen.generate_bus_data(timestamp)
                for data in transport_data:
                    self.send_to_kafka('public-transport', data, key=data['vehicle_id'])
                    self.store_in_postgres('public_transport', data)
                print(f"✓ Sent {len(transport_data)} public transport records")
                
                # Generate and send taxi data
                taxi_data = self.taxi_gen.generate_taxi_data(timestamp)
                for data in taxi_data:
                    self.send_to_kafka('taxi-vtc', data, key=data['taxi_id'])
                    self.store_in_postgres('taxis', data)
                print(f"✓ Sent {len(taxi_data)} taxi records")
                
                # Generate and send parking data
                parking_data = self.parking_gen.generate_parking_data(timestamp)
                for data in parking_data:
                    self.send_to_kafka('parking', data, key=data['parking_id'])
                    self.store_in_postgres('parking_data', data)
                print(f"✓ Sent {len(parking_data)} parking records")
                
                # Generate and send bike share data
                bike_data = self.bike_gen.generate_bike_data(timestamp)
                for data in bike_data:
                    self.send_to_kafka('bike-share', data, key=data['station_id'])
                print(f"✓ Sent {len(bike_data)} bike share records")
                
                # Generate and send incident data (not every iteration)
                if iteration % 6 == 0:  # Every 30 seconds
                    incident = self.incident_gen.generate_incident(timestamp)
                    if incident:
                        self.send_to_kafka('incidents', incident, key=incident['incident_id'])
                        print(f"✓ Sent 1 incident report")
                
                # Generate and send weather data
                weather_data = self.weather_gen.generate_weather_data(timestamp)
                self.send_to_kafka('weather', weather_data)
                print(f"✓ Sent weather update")
                
                # Generate and send air quality data
                pollution_data = self.pollution_gen.generate_pollution_data(timestamp)
                for data in pollution_data:
                    self.send_to_kafka('air-quality', data, key=data['station_id'])
                print(f"✓ Sent {len(pollution_data)} air quality records")
                
                # Flush Kafka producer
                self.producer.flush()
                
                # Sleep until next iteration
                time.sleep(self.generation_interval)
                
            except KeyboardInterrupt:
                print("\nStopping data generation...")
                break
            except Exception as e:
                print(f"Error in generation loop: {e}")
                time.sleep(self.generation_interval)
        
        # Clean up
        self.cleanup()
    
    def cleanup(self):
        """Clean up connections"""
        print("Cleaning up connections...")
        try:
            self.producer.close()
            print("✓ Kafka producer closed")
        except:
            pass
        
        try:
            self.pg_conn.close()
            print("✓ PostgreSQL connection closed")
        except:
            pass

if __name__ == "__main__":
    print("="*60)
    print("SMART CITY DATA GENERATOR")
    print("="*60)
    
    # Configuration from environment
    print("\nConfiguration:")
    print(f"  Kafka: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093')}")
    print(f"  PostgreSQL: {os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}")
    print(f"  Generation interval: {os.getenv('GENERATION_INTERVAL', '5')} seconds")
    print("")
    
    try:
        generator = SmartCityDataGenerator(max_retries=20, retry_delay=3)
        generator.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
