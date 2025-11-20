from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from models.schemas import BusPosition, TransitRoute, APIResponse
from database import get_mongodb, get_redis
import random

router = APIRouter()

@router.get("/vehicles", response_model=List[BusPosition])
async def get_vehicle_positions(
    line_id: Optional[str] = None,
    zone_id: Optional[str] = None,
    limit: int = Query(default=50, le=200)
):
    """Get real-time positions of public transport vehicles"""
    vehicles = []
    
    for i in range(min(limit, 20)):
        vehicle = BusPosition(
            vehicle_id=f"bus-{i+1:03d}",
            line_id=line_id or f"line-{random.randint(1,5)}",
            line_number=str(random.randint(1,10)),
            timestamp=datetime.now(),
            location={
                "lat": 48.8566 + random.uniform(-0.05, 0.05),
                "lon": 2.3522 + random.uniform(-0.05, 0.05)
            },
            speed_kmh=random.uniform(10, 40),
            direction=random.choice(["outbound", "inbound"]),
            current_stop=random.randint(1, 15),
            next_stop=random.randint(2, 16),
            passenger_count=random.randint(10, 60),
            capacity=80,
            occupancy_rate=random.uniform(20, 90),
            delay_minutes=random.uniform(-2, 5),
            status=random.choice(["on_time", "delayed", "early"])
        )
        vehicles.append(vehicle)
    
    return vehicles

@router.get("/lines", response_model=List[TransitRoute])
async def get_transit_lines():
    """Get all public transport lines"""
    lines = []
    line_types = ["bus", "tram", "metro"]
    
    for i in range(10):
        line = TransitRoute(
            line_id=f"line-{i+1}",
            line_number=str(i+1),
            type=random.choice(line_types),
            stops=[
                {"stop_id": f"stop-{j}", "name": f"Station {j}", 
                 "lat": 48.8566 + random.uniform(-0.05, 0.05),
                 "lon": 2.3522 + random.uniform(-0.05, 0.05)}
                for j in range(1, random.randint(10, 20))
            ],
            frequency_minutes=random.randint(5, 15)
        )
        lines.append(line)
    
    return lines

@router.get("/lines/{line_id}/schedule")
async def get_line_schedule(line_id: str):
    """Get schedule for a specific line"""
    now = datetime.now()
    schedule = []
    
    for i in range(10):
        departure = now + timedelta(minutes=i*15)
        schedule.append({
            "departure_time": departure.isoformat(),
            "arrival_time": (departure + timedelta(minutes=random.randint(20, 40))).isoformat(),
            "vehicle_id": f"bus-{random.randint(1,20):03d}",
            "expected_occupancy": random.choice(["low", "medium", "high"])
        })
    
    return {
        "line_id": line_id,
        "schedule": schedule,
        "last_update": now.isoformat()
    }

@router.get("/stops/{stop_id}/arrivals")
async def get_stop_arrivals(stop_id: str):
    """Get upcoming arrivals at a specific stop"""
    arrivals = []
    now = datetime.now()
    
    for i in range(5):
        arrival = {
            "line_id": f"line-{random.randint(1,10)}",
            "line_number": str(random.randint(1,10)),
            "destination": f"Terminal {random.choice(['Nord', 'Sud', 'Est', 'Ouest'])}",
            "arrival_time": (now + timedelta(minutes=random.randint(1, 20))).isoformat(),
            "vehicle_id": f"bus-{random.randint(1,20):03d}",
            "real_time": random.choice([True, False])
        }
        arrivals.append(arrival)
    
    return {
        "stop_id": stop_id,
        "stop_name": f"Station {stop_id}",
        "arrivals": sorted(arrivals, key=lambda x: x["arrival_time"]),
        "timestamp": now.isoformat()
    }

@router.get("/performance/punctuality")
async def get_punctuality_stats(
    start_date: datetime = Query(default=datetime.now() - timedelta(days=7)),
    end_date: datetime = Query(default=datetime.now())
):
    """Get punctuality statistics for public transport"""
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "overall_punctuality": random.uniform(85, 95),
        "by_line": {
            f"line-{i}": random.uniform(80, 98) 
            for i in range(1, 6)
        },
        "by_time_period": {
            "morning_peak": random.uniform(75, 85),
            "midday": random.uniform(90, 98),
            "evening_peak": random.uniform(70, 80),
            "night": random.uniform(95, 99)
        },
        "total_trips": random.randint(5000, 10000),
        "on_time_trips": random.randint(4000, 9000),
        "delayed_trips": random.randint(500, 1500),
        "cancelled_trips": random.randint(10, 100)
    }

@router.post("/optimize/schedule")
async def optimize_schedule(line_id: str, optimization_params: Optional[dict] = {}):
    """Optimize schedule for a transport line"""
    return APIResponse(
        success=True,
        data={
            "line_id": line_id,
            "optimization_type": "schedule",
            "current_frequency": 15,
            "optimized_frequency": 12,
            "expected_improvement": {
                "waiting_time_reduction": "20%",
                "capacity_utilization": "85%",
                "cost_efficiency": "+15%"
            },
            "recommendations": [
                "Increase frequency during morning peak (7-9 AM)",
                "Reduce frequency during midday (11 AM - 2 PM)",
                "Add express service for long-distance commuters"
            ]
        }
    )

@router.get("/disruptions")
async def get_disruptions():
    """Get current service disruptions"""
    disruptions = []
    
    if random.random() > 0.7:  # 30% chance of disruptions
        disruptions.append({
            "disruption_id": f"dis-{random.randint(100,999)}",
            "type": random.choice(["delay", "cancellation", "route_change"]),
            "affected_lines": [f"line-{random.randint(1,5)}"],
            "description": "Technical issue causing delays",
            "start_time": datetime.now().isoformat(),
            "estimated_end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "severity": random.choice(["minor", "moderate", "major"])
        })
    
    return {
        "disruptions": disruptions,
        "total": len(disruptions),
        "last_update": datetime.now().isoformat()
    }
