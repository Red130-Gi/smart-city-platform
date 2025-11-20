import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from faker import Faker
import os

fake = Faker()

# Define city zones and major roads
CITY_ZONES = [
    {"id": "zone-1", "name": "Centre-ville", "lat": 48.8566, "lon": 2.3522},
    {"id": "zone-2", "name": "Quartier d'affaires", "lat": 48.8924, "lon": 2.2360},
    {"id": "zone-3", "name": "Zone résidentielle Nord", "lat": 48.8934, "lon": 2.3487},
    {"id": "zone-4", "name": "Zone résidentielle Sud", "lat": 48.8334, "lon": 2.3333},
    {"id": "zone-5", "name": "Zone industrielle", "lat": 48.8456, "lon": 2.3921},
]

MAJOR_ROADS = [
    {"id": "road-1", "name": "Avenue Principale", "zones": ["zone-1", "zone-2"]},
    {"id": "road-2", "name": "Boulevard Périphérique", "zones": ["zone-1", "zone-3", "zone-4"]},
    {"id": "road-3", "name": "Rue Commerciale", "zones": ["zone-1"]},
    {"id": "road-4", "name": "Avenue Industrielle", "zones": ["zone-5"]},
    {"id": "road-5", "name": "Boulevard Nord-Sud", "zones": ["zone-3", "zone-1", "zone-4"]},
]

class TrafficGenerator:
    """Generate traffic sensor data"""
    
    def __init__(self):
        self.sensors = self._initialize_sensors()
        self.traffic_patterns = self._load_traffic_patterns()
        self.max_speed_kmh = float(os.getenv('MAX_SPEED_KMH', '90'))
    
    def _initialize_sensors(self) -> List[Dict]:
        sensors = []
        sensor_id = 1
        
        for road in MAJOR_ROADS:
            # Place 3-5 sensors per road
            num_sensors = random.randint(3, 5)
            for i in range(num_sensors):
                zone = random.choice(road['zones'])
                zone_data = next(z for z in CITY_ZONES if z['id'] == zone)
                
                sensors.append({
                    'sensor_id': f'traffic-sensor-{sensor_id:03d}',
                    'road_id': road['id'],
                    'road_name': road['name'],
                    'zone_id': zone,
                    'lat': zone_data['lat'] + random.uniform(-0.01, 0.01),
                    'lon': zone_data['lon'] + random.uniform(-0.01, 0.01)
                })
                sensor_id += 1
        
        return sensors
    
    def _load_traffic_patterns(self) -> Dict:
        """Load typical traffic patterns for different times"""
        return {
            'morning_peak': {'hours': [7, 8, 9], 'multiplier': 1.8},
            'lunch': {'hours': [12, 13], 'multiplier': 1.3},
            'evening_peak': {'hours': [17, 18, 19], 'multiplier': 2.0},
            'night': {'hours': [0, 1, 2, 3, 4, 5], 'multiplier': 0.3},
            'normal': {'hours': [10, 11, 14, 15, 16, 20, 21, 22, 23], 'multiplier': 1.0}
        }
    
    def _get_traffic_multiplier(self, timestamp: datetime) -> float:
        hour = timestamp.hour
        for pattern, config in self.traffic_patterns.items():
            if hour in config['hours']:
                return config['multiplier']
        return 1.0
    
    def generate_traffic_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        multiplier = self._get_traffic_multiplier(timestamp)
        
        for sensor in self.sensors:
            # Base values with time-based variation
            base_speed = 50  # km/h
            base_flow = 100  # vehicles per 5 min
            
            # Add randomness and time-based patterns
            speed = max(10, base_speed / multiplier + random.uniform(-10, 10))
            speed = min(speed, self.max_speed_kmh)
            flow = int(base_flow * multiplier + random.uniform(-20, 20))
            occupancy = min(100, flow / 2 + random.uniform(0, 20))  # percentage
            
            # Calculate congestion level
            if speed < 20:
                congestion_level = "high"
            elif speed < 35:
                congestion_level = "medium"
            else:
                congestion_level = "low"
            
            data.append({
                'sensor_id': sensor['sensor_id'],
                'timestamp': timestamp.isoformat(),
                'road_id': sensor['road_id'],
                'road_name': sensor['road_name'],
                'zone_id': sensor['zone_id'],
                'location': {
                    'lat': sensor['lat'],
                    'lon': sensor['lon']
                },
                'speed_kmh': round(speed, 1),
                'vehicle_flow': flow,
                'occupancy_percent': round(occupancy, 1),
                'congestion_level': congestion_level,
                'data_quality': 'good' if random.random() > 0.05 else 'degraded'
            })
        
        return data

