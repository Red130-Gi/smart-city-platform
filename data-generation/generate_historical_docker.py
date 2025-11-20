#!/usr/bin/env python3
"""
Version simplifiée pour exécution dans Docker
Génère automatiquement 6 mois de données sans prompts
"""
import os
import sys
import psycopg2
from datetime import datetime, timedelta
import random
from data_generators import (
    TrafficGenerator,
    PublicTransportGenerator,
    ParkingGenerator,
)

def generate_historical_data():
    """Génère 6 mois de données historiques"""
    
    # Configuration
    months = 6
    interval_minutes = 5
    
    # Connexion PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        dbname=os.getenv('POSTGRES_DB', 'smart_city_db'),
        user=os.getenv('POSTGRES_USER', 'smart_city'),
        password=os.getenv('POSTGRES_PASSWORD', 'smartcity123'),
        port=int(os.getenv('POSTGRES_PORT', '5432'))
    )
    conn.autocommit = False
    
    # Générateurs
    traffic_gen = TrafficGenerator()
    transport_gen = PublicTransportGenerator()
    parking_gen = ParkingGenerator()
    
    # Période
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30 * months)
    total_iterations = int((end_time - start_time).total_seconds() / (interval_minutes * 60))
    
    print("="*70)
    print(f"GÉNÉRATION DE {months} MOIS DE DONNÉES HISTORIQUES")
    print("="*70)
    print(f"Période : {start_time.strftime('%Y-%m-%d')} → {end_time.strftime('%Y-%m-%d')}")
    print(f"Itérations : {total_iterations:,}")
    print("="*70)
    print()
    
    current_time = start_time
    iteration = 0
    total_traffic = 0
    total_transport = 0
    total_parking = 0
    
    cursor = conn.cursor()
    
    try:
        while current_time < end_time:
            iteration += 1
            
            # Traffic data
            traffic_data = traffic_gen.generate_traffic_data(current_time)
            for data in traffic_data:
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
                total_traffic += 1
            
            # Transport data
            transport_data = transport_gen.generate_bus_data(current_time)
            for data in transport_data:
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
                total_transport += 1
            
            # Parking data
            parking_data = parking_gen.generate_parking_data(current_time)
            for data in parking_data:
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
                total_parking += 1
            
            # Commit toutes les 100 itérations
            if iteration % 100 == 0:
                conn.commit()
                progress = (iteration / total_iterations) * 100
                total_records = total_traffic + total_transport + total_parking
                
                print(f"[{progress:>5.1f}%] Iteration {iteration:>8,}/{total_iterations:,} | "
                      f"Records: {total_records:>10,} | "
                      f"Date: {current_time.strftime('%Y-%m-%d %H:%M')}")
            
            current_time += timedelta(minutes=interval_minutes)
        
        # Commit final
        conn.commit()
        
        print()
        print("="*70)
        print("✅ GÉNÉRATION TERMINÉE")
        print("="*70)
        print(f"Traffic data    : {total_traffic:>12,} records")
        print(f"Transport data  : {total_transport:>12,} records")
        print(f"Parking data    : {total_parking:>12,} records")
        print(f"TOTAL           : {total_traffic + total_transport + total_parking:>12,} records")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_historical_data()
