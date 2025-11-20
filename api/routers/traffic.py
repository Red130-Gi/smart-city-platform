from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from models.schemas import (
    TrafficSensor, TrafficPrediction, CongestionLevel, 
    APIResponse, PredictionRequest
)
from database import get_mongodb, get_redis
import random

router = APIRouter()

@router.get("/current", response_model=List[TrafficSensor])
async def get_current_traffic(
    zone_id: Optional[str] = None,
    road_id: Optional[str] = None,
    congestion_level: Optional[CongestionLevel] = None,
    limit: int = Query(default=100, le=500)
):
    """Get current traffic conditions from sensors"""
    # Simulated data for demo
    sensors = []
    for i in range(min(limit, 20)):
        sensor = TrafficSensor(
            sensor_id=f"traffic-sensor-{i:03d}",
            road_id=road_id or f"road-{random.randint(1,5)}",
            road_name=f"Route {i}",
            zone_id=zone_id or f"zone-{random.randint(1,5)}",
            location={"lat": 48.8566 + random.uniform(-0.1, 0.1), 
                     "lon": 2.3522 + random.uniform(-0.1, 0.1)},
            timestamp=datetime.now(),
            speed_kmh=random.uniform(20, 80),
            vehicle_flow=random.randint(50, 200),
            occupancy_percent=random.uniform(20, 90),
            congestion_level=congestion_level or random.choice(list(CongestionLevel)),
            data_quality="good"
        )
        sensors.append(sensor)
    
    return sensors

@router.get("/historical")
async def get_historical_traffic(
    road_id: str,
    start_time: datetime,
    end_time: datetime,
    mongodb=Depends(get_mongodb)
):
    """Get historical traffic data for analysis"""
    collection = mongodb.traffic_historical
    
    query = {
        "road_id": road_id,
        "timestamp": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    
    cursor = collection.find(query).limit(1000)
    data = await cursor.to_list(length=1000)
    
    return APIResponse(
        success=True,
        data=data
    )

@router.post("/predict", response_model=TrafficPrediction)
async def predict_traffic(request: PredictionRequest):
    """Predict future traffic conditions"""
    # Simulated ML prediction
    prediction = TrafficPrediction(
        road_id=request.road_id or "road-1",
        timestamp=request.timestamp + timedelta(minutes=request.horizon_minutes),
        predicted_speed=random.uniform(30, 60),
        predicted_flow=random.randint(80, 150),
        predicted_congestion=random.choice(list(CongestionLevel)),
        confidence=random.uniform(0.7, 0.95),
        horizon_minutes=request.horizon_minutes
    )
    
    return prediction

@router.get("/congestion-map")
async def get_congestion_map(redis_client=Depends(get_redis)):
    """Get city-wide congestion heatmap data"""
    # Try to get from cache
    cached = await redis_client.get("congestion_map")
    if cached:
        import json
        return json.loads(cached)
    
    # Generate congestion map
    congestion_map = {
        "timestamp": datetime.now().isoformat(),
        "zones": []
    }
    
    zones = ["zone-1", "zone-2", "zone-3", "zone-4", "zone-5"]
    for zone in zones:
        congestion_map["zones"].append({
            "zone_id": zone,
            "congestion_level": random.choice(["low", "medium", "high"]),
            "average_speed": random.uniform(25, 55),
            "incidents": random.randint(0, 3)
        })
    
    # Cache for 1 minute
    import json
    await redis_client.setex(
        "congestion_map", 
        60, 
        json.dumps(congestion_map)
    )
    
    return congestion_map

@router.get("/roads/{road_id}/status")
async def get_road_status(road_id: str):
    """Get detailed status for a specific road"""
    return {
        "road_id": road_id,
        "name": f"Road {road_id}",
        "status": "operational",
        "current_speed": random.uniform(30, 70),
        "speed_limit": 50,
        "congestion_level": random.choice(["low", "medium", "high"]),
        "incidents": [],
        "last_update": datetime.now().isoformat()
    }

@router.get("/flow-analysis")
async def analyze_traffic_flow(
    start_zone: str,
    end_zone: str,
    time_window: int = Query(default=60, description="Time window in minutes")
):
    """Analyze traffic flow between zones"""
    return {
        "origin": start_zone,
        "destination": end_zone,
        "time_window_minutes": time_window,
        "vehicle_count": random.randint(100, 500),
        "average_travel_time": random.uniform(15, 45),
        "peak_hour": f"{random.randint(7,9)}:00",
        "recommended_routes": [
            {"route": "Via Avenue Principale", "duration": 25},
            {"route": "Via Boulevard Périphérique", "duration": 30}
        ]
    }
