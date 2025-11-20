from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from models.schemas import (
    RouteRequest, Route, RouteSegment, TransportMode,
    TaxiStatus, ParkingStatus, BikeStation, APIResponse
)
from database import get_redis
import random
import uuid

router = APIRouter()

@router.post("/route/plan", response_model=Route)
async def plan_route(request: RouteRequest):
    """Plan optimal multimodal route"""
    
    # Calculate distance (simplified)
    distance = ((request.destination.lat - request.origin.lat)**2 + 
                (request.destination.lon - request.origin.lon)**2)**0.5 * 111  # km
    
    # Generate route segments based on requested modes
    segments = []
    current_loc = request.origin
    remaining_distance = distance
    
    for i, mode in enumerate(request.modes[:3]):  # Max 3 segments for demo
        segment_distance = remaining_distance / (len(request.modes) - i)
        
        if mode == TransportMode.WALK:
            duration = segment_distance * 12  # 5 km/h walking speed
            cost = 0
            emissions = 0
        elif mode == TransportMode.BIKE:
            duration = segment_distance * 4  # 15 km/h bike speed
            cost = 1.5
            emissions = 0
        elif mode == TransportMode.BUS:
            duration = segment_distance * 3  # 20 km/h average
            cost = 2.5
            emissions = segment_distance * 50  # g CO2
        elif mode == TransportMode.METRO:
            duration = segment_distance * 2  # 30 km/h average
            cost = 3.0
            emissions = segment_distance * 30
        elif mode == TransportMode.TAXI:
            duration = segment_distance * 2.5
            cost = segment_distance * 2
            emissions = segment_distance * 150
        else:
            duration = segment_distance * 3
            cost = segment_distance * 0.5
            emissions = segment_distance * 200
        
        end_loc = {
            "lat": current_loc.lat + (request.destination.lat - current_loc.lat) * (i+1) / len(request.modes),
            "lon": current_loc.lon + (request.destination.lon - current_loc.lon) * (i+1) / len(request.modes)
        }
        
        segment = RouteSegment(
            mode=mode,
            start_location=current_loc,
            end_location=end_loc,
            distance_km=segment_distance,
            duration_minutes=duration,
            instructions=f"Take {mode.value} for {segment_distance:.1f} km",
            cost=cost,
            carbon_emissions=emissions
        )
        segments.append(segment)
        
        current_loc = end_loc
        remaining_distance -= segment_distance
    
    # Calculate totals
    total_distance = sum(s.distance_km for s in segments)
    total_duration = sum(s.duration_minutes for s in segments)
    total_cost = sum(s.cost for s in segments)
    total_emissions = sum(s.carbon_emissions for s in segments)
    
    departure = request.departure_time or datetime.now()
    arrival = departure + timedelta(minutes=total_duration)
    
    return Route(
        route_id=str(uuid.uuid4()),
        origin=request.origin,
        destination=request.destination,
        total_distance_km=total_distance,
        total_duration_minutes=total_duration,
        total_cost=total_cost,
        total_emissions=total_emissions,
        segments=segments,
        departure_time=departure,
        arrival_time=arrival
    )

