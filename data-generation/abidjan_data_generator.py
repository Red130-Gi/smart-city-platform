"""
Générateur de données pour Abidjan Smart City
Génère des données réalistes basées sur les caractéristiques d'Abidjan
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.abidjan_config import *
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_batch

# Configuration PostgreSQL
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': 'smart_city_db',
    'user': 'smart_city',
    'password': 'smartcity123'
}

class AbidjanDataGenerator:
    def __init__(self):
        self.conn = psycopg2.connect(**PG_CONFIG)
        self.routes = ROUTES_PRINCIPALES
        self.zones = ZONES_TRAFIC
        self.communes = COMMUNES
        
    def calculate_traffic_speed(self, route, hour, day_of_week):
        """Calcule la vitesse réaliste selon l'heure et le type de route"""
        base_speed = route['vitesse_max']
        
        # Facteur heure de pointe
        rush = is_rush_hour(hour)
        if rush:
            multiplicateur = HEURES_POINTE[rush]['multiplicateur_trafic']
            base_speed = base_speed / multiplicateur
        
        # Facteur jour de semaine (weekend plus fluide)
        if day_of_week >= 5:  # Samedi/Dimanche
            base_speed *= 1.3
        
        # Facteur type de route
        if route['importance'] == 'critique':
            # Les ponts sont des points de congestion
            base_speed *= 0.7
        
        # Variation aléatoire ±15%
        variation = random.uniform(0.85, 1.15)
        final_speed = base_speed * variation
        
        # Limites réalistes pour Abidjan
        return max(5, min(final_speed, route['vitesse_max']))
    
    def calculate_vehicle_flow(self, route, hour, speed):
        """Calcule le flux de véhicules"""
        # Capacité théorique: 2000 véhicules/heure/voie
        capacity_per_lane = 2000
        total_capacity = capacity_per_lane * route['voies']
        
        # Facteur heure
        rush = is_rush_hour(hour)
        if rush:
            flow_factor = 0.9  # 90% de capacité en heure de pointe
        elif 22 <= hour or hour < 5:
            flow_factor = 0.1  # 10% la nuit
        else:
            flow_factor = 0.5  # 50% en journée normale
        
        # Le flux diminue si la vitesse est très basse (embouteillage)
        if speed < 15:
            flow_factor *= 0.6
        
        flow = int(total_capacity * flow_factor * random.uniform(0.8, 1.2))
        return max(10, flow)
    
    def calculate_occupancy(self, flow, capacity_per_lane, voies):
        """Calcule le taux d'occupation de la route"""
        total_capacity = capacity_per_lane * voies
        occupancy = (flow / total_capacity) * 100
        return min(100, occupancy)
    
    def generate_traffic_data(self, timestamp):
        """Génère des données de trafic pour toutes les routes"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        data_batch = []
        
        for route in self.routes:
            # Générer 2-3 capteurs par route
            nb_sensors = random.randint(2, 3)
            
            for i in range(nb_sensors):
                sensor_id = f"{route['id']}_S{i+1}"
                
                # Position le long de la route
                if i == 0:
                    lat, lon = route['start']['lat'], route['start']['lon']
                elif i == nb_sensors - 1:
                    lat, lon = route['end']['lat'], route['end']['lon']
                else:
                    # Position intermédiaire
                    ratio = i / nb_sensors
                    lat = route['start']['lat'] + (route['end']['lat'] - route['start']['lat']) * ratio
                    lon = route['start']['lon'] + (route['end']['lon'] - route['start']['lon']) * ratio
                
                # Calculs
                speed = self.calculate_traffic_speed(route, hour, day_of_week)
                flow = self.calculate_vehicle_flow(route, hour, speed)
                occupancy = self.calculate_occupancy(flow, 2000, route['voies'])
                
                # Zone de trafic
                commune = route['communes'][0] if route['communes'] else 'Plateau'
                zone_id = get_zone_from_commune(commune)
                
                # Niveau de congestion
                if speed > 50:
                    congestion = 'fluide'
                elif speed > 30:
                    congestion = 'moyen'
                elif speed > 15:
                    congestion = 'dense'
                else:
                    congestion = 'sature'
                
                data_batch.append((
                    timestamp,
                    sensor_id,
                    speed,
                    flow,
                    occupancy,
                    route['name'],
                    route['id'],
                    zone_id,
                    lat,
                    lon,
                    congestion,
                    'normal'
                ))
        
        return data_batch
    
    def generate_public_transport(self, timestamp):
        """Génère des données de transport en commun (Bus SOTRA)"""
        hour = timestamp.hour
        
        # Nombre de bus actifs selon l'heure
        if 6 <= hour < 22:
            nb_buses = random.randint(80, 120)
        else:
            nb_buses = random.randint(10, 30)
        
        data_batch = []
        
        for i in range(nb_buses):
            bus_id = f"SOTRA_{i+1:03d}"
            
            # Choisir une commune aléatoire
            commune = random.choice(list(COMMUNES.keys()))
            lat, lon = get_random_location_in_commune(commune)
            zone_id = get_zone_from_commune(commune)
            
            # Vitesse moyenne des bus
            base_speed = TRANSPORT_COMMUN['bus_sotra']['vitesse_moyenne']
            rush = is_rush_hour(hour)
            if rush:
                speed = base_speed / 1.5
            else:
                speed = base_speed * random.uniform(0.9, 1.1)
            
            # Occupation (50-100% en heure de pointe)
            if rush:
                occupancy = random.uniform(70, 100)
            else:
                occupancy = random.uniform(30, 70)
            
            # Ponctualité (70-95%)
            on_time = random.random() < 0.80
            delay_minutes = 0 if on_time else random.randint(5, 30)
            
            data_batch.append((
                timestamp,
                bus_id,
                f"Ligne {random.randint(1, 25)}",
                lat,
                lon,
                speed,
                occupancy,
                delay_minutes,
                zone_id
            ))
        
        return data_batch
    
    def generate_parking_data(self, timestamp):
        """Génère des données de parking"""
        hour = timestamp.hour
        
        # Parkings principaux à Abidjan
        parkings = [
            {'name': 'Parking Plateau Centre', 'capacity': 500, 'zone': 'zone-centre', 'lat': 5.320, 'lon': -4.010},
            {'name': 'Parking Adjamé Gare', 'capacity': 300, 'zone': 'zone-centre', 'lat': 5.355, 'lon': -4.020},
            {'name': 'Parking Cocody Centre', 'capacity': 400, 'zone': 'zone-est', 'lat': 5.360, 'lon': -3.980},
            {'name': 'Parking Aéroport', 'capacity': 600, 'zone': 'zone-sud', 'lat': 5.254, 'lon': -3.926},
            {'name': 'Parking Port Autonome', 'capacity': 350, 'zone': 'zone-sud', 'lat': 5.280, 'lon': -3.990},
            {'name': 'Parking Treichville', 'capacity': 250, 'zone': 'zone-sud', 'lat': 5.300, 'lon': -4.000},
            {'name': 'Parking Yopougon Centre', 'capacity': 300, 'zone': 'zone-ouest', 'lat': 5.340, 'lon': -4.090},
            {'name': 'Parking Marcory Zone 4', 'capacity': 200, 'zone': 'zone-sud', 'lat': 5.280, 'lon': -3.970}
        ]
        
        data_batch = []
        
        for parking in parkings:
            parking_id = f"P_{parking['name'].replace(' ', '_')}"
            
            # Taux d'occupation selon l'heure
            if 8 <= hour < 18:  # Journée de travail
                occupancy_rate = random.uniform(0.7, 0.95)
            elif 18 <= hour < 22:
                occupancy_rate = random.uniform(0.5, 0.8)
            else:
                occupancy_rate = random.uniform(0.2, 0.5)
            
            occupied_spots = int(parking['capacity'] * occupancy_rate)
            available_spots = parking['capacity'] - occupied_spots
            
            # Tarif (FCFA par heure)
            if parking['zone'] == 'zone-centre':
                tarif = random.randint(200, 500)
            else:
                tarif = random.randint(100, 300)
            
            data_batch.append((
                timestamp,
                parking_id,
                parking['name'],
                parking['capacity'],
                occupied_spots,
                available_spots,
                tarif,
                parking['zone'],
                parking['lat'],
                parking['lon']
            ))
        
        return data_batch
    
    def insert_data(self, timestamp):
        """Insère toutes les données pour un timestamp"""
        cursor = self.conn.cursor()
        
        try:
            # Traffic data
            traffic_data = self.generate_traffic_data(timestamp)
            execute_batch(cursor, """
                INSERT INTO traffic_data 
                (timestamp, sensor_id, speed_kmh, vehicle_flow, occupancy_percent,
                 road_name, road_id, zone_id, latitude, longitude, congestion_level, data_quality)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, traffic_data)
            
            # Public transport
            transport_data = self.generate_public_transport(timestamp)
            execute_batch(cursor, """
                INSERT INTO public_transport
                (timestamp, vehicle_id, route, latitude, longitude, speed_kmh,
                 occupancy_percent, delay_minutes, zone_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, transport_data)
            
            # Parking
            parking_data = self.generate_parking_data(timestamp)
            execute_batch(cursor, """
                INSERT INTO parking_data
                (timestamp, parking_id, parking_name, capacity, occupied_spots,
                 available_spots, hourly_rate, zone_id, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, parking_data)
            
            self.conn.commit()
            print(f"✅ Données générées pour {timestamp}: {len(traffic_data)} capteurs, {len(transport_data)} bus, {len(parking_data)} parkings")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erreur: {e}")
    
    def generate_continuous(self, interval_seconds=5):
        """Génère des données en continu"""
        print(f"\n{'='*70}")
        print("GÉNÉRATEUR DE DONNÉES ABIDJAN SMART CITY")
        print(f"{'='*70}\n")
        print(f"🌍 Ville : Abidjan, Côte d'Ivoire")
        print(f"📊 {len(ROUTES_PRINCIPALES)} routes principales")
        print(f"🗺️  {len(ZONES_TRAFIC)} zones de trafic")
        print(f"🏘️  {len(COMMUNES)} communes")
        print(f"⏱️  Intervalle : {interval_seconds} secondes\n")
        
        import time
        while True:
            try:
                timestamp = datetime.now()
                self.insert_data(timestamp)
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt du générateur")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                time.sleep(interval_seconds)
    
    def close(self):
        """Ferme la connexion"""
        self.conn.close()

if __name__ == '__main__':
    generator = AbidjanDataGenerator()
    try:
        generator.generate_continuous(interval_seconds=5)
    finally:
        generator.close()
