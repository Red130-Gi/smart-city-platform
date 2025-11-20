import json
import random
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaProducer
from faker import Faker
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
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.generation_interval = int(os.getenv('GENERATION_INTERVAL', '5'))
        self.pg_host = os.getenv('POSTGRES_HOST', 'postgres')
        self.pg_db = os.getenv('POSTGRES_DB', 'smart_city_db')
        self.pg_user = os.getenv('POSTGRES_USER', 'smart_city')
        self.pg_password = os.getenv('POSTGRES_PASSWORD', 'smartcity123')
        self.pg_port = int(os.getenv('POSTGRES_PORT', '5432'))
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: json.dumps(v).encode('utf-8') if v else None
        )
        
        # Initialize PostgreSQL connection and schema (for Grafana dashboards)
        self.pg_conn = psycopg2.connect(
            host=self.pg_host,
            dbname=self.pg_db,
            user=self.pg_user,
            password=self.pg_password,
            port=self.pg_port,
        )
        self.pg_conn.autocommit = False
        self._ensure_postgres_schema()
        
        # Initialize data generators
        self.traffic_gen = TrafficGenerator()
        self.transport_gen = PublicTransportGenerator()
        self.taxi_gen = TaxiGenerator()
        self.parking_gen = ParkingGenerator()
        self.bike_gen = BikeShareGenerator()
        self.incident_gen = IncidentGenerator()
        self.weather_gen = WeatherGenerator()
        self.pollution_gen = PollutionGenerator()
        
        print(f"Smart City Data Generator initialized")
        print(f"Kafka servers: {self.kafka_servers}")
        print(f"Generation interval: {self.generation_interval} seconds")
    
    def _ensure_postgres_schema(self):
        with self.pg_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS traffic_sensors (
                    id SERIAL PRIMARY KEY,
                    sensor_id TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    road_id TEXT,
                    road_name TEXT,
                    zone_id TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    speed_kmh DOUBLE PRECISION,
                    vehicle_flow INTEGER,
                    occupancy_percent DOUBLE PRECISION,
                    congestion_level TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_sensors_ts ON traffic_sensors (timestamp);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_sensors_zone ON traffic_sensors (zone_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_sensors_road ON traffic_sensors (road_name);")

            # Mobility tables
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS bus_positions (
                    id SERIAL PRIMARY KEY,
                    vehicle_id TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    line_id TEXT,
                    line_number TEXT,
                    current_stop INTEGER,
                    next_stop INTEGER,
                    direction TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    speed_kmh DOUBLE PRECISION,
                    passenger_count INTEGER,
                    capacity INTEGER,
                    occupancy_rate DOUBLE PRECISION,
                    delay_minutes DOUBLE PRECISION,
                    status TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_bus_positions_ts ON bus_positions (timestamp);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_bus_positions_line ON bus_positions (line_number);")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS bike_stations (
                    id SERIAL PRIMARY KEY,
                    station_id TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    station_name TEXT,
                    zone_id TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    capacity INTEGER,
                    available_bikes INTEGER,
                    available_docks INTEGER,
                    status TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_bike_stations_ts ON bike_stations (timestamp);")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS parking_lots (
                    id SERIAL PRIMARY KEY,
                    parking_id TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    name TEXT,
                    zone_id TEXT,
                    type TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    total_spaces INTEGER,
                    occupied_spaces INTEGER,
                    available_spaces INTEGER,
                    occupancy_rate DOUBLE PRECISION,
                    hourly_rate DOUBLE PRECISION,
                    status TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_parking_lots_ts ON parking_lots (timestamp);")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS taxis (
                    id SERIAL PRIMARY KEY,
                    taxi_id TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    type TEXT,
                    status TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    current_zone TEXT,
                    speed_kmh DOUBLE PRECISION,
                    battery_level INTEGER
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_taxis_ts ON taxis (timestamp);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_taxis_status ON taxis (status);")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS trips (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    date DATE NOT NULL,
                    mode TEXT NOT NULL,
                    origin_zone TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_date ON trips (date);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trips_ts ON trips (timestamp);")

            # Extend trips with alias column expected by overview dashboard
            cur.execute("ALTER TABLE trips ADD COLUMN IF NOT EXISTS transport_mode TEXT;")

            # Incidents table (for overview dashboard)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id SERIAL PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    type TEXT,
                    severity TEXT,
                    road_id TEXT,
                    road_name TEXT,
                    zone_id TEXT,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    description TEXT,
                    estimated_duration_min INTEGER,
                    affected_lanes INTEGER,
                    status TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents (created_at);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents (status);")

            # Air quality table (for overview dashboard)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS air_quality (
                    id SERIAL PRIMARY KEY,
                    station_id TEXT,
                    timestamp TIMESTAMPTZ NOT NULL,
                    zone_id TEXT,
                    zone_name TEXT,
                    aqi INTEGER
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_air_quality_ts ON air_quality (timestamp);")

            # Views expected by overview dashboard
            cur.execute(
                """
                CREATE OR REPLACE VIEW parking_status AS
                SELECT timestamp, occupancy_rate FROM parking_lots;
                """
            )
            cur.execute(
                """
                CREATE OR REPLACE VIEW vehicle_positions AS
                SELECT
                  vehicle_id,
                  timestamp,
                  CASE WHEN status IN ('on_time','delayed') THEN 'active' ELSE 'inactive' END AS status
                FROM bus_positions;
                """
            )
            cur.execute(
                """
                CREATE OR REPLACE VIEW public_transport_stats AS
                SELECT
                  (timestamp::date) AS date,
                  line_number,
                  AVG(CASE WHEN ABS(delay_minutes) < 3 THEN 1.0 ELSE 0.0 END) AS punctuality_rate
                FROM bus_positions
                GROUP BY date, line_number;
                """
            )

            # Traffic predictions table for Grafana 'Prédictions vs Réel'
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
        self.pg_conn.commit()

    def _insert_traffic_rows(self, traffic_data: List[Dict[str, Any]]):
        if not traffic_data:
            return
        rows = [
            (
                d.get('sensor_id'),
                datetime.fromisoformat(d.get('timestamp')),
                d.get('road_id'),
                d.get('road_name'),
                d.get('zone_id'),
                (d.get('location') or {}).get('lat'),
                (d.get('location') or {}).get('lon'),
                d.get('speed_kmh'),
                d.get('vehicle_flow'),
                d.get('occupancy_percent'),
                d.get('congestion_level'),
            )
            for d in traffic_data
        ]
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO traffic_sensors (
                    sensor_id, timestamp, road_id, road_name, zone_id, lat, lon,
                    speed_kmh, vehicle_flow, occupancy_percent, congestion_level
                ) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_bus_positions(self, bus_data: List[Dict[str, Any]]):
        if not bus_data:
            return
        rows = [
            (
                d.get('vehicle_id'),
                datetime.fromisoformat(d.get('timestamp')),
                d.get('line_id'),
                d.get('line_number'),
                d.get('current_stop'),
                d.get('next_stop'),
                d.get('direction'),
                (d.get('location') or {}).get('lat'),
                (d.get('location') or {}).get('lon'),
                d.get('speed_kmh'),
                d.get('passenger_count'),
                d.get('capacity'),
                d.get('occupancy_rate'),
                d.get('delay_minutes'),
                d.get('status'),
            )
            for d in bus_data
        ]
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO bus_positions (
                    vehicle_id, timestamp, line_id, line_number, current_stop, next_stop,
                    direction, lat, lon, speed_kmh, passenger_count, capacity,
                    occupancy_rate, delay_minutes, status
                ) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_bike_stations(self, bike_data: List[Dict[str, Any]]):
        if not bike_data:
            return
        rows = [
            (
                d.get('station_id'),
                datetime.fromisoformat(d.get('timestamp')),
                d.get('name'),
                d.get('zone_id'),
                (d.get('location') or {}).get('lat'),
                (d.get('location') or {}).get('lon'),
                d.get('capacity'),
                d.get('available_bikes'),
                d.get('available_docks'),
                d.get('status'),
            )
            for d in bike_data
        ]
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO bike_stations (
                    station_id, timestamp, station_name, zone_id, lat, lon,
                    capacity, available_bikes, available_docks, status
                ) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_parking_lots(self, parking_data: List[Dict[str, Any]]):
        if not parking_data:
            return
        rows = [
            (
                d.get('parking_id'),
                datetime.fromisoformat(d.get('timestamp')),
                d.get('name'),
                d.get('zone_id'),
                d.get('type'),
                (d.get('location') or {}).get('lat'),
                (d.get('location') or {}).get('lon'),
                d.get('total_spaces'),
                d.get('occupied_spaces'),
                d.get('available_spaces'),
                (d.get('occupancy_rate') / 100.0) if d.get('occupancy_rate') is not None else None,
                d.get('hourly_rate'),
                d.get('status'),
            )
            for d in parking_data
        ]
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO parking_lots (
                    parking_id, timestamp, name, zone_id, type, lat, lon,
                    total_spaces, occupied_spaces, available_spaces, occupancy_rate,
                    hourly_rate, status
                ) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_taxis(self, taxi_data: List[Dict[str, Any]]):
        if not taxi_data:
            return
        rows = [
            (
                d.get('taxi_id'),
                datetime.fromisoformat(d.get('timestamp')),
                d.get('type'),
                d.get('status'),
                (d.get('location') or {}).get('lat'),
                (d.get('location') or {}).get('lon'),
                d.get('current_zone'),
                d.get('speed_kmh'),
                d.get('battery_level') if d.get('battery_level') is not None else None,
            )
            for d in taxi_data
        ]
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO taxis (
                    taxi_id, timestamp, type, status, lat, lon, current_zone, speed_kmh, battery_level
                ) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_trips(self, taxi_data: List[Dict[str, Any]], bike_data: List[Dict[str, Any]], bus_data: List[Dict[str, Any]]):
        rows = []
        # Taxi trips: one per occupied taxi event
        for d in taxi_data:
            if d.get('status') == 'occupied':
                ts = datetime.fromisoformat(d.get('timestamp'))
                rows.append((ts, ts.date(), 'taxi', d.get('current_zone'), 'taxi'))
        # Bike trips: small probability per station snapshot
        for d in bike_data:
            if random.random() < 0.05:
                ts = datetime.fromisoformat(d.get('timestamp'))
                rows.append((ts, ts.date(), 'bike', d.get('zone_id'), 'bike'))
        # Bus trips: small random sample with random zone
        if bus_data:
            sample_size = min(10, max(1, len(bus_data) // 10))
            for _ in range(sample_size):
                ts = datetime.now()
                zone = random.choice(CITY_ZONES)['id'] if CITY_ZONES else None
                rows.append((ts, ts.date(), 'bus', zone, 'bus'))
        if not rows:
            return
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO trips (timestamp, date, mode, origin_zone, transport_mode) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def _insert_incidents(self, incident: Dict[str, Any]):
        if not incident:
            return
        d = incident
        ts = datetime.fromisoformat(d.get('timestamp'))
        loc = d.get('location') or {}
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO incidents (
                  incident_id, created_at, type, severity, road_id, road_name, zone_id, lat, lon,
                  description, estimated_duration_min, affected_lanes, status
                ) VALUES %s
                """,
                [(
                    d.get('incident_id'), ts, d.get('type'), d.get('severity'),
                    loc.get('road_id'), loc.get('road_name'), loc.get('zone_id'),
                    loc.get('lat'), loc.get('lon'), d.get('description'),
                    d.get('estimated_duration_min'), d.get('affected_lanes'), d.get('status')
                )],
            )
        self.pg_conn.commit()

    def _insert_air_quality(self, pollution_data: List[Dict[str, Any]]):
        if not pollution_data:
            return
        rows = []
        for d in pollution_data:
            ts = datetime.fromisoformat(d.get('timestamp'))
            rows.append((
                d.get('station_id'), ts, d.get('zone_id'), d.get('zone_name'), int(d.get('aqi')) if d.get('aqi') is not None else None
            ))
        with self.pg_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO air_quality (station_id, timestamp, zone_id, zone_name, aqi) VALUES %s
                """,
                rows,
            )
        self.pg_conn.commit()

    def generate_and_send_data(self):
        """Generate and send all types of urban data"""
        timestamp = datetime.now()
        
        # Generate traffic data
        traffic_data = self.traffic_gen.generate_traffic_data(timestamp)
        for data in traffic_data:
            self.producer.send('traffic-sensors', value=data, key=data.get('sensor_id'))
        # Persist to PostgreSQL for Grafana panels
        try:
            self._insert_traffic_rows(traffic_data)
        except Exception as e:
            print(f"PostgreSQL insert error: {e}")
        
        # Generate public transport data
        bus_data = self.transport_gen.generate_bus_data(timestamp)
        for data in bus_data:
            self.producer.send('public-transport', value=data, key=data.get('vehicle_id'))
        try:
            self._insert_bus_positions(bus_data)
        except Exception as e:
            print(f"PostgreSQL insert error (bus_positions): {e}")
        
        # Generate taxi/VTC data
        taxi_data = self.taxi_gen.generate_taxi_data(timestamp)
        for data in taxi_data:
            self.producer.send('taxi-vtc', value=data, key=data.get('taxi_id'))
        try:
            self._insert_taxis(taxi_data)
        except Exception as e:
            print(f"PostgreSQL insert error (taxis): {e}")
        
        # Generate parking data
        parking_data = self.parking_gen.generate_parking_data(timestamp)
        for data in parking_data:
            self.producer.send('parking', value=data, key=data.get('parking_id'))
        try:
            self._insert_parking_lots(parking_data)
        except Exception as e:
            print(f"PostgreSQL insert error (parking_lots): {e}")
        
        # Generate bike share data
        bike_data = self.bike_gen.generate_bike_data(timestamp)
        for data in bike_data:
            self.producer.send('bike-share', value=data, key=data.get('station_id'))
        try:
            self._insert_bike_stations(bike_data)
        except Exception as e:
            print(f"PostgreSQL insert error (bike_stations): {e}")

        # Trips derived from taxi/bike/bus snapshots
        try:
            self._insert_trips(taxi_data, bike_data, bus_data)
        except Exception as e:
            print(f"PostgreSQL insert error (trips): {e}")
        
        # Generate incident data (less frequent)
        if random.random() < 0.1:  # 10% chance per cycle
            incident_data = self.incident_gen.generate_incident(timestamp)
            if incident_data:
                self.producer.send('incidents', value=incident_data, key=incident_data.get('incident_id'))
                try:
                    self._insert_incidents(incident_data)
                except Exception as e:
                    print(f"PostgreSQL insert error (incidents): {e}")
        
        # Generate weather data
        weather_data = self.weather_gen.generate_weather_data(timestamp)
        self.producer.send('weather', value=weather_data, key='city-center')
        
        # Generate pollution data
        pollution_data = self.pollution_gen.generate_pollution_data(timestamp)
        for data in pollution_data:
            self.producer.send('air-quality', value=data, key=data.get('station_id'))
        try:
            self._insert_air_quality(pollution_data)
        except Exception as e:
            print(f"PostgreSQL insert error (air_quality): {e}")
        
        # Flush producer
        self.producer.flush()
        
        # Log statistics
        total_messages = (
            len(traffic_data) + 
            len(bus_data) + 
            len(taxi_data) + 
            len(parking_data) + 
            len(bike_data) + 
            1 +  # weather
            len(pollution_data)
        )
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Generated {total_messages} messages")
    
    def run(self):
        """Main execution loop"""
        print("Starting continuous data generation...")
        
        while True:
            try:
                self.generate_and_send_data()
                time.sleep(self.generation_interval)
            except KeyboardInterrupt:
                print("Stopping data generation...")
                break
            except Exception as e:
                print(f"Error generating data: {e}")
                time.sleep(self.generation_interval)
        
        self.producer.close()
        try:
            self.pg_conn.close()
        except Exception:
            pass
        print("Data generation stopped.")

if __name__ == "__main__":
    generator = SmartCityDataGenerator()
    generator.run()
