from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class CongestionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"

class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OFF_DUTY = "off_duty"
    MAINTENANCE = "maintenance"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransportMode(str, Enum):
    BUS = "bus"
    METRO = "metro"
    TRAM = "tram"
    BIKE = "bike"
    TAXI = "taxi"
    WALK = "walk"
    CAR = "car"

# Location Models
class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [lon, lat]

# Traffic Models
class TrafficSensor(BaseModel):
    sensor_id: str
    road_id: str
    road_name: str
    zone_id: str
    location: Location
    timestamp: datetime
    speed_kmh: float = Field(..., ge=0)
    vehicle_flow: int = Field(..., ge=0)
    occupancy_percent: float = Field(..., ge=0, le=100)
    congestion_level: CongestionLevel
    data_quality: str

class TrafficPrediction(BaseModel):
    road_id: str
    timestamp: datetime
    predicted_speed: float
    predicted_flow: int
    predicted_congestion: CongestionLevel
    confidence: float = Field(..., ge=0, le=1)
    horizon_minutes: int

# Public Transport Models
class BusPosition(BaseModel):
    vehicle_id: str
    line_id: str
    line_number: str
    timestamp: datetime
    location: Location
    speed_kmh: float
    direction: str
    current_stop: int
    next_stop: int
    passenger_count: int
    capacity: int
    occupancy_rate: float
    delay_minutes: float
    status: str

class TransitRoute(BaseModel):
    line_id: str
    line_number: str
    type: str
    stops: List[Dict[str, Any]]
    schedule: Optional[List[datetime]]
    frequency_minutes: int
    
# Taxi/VTC Models
class TaxiStatus(BaseModel):
    taxi_id: str
    type: str  # taxi or vtc
    timestamp: datetime
    location: Location
    status: VehicleStatus
    current_zone: str
    speed_kmh: Optional[float]
    fare_info: Optional[Dict[str, Any]]
    battery_level: Optional[int]

# Parking Models
class ParkingStatus(BaseModel):
    parking_id: str
    name: str
    zone_id: str
    type: str
    location: Location
    timestamp: datetime
    total_spaces: int
    occupied_spaces: int
    available_spaces: int
    occupancy_rate: float
    hourly_rate: float
    status: str

# Bike Share Models
class BikeStation(BaseModel):
    station_id: str
    name: str
    zone_id: str
    location: Location
    timestamp: datetime
    capacity: int
    available_bikes: int
    available_docks: int
    status: str

# Incident Models
class Incident(BaseModel):
    incident_id: str
    timestamp: datetime
    type: str
    severity: IncidentSeverity
    location: Dict[str, Any]
    description: str
    estimated_duration_min: int
    affected_lanes: Optional[int]
    status: str

# Route Planning Models
class RouteRequest(BaseModel):
    origin: Location
    destination: Location
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    modes: List[TransportMode]
    preferences: Optional[Dict[str, Any]] = {}
    
class RouteSegment(BaseModel):
    mode: TransportMode
    start_location: Location
    end_location: Location
    distance_km: float
    duration_minutes: float
    instructions: str
    line_info: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    carbon_emissions: Optional[float] = None

class Route(BaseModel):
    route_id: str
    origin: Location
    destination: Location
    total_distance_km: float
    total_duration_minutes: float
    total_cost: float
    total_emissions: float
    segments: List[RouteSegment]
    departure_time: datetime
    arrival_time: datetime
    
# Analytics Models
class ZoneStatistics(BaseModel):
    zone_id: str
    zone_name: str
    timestamp: datetime
    metrics: Dict[str, float]
    
class TrafficFlow(BaseModel):
    origin_zone: str
    destination_zone: str
    timestamp: datetime
    vehicle_count: int
    average_speed: float
    average_duration: float

class PredictionRequest(BaseModel):
    location: Optional[Location] = None
    road_id: Optional[str] = None
    timestamp: datetime
    horizon_minutes: int = Field(default=30, ge=5, le=120)
    
class OptimizationRequest(BaseModel):
    zone_id: str
    optimization_type: str  # "traffic_lights", "route", "fleet"
    constraints: Optional[Dict[str, Any]] = {}
    objectives: Optional[List[str]] = ["minimize_congestion"]

# Response Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

# Real-time Updates
class RealtimeUpdate(BaseModel):
    update_type: str
    entity_id: str
    entity_type: str
    data: Dict[str, Any]
    timestamp: datetime
    
# Air Quality Models
class AirQuality(BaseModel):
    station_id: str
    zone_id: str
    zone_name: str
    location: Location
    timestamp: datetime
    pollutants: Dict[str, float]
    aqi: int
    air_quality: str
    
# Weather Models  
class Weather(BaseModel):
    timestamp: datetime
    condition: str
    temperature_celsius: float
    humidity_percent: int
    wind_speed_kmh: float
    precipitation_mm: float
    visibility_km: float
    uv_index: int
