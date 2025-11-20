from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any
from datetime import datetime
from database import get_mongodb, get_redis
import json
import random

router = APIRouter()

@router.get("/predict/traffic")
async def predict_traffic(
    road: str = Query(..., description="Road ID"),
    datetime: str = Query(..., description="Target datetime (ISO format)"),
    redis_client=Depends(get_redis)
):
    """
    Predict future traffic conditions for a specific road and datetime
    
    Example: GET /predict/traffic?road=X&datetime=2024-01-15T13:00:00
    """
    try:
        # Check cache first
        cache_key = f"prediction:{road}:{datetime}"
        cached = await redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Simulated prediction (replace with ML model in production)
        prediction = {
            "road": road,
            "datetime": datetime,
            "prediction": {
                "speed_kmh": random.uniform(25, 65),
                "congestion": random.choice(["low", "medium", "high"]),
                "confidence": random.uniform(0.7, 0.95)
            },
            "status": "success"
        }
        
        # Cache for 5 minutes
        await redis_client.setex(cache_key, 300, json.dumps(prediction))
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/route")
async def recommend_route(
    origin: str = Query(..., description="Origin coordinates (lat,lon)"),
    destination: str = Query(..., description="Destination coordinates (lat,lon)"),
    datetime: str = Query(..., description="Departure datetime (ISO format)"),
    redis_client=Depends(get_redis)
):
    """
    Recommend optimal routes based on future traffic predictions
    
    Example: GET /recommend/route?origin=48.8566,2.3522&destination=48.8606,2.3376&datetime=2024-01-15T13:00:00
    """
    try:
        # Check cache
        cache_key = f"route:{origin}:{destination}:{datetime}"
        cached = await redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Parse coordinates
        origin_parts = origin.split(',')
        dest_parts = destination.split(',')
        
        if len(origin_parts) != 2 or len(dest_parts) != 2:
            raise HTTPException(status_code=400, detail="Coordinates must be in format 'lat,lon'")
        
        # Simulated route recommendation
        routes = [
            {
                "route_id": "route_1",
                "distance_km": random.uniform(4, 8),
                "duration_minutes": random.uniform(10, 25),
                "congestion": random.choice(["low", "medium"]),
                "reason": "Primary route"
            },
            {
                "route_id": "route_2",
                "distance_km": random.uniform(5, 10),
                "duration_minutes": random.uniform(12, 30),
                "congestion": random.choice(["low", "medium", "high"]),
                "reason": "Alternative route"
            }
        ]
        
        result = {
            "origin": origin,
            "destination": destination,
            "datetime": datetime,
            "routes": routes,
            "status": "success"
        }
        
        # Cache for 10 minutes
        await redis_client.setex(cache_key, 600, json.dumps(result))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{road_id}")
async def get_forecast(
    road_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Forecast horizon in hours"),
    redis_client=Depends(get_redis)
):
    """
    Get traffic forecast for a specific road
    """
    try:
        # Check cache
        cache_key = f"forecast:{road_id}:{hours}"
        cached = await redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Generate forecast
        current_time = datetime.now()
        predictions = []
        
        for i in range(0, hours, max(1, hours // 24)):
            target_time = current_time.timestamp() + (i * 3600)
            predictions.append({
                "datetime": datetime.fromtimestamp(target_time).isoformat(),
                "hours_ahead": i,
                "predicted_speed_kmh": 35 + random.uniform(-10, 15),
                "congestion_level": random.choice(["low", "medium", "high"]),
                "confidence": max(0.5, 0.95 - i * 0.005)
            })
        
        result = {
            "road_id": road_id,
            "forecast_start": current_time.isoformat(),
            "forecast_hours": hours,
            "predictions": predictions
        }
        
        # Cache for 30 minutes
        await redis_client.setex(cache_key, 1800, json.dumps(result))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