class PublicTransportGenerator:
    """Generate public transport (bus, tram, metro) data"""
    
    def __init__(self):
        self.bus_lines = self._initialize_bus_lines()
        self.vehicles = self._initialize_vehicles()
    
    def _initialize_bus_lines(self) -> List[Dict]:
        lines = []
        line_numbers = ['1', '2', '3A', '3B', '4', '5', 'Express-1', 'Express-2']
        
        for line_num in line_numbers:
            stops = random.randint(10, 20)
            zones = random.sample([z['id'] for z in CITY_ZONES], k=min(3, len(CITY_ZONES)))
            
            lines.append({
                'line_id': f'line-{line_num}',
                'line_number': line_num,
                'type': 'express' if 'Express' in line_num else 'regular',
                'stops': stops,
                'zones': zones,
                'frequency_minutes': 10 if 'Express' in line_num else 15
            })
        
        return lines
    
    def _initialize_vehicles(self) -> List[Dict]:
        vehicles = []
        vehicle_id = 1
        
        for line in self.bus_lines:
            # 3-5 vehicles per line
            num_vehicles = random.randint(3, 5)
            for i in range(num_vehicles):
                vehicles.append({
                    'vehicle_id': f'bus-{vehicle_id:03d}',
                    'line_id': line['line_id'],
                    'capacity': 60 if line['type'] == 'regular' else 100,
                    'current_stop': random.randint(1, line['stops']),
                    'direction': random.choice(['outbound', 'inbound'])
                })
                vehicle_id += 1
        
        return vehicles
    
    def generate_bus_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        
        for vehicle in self.vehicles:
            line = next(l for l in self.bus_lines if l['line_id'] == vehicle['line_id'])
            zone = random.choice(line['zones'])
            zone_data = next(z for z in CITY_ZONES if z['id'] == zone)
            
            # Simulate passenger count based on time
            hour = timestamp.hour
            if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
                passenger_count = random.randint(40, vehicle['capacity'])
            elif hour in [0, 1, 2, 3, 4, 5]:  # Night
                passenger_count = random.randint(0, 10)
            else:
                passenger_count = random.randint(15, 35)
            
            # Simulate delays
            scheduled_time = timestamp
            actual_time = timestamp + timedelta(minutes=random.randint(-2, 5))
            delay_minutes = (actual_time - scheduled_time).total_seconds() / 60
            
            data.append({
                'vehicle_id': vehicle['vehicle_id'],
                'timestamp': timestamp.isoformat(),
                'line_id': line['line_id'],
                'line_number': line['line_number'],
                'current_stop': vehicle['current_stop'],
                'next_stop': (vehicle['current_stop'] % line['stops']) + 1,
                'direction': vehicle['direction'],
                'location': {
                    'lat': zone_data['lat'] + random.uniform(-0.005, 0.005),
                    'lon': zone_data['lon'] + random.uniform(-0.005, 0.005)
                },
                'speed_kmh': random.uniform(15, 40),
                'passenger_count': passenger_count,
                'capacity': vehicle['capacity'],
                'occupancy_rate': round(passenger_count / vehicle['capacity'] * 100, 1),
                'delay_minutes': round(delay_minutes, 1),
                'status': 'on_time' if abs(delay_minutes) < 3 else 'delayed'
            })
            
            # Move to next stop
            if random.random() > 0.7:
                vehicle['current_stop'] = (vehicle['current_stop'] % line['stops']) + 1
        
        return data

