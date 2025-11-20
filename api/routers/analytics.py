from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from models.schemas import ZoneStatistics, AirQuality, Weather, APIResponse
from database import get_mongodb, get_redis
import random
import numpy as np

router = APIRouter()

@router.get("/zones/statistics", response_model=List[ZoneStatistics])
async def get_zone_statistics():
    """Get statistics for all city zones"""
    zones = ["zone-1", "zone-2", "zone-3", "zone-4", "zone-5"]
    zone_names = ["Centre-ville", "Quartier d'affaires", "Nord", "Sud", "Industrielle"]
    
    statistics = []
    for i, zone_id in enumerate(zones):
        stats = ZoneStatistics(
            zone_id=zone_id,
            zone_name=zone_names[i],
            timestamp=datetime.now(),
            metrics={
                "average_speed_kmh": random.uniform(25, 55),
                "congestion_index": random.uniform(0.3, 0.9),
                "vehicle_count": random.randint(500, 2000),
                "incident_count": random.randint(0, 5),
                "parking_occupancy": random.uniform(40, 95),
                "public_transport_usage": random.randint(1000, 5000),
                "bike_usage": random.randint(100, 500),
                "air_quality_index": random.randint(40, 150)
            }
        )
        statistics.append(stats)
    
    return statistics

@router.get("/trends/traffic")
async def get_traffic_trends(
    zone_id: Optional[str] = None,
    period_days: int = Query(default=7, le=30)
):
    """Get traffic trends over time"""
    now = datetime.now()
    trends = []
    
    for i in range(period_days * 24):  # Hourly data
        timestamp = now - timedelta(hours=i)
        hour = timestamp.hour
        
        # Simulate traffic patterns
        if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
            base_flow = random.uniform(150, 200)
        elif hour in [0, 1, 2, 3, 4, 5]:  # Night
            base_flow = random.uniform(20, 50)
        else:
            base_flow = random.uniform(80, 120)
        
        trends.append({
            "timestamp": timestamp.isoformat(),
            "vehicle_flow": int(base_flow + random.uniform(-20, 20)),
            "average_speed": random.uniform(30, 60),
            "congestion_level": "high" if base_flow > 150 else "medium" if base_flow > 80 else "low"
        })
    
    return {
        "zone_id": zone_id or "all",
        "period_days": period_days,
        "data_points": len(trends),
        "trends": trends[:168],  # Return last week of hourly data
        "summary": {
            "peak_hours": ["07:00-09:00", "17:00-19:00"],
            "average_daily_flow": random.randint(20000, 50000),
            "congestion_increase": f"+{random.uniform(5, 25):.1f}%"
        }
    }

@router.get("/predictions/demand")
async def predict_transport_demand(
    zone_id: str,
    forecast_hours: int = Query(default=24, le=72)
):
    """Predict transport demand for the next hours"""
    predictions = []
    now = datetime.now()
    
    for i in range(forecast_hours):
        timestamp = now + timedelta(hours=i)
        hour = timestamp.hour
        
        # Base demand patterns
        if hour in range(7, 10):
            base_demand = random.uniform(0.8, 1.0)
        elif hour in range(17, 20):
            base_demand = random.uniform(0.85, 1.0)
        elif hour in range(0, 6):
            base_demand = random.uniform(0.1, 0.3)
        else:
            base_demand = random.uniform(0.4, 0.6)
        
        predictions.append({
            "timestamp": timestamp.isoformat(),
            "predicted_demand": int(base_demand * 1000),
            "confidence": random.uniform(0.7, 0.95),
            "transport_modes": {
                "bus": int(base_demand * 400),
                "metro": int(base_demand * 300),
                "taxi": int(base_demand * 200),
                "bike": int(base_demand * 100)
            }
        })
    
    return {
        "zone_id": zone_id,
        "forecast_hours": forecast_hours,
        "predictions": predictions,
        "model_info": {
            "model_type": "LSTM",
            "last_trained": datetime.now().isoformat(),
            "accuracy": 0.87
        }
    }

