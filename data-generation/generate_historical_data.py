#!/usr/bin/env python3
"""
Générateur de données historiques pour Big Data
Génère des mois de données pour l'analyse Big Data
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
    CITY_ZONES
)

class HistoricalDataGenerator:
    """Génère des données historiques massives pour Big Data"""
    
    def __init__(self):
        self.pg_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.pg_db = os.getenv('POSTGRES_DB', 'smart_city_db')
        self.pg_user = os.getenv('POSTGRES_USER', 'smart_city')
        self.pg_password = os.getenv('POSTGRES_PASSWORD', 'smartcity123')
        self.pg_port = int(os.getenv('POSTGRES_PORT', '5432'))
        
        self.conn = psycopg2.connect(
            host=self.pg_host,
            dbname=self.pg_db,
            user=self.pg_user,
            password=self.pg_password,
            port=self.pg_port,
        )
        self.conn.autocommit = False
        
        self.traffic_gen = TrafficGenerator()
        self.transport_gen = PublicTransportGenerator()
        self.parking_gen = ParkingGenerator()
    
    def generate_batch_traffic(self, timestamp, batch_size=1000):
        """Génère un batch de données de trafic"""
        cursor = self.conn.cursor()
        
        data_batch = []
        for _ in range(batch_size):
            traffic_data = self.traffic_gen.generate_traffic_data(timestamp)
            for data in traffic_data:
                data_batch.append((
                    data['timestamp'], data['sensor_id'], data['road_id'],
                    data['road_name'], data['zone_id'], 
                    data['location']['lat'], data['location']['lon'],
                    data['speed_kmh'], data['vehicle_flow'], data['occupancy_percent'],
                    data['congestion_level'], data['data_quality']
                ))
        
        # Insertion en batch
        cursor.executemany("""
            INSERT INTO traffic_data 
            (timestamp, sensor_id, road_id, road_name, zone_id, lat, lon,
             speed_kmh, vehicle_flow, occupancy_percent, congestion_level, data_quality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data_batch)
        
        cursor.close()
        return len(data_batch)
    
    def generate_batch_transport(self, timestamp, batch_size=1000):
        """Génère un batch de données de transport"""
        cursor = self.conn.cursor()
        
        data_batch = []
        for _ in range(batch_size):
            transport_data = self.transport_gen.generate_bus_data(timestamp)
            for data in transport_data:
                data_batch.append((
                    data['timestamp'], data['vehicle_id'], data['line_id'],
                    data['line_number'], data['current_stop'], data['next_stop'],
                    data['direction'], data['location']['lat'], data['location']['lon'],
                    data['speed_kmh'], data['passenger_count'], data['capacity'],
                    data['occupancy_rate'], data['delay_minutes'], data['status']
                ))
        
        cursor.executemany("""
            INSERT INTO public_transport
            (timestamp, vehicle_id, line_id, line_number, current_stop, next_stop,
             direction, lat, lon, speed_kmh, passenger_count, capacity,
             occupancy_rate, delay_minutes, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data_batch)
        
        cursor.close()
        return len(data_batch)
    
    def generate_batch_parking(self, timestamp, batch_size=1000):
        """Génère un batch de données de parking"""
        cursor = self.conn.cursor()
        
        data_batch = []
        for _ in range(batch_size):
            parking_data = self.parking_gen.generate_parking_data(timestamp)
            for data in parking_data:
                data_batch.append((
                    data['timestamp'], data['parking_id'], data['name'],
                    data['zone_id'], data['type'],
                    data['location']['lat'], data['location']['lon'],
                    data['total_spaces'], data['occupied_spaces'], data['available_spaces'],
                    data['occupancy_rate'], data['hourly_rate'], data['status']
                ))
        
        cursor.executemany("""
            INSERT INTO parking_data
            (timestamp, parking_id, name, zone_id, type, lat, lon,
             total_spaces, occupied_spaces, available_spaces,
             occupancy_rate, hourly_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data_batch)
        
        cursor.close()
        return len(data_batch)
    
    def generate_historical_data(self, months=6, interval_minutes=5):
        """
        Génère des données historiques sur plusieurs mois
        
        Args:
            months: Nombre de mois à générer (défaut: 6)
            interval_minutes: Intervalle entre les mesures en minutes (défaut: 5)
        """
        print("="*70)
        print("GÉNÉRATEUR DE DONNÉES HISTORIQUES BIG DATA")
        print("="*70)
        print()
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30 * months)
        
        total_iterations = int((end_time - start_time).total_seconds() / (interval_minutes * 60))
        
        print(f"📅 Période : {start_time.strftime('%Y-%m-%d')} → {end_time.strftime('%Y-%m-%d')}")
        print(f"⏱️  Intervalle : {interval_minutes} minutes")
        print(f"🔢 Itérations estimées : {total_iterations:,}")
        print()
        
        # Estimation du volume
        records_per_iteration = 19 + 34 + 12  # traffic + transport + parking
        total_records = total_iterations * records_per_iteration
        size_mb = (total_records * 500) / (1024 * 1024)  # 500 bytes par record
        
        print(f"📊 Volume estimé : {total_records:,} records (~{size_mb:,.0f} MB)")
        print()
        
        confirmation = input("⚠️  Cette opération peut prendre plusieurs heures. Continuer? (y/n): ")
        if confirmation.lower() != 'y':
            print("❌ Annulé")
            return
        
        print()
        print("🚀 Génération en cours...")
        print()
        
        current_time = start_time
        iteration = 0
        total_traffic = 0
        total_transport = 0
        total_parking = 0
        
        try:
            while current_time < end_time:
                iteration += 1
                
                # Génération des données
                traffic_count = self.generate_batch_traffic(current_time, batch_size=1)
                transport_count = self.generate_batch_transport(current_time, batch_size=1)
                parking_count = self.generate_batch_parking(current_time, batch_size=1)
                
                total_traffic += traffic_count
                total_transport += transport_count
                total_parking += parking_count
                
                # Commit toutes les 100 itérations
                if iteration % 100 == 0:
                    self.conn.commit()
                    progress = (iteration / total_iterations) * 100
                    total_records_so_far = total_traffic + total_transport + total_parking
                    
                    print(f"  [{progress:>5.1f}%] Iteration {iteration:>8,}/{total_iterations:,} | "
                          f"Records: {total_records_so_far:>10,} | "
                          f"Date: {current_time.strftime('%Y-%m-%d %H:%M')}")
                
                current_time += timedelta(minutes=interval_minutes)
            
            # Commit final
            self.conn.commit()
            
            print()
            print("="*70)
            print("✅ GÉNÉRATION TERMINÉE")
            print("="*70)
            print()
            print(f"📊 Statistiques finales :")
            print(f"  • Traffic data      : {total_traffic:>12,} records")
            print(f"  • Transport data    : {total_transport:>12,} records")
            print(f"  • Parking data      : {total_parking:>12,} records")
            print(f"  • TOTAL             : {total_traffic + total_transport + total_parking:>12,} records")
            print()
            
        except KeyboardInterrupt:
            print()
            print("⚠️  Génération interrompue par l'utilisateur")
            self.conn.rollback()
        except Exception as e:
            print(f"❌ Erreur : {e}")
            self.conn.rollback()
        finally:
            self.conn.close()

def main():
    """Point d'entrée principal"""
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║    GÉNÉRATEUR DE DONNÉES HISTORIQUES - SMART CITY BIG DATA       ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    
    print("Options de génération :")
    print("  1. Léger    : 1 mois  (~ 500K records, ~250 MB, ~30 min)")
    print("  2. Moyen    : 3 mois  (~ 1.5M records, ~750 MB, ~1.5h)")
    print("  3. Complet  : 6 mois  (~ 3M records, ~1.5 GB, ~3h)")
    print("  4. Massif   : 12 mois (~ 6M records, ~3 GB, ~6h)")
    print("  5. Custom")
    print()
    
    choice = input("Choisissez une option (1-5): ")
    
    months_map = {
        '1': 1,
        '2': 3,
        '3': 6,
        '4': 12,
    }
    
    if choice in months_map:
        months = months_map[choice]
    elif choice == '5':
        months = int(input("Nombre de mois : "))
    else:
        print("❌ Option invalide")
        return
    
    print()
    generator = HistoricalDataGenerator()
    generator.generate_historical_data(months=months, interval_minutes=5)

if __name__ == "__main__":
    main()