class TaxiGenerator:
    """Generate taxi and VTC data"""
    
    def __init__(self):
        self.taxis = self._initialize_taxis()
    
    def _initialize_taxis(self) -> List[Dict]:
        taxis = []
        
        for i in range(50):  # 50 taxis in the city
            zone = random.choice(CITY_ZONES)
            
            taxis.append({
                'taxi_id': f'taxi-{i+1:03d}',
                'type': random.choice(['taxi', 'vtc', 'vtc']),  # More VTCs
                'current_zone': zone['id'],
                'status': random.choice(['available', 'occupied', 'off_duty']),
                'lat': zone['lat'] + random.uniform(-0.01, 0.01),
                'lon': zone['lon'] + random.uniform(-0.01, 0.01)
            })
        
        return taxis
    
    def generate_taxi_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        
        for taxi in self.taxis:
            # Update taxi status randomly
            if random.random() < 0.1:  # 10% chance to change status
                old_status = taxi['status']
                if old_status == 'available':
                    taxi['status'] = random.choice(['occupied', 'available', 'available'])
                elif old_status == 'occupied':
                    taxi['status'] = random.choice(['available', 'occupied', 'occupied'])
                else:
                    taxi['status'] = random.choice(['available', 'off_duty'])
            
            # Move taxi slightly
            taxi['lat'] += random.uniform(-0.001, 0.001)
            taxi['lon'] += random.uniform(-0.001, 0.001)
            
            # Generate fare info if occupied
            fare_info = None
            if taxi['status'] == 'occupied':
                fare_info = {
                    'trip_id': str(uuid.uuid4()),
                    'start_zone': taxi['current_zone'],
                    'estimated_fare': round(random.uniform(10, 50), 2),
                    'estimated_duration_min': random.randint(5, 30)
                }
            
            data.append({
                'taxi_id': taxi['taxi_id'],
                'timestamp': timestamp.isoformat(),
                'type': taxi['type'],
                'status': taxi['status'],
                'location': {
                    'lat': taxi['lat'],
                    'lon': taxi['lon']
                },
                'current_zone': taxi['current_zone'],
                'speed_kmh': random.uniform(0, 60) if taxi['status'] == 'occupied' else 0,
                'fare_info': fare_info,
                'battery_level': random.randint(20, 100) if taxi['type'] == 'vtc' else None
            })
        
        return data

class ParkingGenerator:
    """Generate parking availability data"""
    
    def __init__(self):
        self.parking_lots = self._initialize_parking()
    
    def _initialize_parking(self) -> List[Dict]:
        parking = []
        
        for i, zone in enumerate(CITY_ZONES):
            # 2-3 parking lots per zone
            for j in range(random.randint(2, 3)):
                parking.append({
                    'parking_id': f'parking-{zone["id"]}-{j+1}',
                    'name': f'{zone["name"]} Parking {j+1}',
                    'zone_id': zone['id'],
                    'type': random.choice(['street', 'garage', 'lot']),
                    'total_spaces': random.randint(50, 200),
                    'lat': zone['lat'] + random.uniform(-0.005, 0.005),
                    'lon': zone['lon'] + random.uniform(-0.005, 0.005),
                    'hourly_rate': random.uniform(2, 5)
                })
        
        return parking
    
    def generate_parking_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        hour = timestamp.hour
        
        for parking in self.parking_lots:
            # Occupancy based on time and zone
            if parking['zone_id'] in ['zone-1', 'zone-2']:  # Business areas
                if hour in range(9, 17):  # Business hours
                    occupancy_rate = random.uniform(0.7, 0.95)
                else:
                    occupancy_rate = random.uniform(0.2, 0.5)
            else:  # Residential areas
                if hour in range(20, 24) or hour in range(0, 7):  # Night
                    occupancy_rate = random.uniform(0.6, 0.9)
                else:
                    occupancy_rate = random.uniform(0.3, 0.6)
            
            occupied_spaces = int(parking['total_spaces'] * occupancy_rate)
            available_spaces = parking['total_spaces'] - occupied_spaces
            
            data.append({
                'parking_id': parking['parking_id'],
                'timestamp': timestamp.isoformat(),
                'name': parking['name'],
                'zone_id': parking['zone_id'],
                'type': parking['type'],
                'location': {
                    'lat': parking['lat'],
                    'lon': parking['lon']
                },
                'total_spaces': parking['total_spaces'],
                'occupied_spaces': occupied_spaces,
                'available_spaces': available_spaces,
                'occupancy_rate': round(occupancy_rate * 100, 1),
                'hourly_rate': parking['hourly_rate'],
                'status': 'full' if available_spaces < 5 else 'available'
            })
        
        return data