@router.get("/air-quality/current")
async def get_air_quality():
    """Get current air quality measurements"""
    stations = []
    zones = ["zone-1", "zone-2", "zone-3", "zone-4", "zone-5"]
    zone_names = ["Centre-ville", "Quartier d'affaires", "Nord", "Sud", "Industrielle"]
    
    for i, zone_id in enumerate(zones):
        # Industrial zone has worse air quality
        if zone_id == "zone-5":
            pm25 = random.uniform(45, 85)
            pm10 = random.uniform(60, 110)
        else:
            pm25 = random.uniform(15, 45)
            pm10 = random.uniform(25, 60)
        
        aqi = max(pm25 * 2, pm10 * 1.5)
        
        quality = AirQuality(
            station_id=f"air-quality-{zone_id}",
            zone_id=zone_id,
            zone_name=zone_names[i],
            location={
                "lat": 48.8566 + random.uniform(-0.05, 0.05),
                "lon": 2.3522 + random.uniform(-0.05, 0.05)
            },
            timestamp=datetime.now(),
            pollutants={
                "pm25": round(pm25, 1),
                "pm10": round(pm10, 1),
                "no2": round(random.uniform(20, 60), 1),
                "o3": round(random.uniform(30, 70), 1),
                "co": round(random.uniform(0.5, 2), 1),
                "so2": round(random.uniform(5, 25), 1)
            },
            aqi=int(aqi),
            air_quality="good" if aqi < 50 else "moderate" if aqi < 100 else "unhealthy"
        )
        stations.append(quality)
    
    return stations

@router.get("/weather/current")
async def get_weather():
    """Get current weather conditions"""
    conditions = ["clear", "cloudy", "rain", "fog"]
    current_condition = random.choice(conditions)
    
    weather = Weather(
        timestamp=datetime.now(),
        condition=current_condition,
        temperature_celsius=random.uniform(10, 25),
        humidity_percent=random.randint(40, 80),
        wind_speed_kmh=random.uniform(5, 25),
        precipitation_mm=random.uniform(0, 5) if current_condition == "rain" else 0,
        visibility_km=random.uniform(5, 10) if current_condition != "fog" else random.uniform(0.5, 2),
        uv_index=random.randint(1, 8)
    )
    
    return weather

@router.get("/emissions/summary")
async def get_emissions_summary(
    start_date: datetime = Query(default=datetime.now() - timedelta(days=7)),
    end_date: datetime = Query(default=datetime.now())
):
    """Get CO2 emissions summary"""
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_emissions_tons": random.uniform(500, 1500),
        "by_transport_mode": {
            "cars": random.uniform(300, 800),
            "buses": random.uniform(100, 300),
            "trucks": random.uniform(100, 400),
            "motorcycles": random.uniform(20, 50)
        },
        "by_zone": {
            f"zone-{i+1}": random.uniform(50, 350) 
            for i in range(5)
        },
        "daily_average": random.uniform(70, 210),
        "comparison": {
            "previous_period": random.uniform(500, 1600),
            "change_percent": random.uniform(-15, 10)
        },
        "reduction_initiatives": [
            {"name": "Bike lanes expansion", "impact": "-5%"},
            {"name": "Electric bus fleet", "impact": "-8%"},
            {"name": "Carpooling program", "impact": "-3%"}
        ]
    }

@router.get("/kpi/dashboard")
async def get_kpi_dashboard():
    """Get key performance indicators for dashboard"""
    return {
        "timestamp": datetime.now().isoformat(),
        "mobility": {
            "average_commute_time": random.randint(25, 45),
            "public_transport_punctuality": random.uniform(85, 95),
            "bike_share_availability": random.uniform(70, 90),
            "parking_availability": random.uniform(20, 40)
        },
        "traffic": {
            "congestion_index": random.uniform(0.4, 0.8),
            "average_speed": random.uniform(30, 50),
            "incident_response_time": random.randint(5, 15),
            "traffic_flow_efficiency": random.uniform(60, 85)
        },
        "environment": {
            "air_quality_index": random.randint(40, 120),
            "co2_emissions_daily": random.uniform(100, 300),
            "green_transport_usage": random.uniform(30, 60),
            "energy_consumption": random.uniform(1000, 2000)
        },
        "citizen_satisfaction": {
            "overall_score": random.uniform(3.5, 4.5),
            "transport_satisfaction": random.uniform(3.0, 4.5),
            "safety_perception": random.uniform(3.5, 4.8),
            "service_accessibility": random.uniform(3.8, 4.7)
        }
    }

@router.post("/reports/generate")
async def generate_report(
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    zone_ids: Optional[List[str]] = None
):
    """Generate analytical reports"""
    report_id = f"report-{random.randint(1000, 9999)}"
    
    return APIResponse(
        success=True,
        data={
            "report_id": report_id,
            "type": report_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "zones": zone_ids or ["all"],
            "status": "generating",
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "format": "pdf",
            "size_estimate": f"{random.randint(500, 2000)} KB"
        }
    )