@router.get("/route/alternatives")
async def get_alternative_routes(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
):
    """Get alternative route options"""
    alternatives = []
    
    route_options = [
        {"name": "Fastest", "modes": ["metro", "walk"], "duration": 25},
        {"name": "Cheapest", "modes": ["bus", "walk"], "duration": 35},
        {"name": "Eco-friendly", "modes": ["bike"], "duration": 30},
        {"name": "Comfortable", "modes": ["taxi"], "duration": 20},
        {"name": "Balanced", "modes": ["bus", "metro", "walk"], "duration": 28}
    ]
    
    for option in route_options:
        alternatives.append({
            "route_id": str(uuid.uuid4()),
            "name": option["name"],
            "modes": option["modes"],
            "duration_minutes": option["duration"],
            "cost": random.uniform(1, 15),
            "emissions_gco2": random.uniform(50, 500),
            "comfort_score": random.uniform(3, 5),
            "reliability_score": random.uniform(3.5, 5)
        })
    
    return {
        "origin": {"lat": origin_lat, "lon": origin_lon},
        "destination": {"lat": dest_lat, "lon": dest_lon},
        "alternatives": alternatives,
        "recommendation": alternatives[0]["route_id"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/taxis/nearby", response_model=List[TaxiStatus])
async def get_nearby_taxis(
    lat: float,
    lon: float,
    radius_km: float = 2.0,
    limit: int = 10
):
    """Get nearby available taxis"""
    taxis = []
    
    for i in range(min(limit, 10)):
        taxi = TaxiStatus(
            taxi_id=f"taxi-{random.randint(100,999)}",
            type=random.choice(["taxi", "vtc"]),
            timestamp=datetime.now(),
            location={
                "lat": lat + random.uniform(-0.02, 0.02),
                "lon": lon + random.uniform(-0.02, 0.02)
            },
            status="available",
            current_zone=f"zone-{random.randint(1,5)}",
            speed_kmh=random.uniform(0, 30),
            battery_level=random.randint(40, 100) if random.random() > 0.5 else None
        )
        taxis.append(taxi)
    
    return taxis

@router.get("/parking/nearby", response_model=List[ParkingStatus])
async def get_nearby_parking(
    lat: float,
    lon: float,
    radius_km: float = 1.0,
    min_spaces: int = 1
):
    """Find nearby parking with availability"""
    parking_lots = []
    
    for i in range(5):
        parking = ParkingStatus(
            parking_id=f"parking-{i+1}",
            name=f"Parking {['Nord', 'Sud', 'Est', 'Ouest', 'Centre'][i]}",
            zone_id=f"zone-{random.randint(1,5)}",
            type=random.choice(["street", "garage", "lot"]),
            location={
                "lat": lat + random.uniform(-0.01, 0.01),
                "lon": lon + random.uniform(-0.01, 0.01)
            },
            timestamp=datetime.now(),
            total_spaces=random.randint(50, 200),
            occupied_spaces=random.randint(30, 180),
            available_spaces=random.randint(5, 50),
            occupancy_rate=random.uniform(60, 95),
            hourly_rate=random.uniform(2, 5),
            status="available"
        )
        
        if parking.available_spaces >= min_spaces:
            parking_lots.append(parking)
    
    return parking_lots

@router.get("/bikes/stations", response_model=List[BikeStation])
async def get_bike_stations(
    zone_id: Optional[str] = None,
    available_bikes_min: int = 1
):
    """Get bike sharing stations with availability"""
    stations = []
    
    for i in range(10):
        station = BikeStation(
            station_id=f"bike-station-{i+1:03d}",
            name=f"Station {i+1}",
            zone_id=zone_id or f"zone-{random.randint(1,5)}",
            location={
                "lat": 48.8566 + random.uniform(-0.05, 0.05),
                "lon": 2.3522 + random.uniform(-0.05, 0.05)
            },
            timestamp=datetime.now(),
            capacity=random.randint(15, 30),
            available_bikes=random.randint(0, 25),
            available_docks=random.randint(0, 15),
            status="active"
        )
        
        if station.available_bikes >= available_bikes_min:
            stations.append(station)
    
    return stations

@router.post("/trip/start")
async def start_trip(
    user_id: str,
    route_id: str,
    mode: TransportMode
):
    """Start tracking a trip"""
    trip_id = str(uuid.uuid4())
    
    return APIResponse(
        success=True,
        data={
            "trip_id": trip_id,
            "user_id": user_id,
            "route_id": route_id,
            "mode": mode,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "tracking_enabled": True
        }
    )

@router.post("/trip/{trip_id}/end")
async def end_trip(trip_id: str):
    """End trip tracking and get summary"""
    return APIResponse(
        success=True,
        data={
            "trip_id": trip_id,
            "end_time": datetime.now().isoformat(),
            "duration_minutes": random.randint(15, 45),
            "distance_km": random.uniform(2, 15),
            "cost": random.uniform(2, 20),
            "carbon_saved_kg": random.uniform(0.5, 3),
            "calories_burned": random.randint(50, 300),
            "points_earned": random.randint(10, 100)
        }
    )

@router.get("/mobility/score")
async def get_mobility_score(user_id: str):
    """Get user's sustainable mobility score"""
    return {
        "user_id": user_id,
        "mobility_score": random.randint(60, 95),
        "level": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
        "stats": {
            "total_trips": random.randint(50, 200),
            "eco_trips": random.randint(30, 150),
            "carbon_saved_kg": random.uniform(10, 100),
            "distance_walked_km": random.uniform(20, 200),
            "distance_biked_km": random.uniform(10, 150)
        },
        "badges": [
            {"name": "Eco Warrior", "earned_date": "2024-01-15"},
            {"name": "Public Transport Champion", "earned_date": "2024-02-20"}
        ],
        "recommendations": [
            "Try biking for trips under 3km",
            "Use public transport during peak hours"
        ]
    }