class BikeShareGenerator:
    """Generate bike sharing station data"""
    
    def __init__(self):
        self.stations = self._initialize_stations()
    
    def _initialize_stations(self) -> List[Dict]:
        stations = []
        station_id = 1
        
        for zone in CITY_ZONES:
            # 3-5 stations per zone
            for i in range(random.randint(3, 5)):
                stations.append({
                    'station_id': f'bike-station-{station_id:03d}',
                    'name': f'{zone["name"]} Station {i+1}',
                    'zone_id': zone['id'],
                    'capacity': random.randint(15, 30),
                    'lat': zone['lat'] + random.uniform(-0.005, 0.005),
                    'lon': zone['lon'] + random.uniform(-0.005, 0.005)
                })
                station_id += 1
        
        return stations
    
    def generate_bike_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        hour = timestamp.hour
        
        for station in self.stations:
            # Bike availability patterns
            if hour in range(7, 10):  # Morning commute
                availability_rate = random.uniform(0.3, 0.6)
            elif hour in range(17, 20):  # Evening commute
                availability_rate = random.uniform(0.4, 0.7)
            else:
                availability_rate = random.uniform(0.5, 0.8)
            
            available_bikes = int(station['capacity'] * availability_rate)
            available_docks = station['capacity'] - available_bikes
            
            data.append({
                'station_id': station['station_id'],
                'timestamp': timestamp.isoformat(),
                'name': station['name'],
                'zone_id': station['zone_id'],
                'location': {
                    'lat': station['lat'],
                    'lon': station['lon']
                },
                'capacity': station['capacity'],
                'available_bikes': available_bikes,
                'available_docks': available_docks,
                'status': 'active' if random.random() > 0.05 else 'maintenance',
                'last_update': timestamp.isoformat()
            })
        
        return data

class IncidentGenerator:
    """Generate traffic incidents and events"""
    
    def __init__(self):
        self.incident_types = [
            'accident', 'breakdown', 'roadwork', 'event', 
            'demonstration', 'flooding', 'power_outage'
        ]
    
    def generate_incident(self, timestamp: datetime) -> Dict:
        if random.random() > 0.3:  # 30% chance of incident
            return None
        
        road = random.choice(MAJOR_ROADS)
        zone_id = random.choice(road['zones'])
        zone = next(z for z in CITY_ZONES if z['id'] == zone_id)
        
        incident_type = random.choice(self.incident_types)
        
        # Severity based on type
        if incident_type in ['accident', 'flooding']:
            severity = random.choice(['high', 'high', 'medium'])
        elif incident_type in ['demonstration', 'event']:
            severity = 'medium'
        else:
            severity = random.choice(['low', 'medium'])
        
        return {
            'incident_id': str(uuid.uuid4()),
            'timestamp': timestamp.isoformat(),
            'type': incident_type,
            'severity': severity,
            'location': {
                'road_id': road['id'],
                'road_name': road['name'],
                'zone_id': zone_id,
                'lat': zone['lat'] + random.uniform(-0.005, 0.005),
                'lon': zone['lon'] + random.uniform(-0.005, 0.005)
            },
            'description': f'{incident_type.capitalize()} reported on {road["name"]}',
            'estimated_duration_min': random.randint(15, 120),
            'affected_lanes': random.randint(1, 2),
            'status': 'active'
        }

class WeatherGenerator:
    """Generate weather data"""
    
    def __init__(self):
        self.conditions = ['clear', 'cloudy', 'rain', 'fog', 'snow']
        self.current_condition = random.choice(self.conditions)
    
    def generate_weather_data(self, timestamp: datetime) -> Dict:
        # Weather changes slowly
        if random.random() < 0.05:  # 5% chance to change
            self.current_condition = random.choice(self.conditions)
        
        # Temperature based on time of day
        hour = timestamp.hour
        if hour in range(0, 6):
            base_temp = 10
        elif hour in range(6, 12):
            base_temp = 15
        elif hour in range(12, 18):
            base_temp = 20
        else:
            base_temp = 15
        
        temperature = base_temp + random.uniform(-3, 3)
        
        # Adjust for weather condition
        if self.current_condition == 'snow':
            temperature = min(temperature, 2)
        elif self.current_condition == 'rain':
            temperature -= 2
        
        return {
            'timestamp': timestamp.isoformat(),
            'condition': self.current_condition,
            'temperature_celsius': round(temperature, 1),
            'humidity_percent': random.randint(40, 90),
            'wind_speed_kmh': random.uniform(5, 30),
            'precipitation_mm': random.uniform(0, 10) if self.current_condition in ['rain', 'snow'] else 0,
            'visibility_km': random.uniform(1, 10) if self.current_condition != 'fog' else random.uniform(0.1, 1),
            'uv_index': random.randint(1, 11) if self.current_condition == 'clear' else random.randint(1, 3)
        }

class PollutionGenerator:
    """Generate air quality data"""
    
    def __init__(self):
        self.stations = self._initialize_stations()
    
    def _initialize_stations(self) -> List[Dict]:
        stations = []
        
        for zone in CITY_ZONES:
            stations.append({
                'station_id': f'air-quality-{zone["id"]}',
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'lat': zone['lat'],
                'lon': zone['lon']
            })
        
        return stations
    
    def generate_pollution_data(self, timestamp: datetime) -> List[Dict]:
        data = []
        hour = timestamp.hour
        
        for station in self.stations:
            # Pollution levels based on traffic patterns
            if station['zone_id'] in ['zone-1', 'zone-2']:  # High traffic areas
                if hour in [7, 8, 9, 17, 18, 19]:  # Rush hours
                    pm25 = random.uniform(35, 75)
                    pm10 = random.uniform(50, 100)
                    no2 = random.uniform(40, 80)
                else:
                    pm25 = random.uniform(20, 40)
                    pm10 = random.uniform(30, 60)
                    no2 = random.uniform(20, 50)
            else:  # Lower traffic areas
                pm25 = random.uniform(10, 30)
                pm10 = random.uniform(15, 40)
                no2 = random.uniform(10, 35)
            
            # Calculate AQI
            aqi = max(pm25 * 2, pm10 * 1.5, no2 * 1.2)
            
            if aqi < 50:
                quality = 'good'
            elif aqi < 100:
                quality = 'moderate'
            elif aqi < 150:
                quality = 'unhealthy_sensitive'
            elif aqi < 200:
                quality = 'unhealthy'
            else:
                quality = 'very_unhealthy'
            
            data.append({
                'station_id': station['station_id'],
                'timestamp': timestamp.isoformat(),
                'zone_id': station['zone_id'],
                'zone_name': station['zone_name'],
                'location': {
                    'lat': station['lat'],
                    'lon': station['lon']
                },
                'pollutants': {
                    'pm25': round(pm25, 1),
                    'pm10': round(pm10, 1),
                    'no2': round(no2, 1),
                    'o3': round(random.uniform(20, 60), 1),
                    'co': round(random.uniform(0.5, 2), 1),
                    'so2': round(random.uniform(5, 20), 1)
                },
                'aqi': round(aqi),
                'air_quality': quality
            })
        
        return data
