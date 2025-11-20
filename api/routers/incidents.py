from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from models.schemas import Incident, IncidentSeverity, APIResponse
from database import get_mongodb
import random
import uuid

router = APIRouter()

@router.get("/active", response_model=List[Incident])
async def get_active_incidents(
    severity: Optional[IncidentSeverity] = None,
    zone_id: Optional[str] = None,
    incident_type: Optional[str] = None
):
    """Get all active incidents"""
    incidents = []
    
    # Generate some sample incidents
    incident_types = ["accident", "breakdown", "roadwork", "event", "flooding"]
    
    for i in range(random.randint(2, 8)):
        incident = Incident(
            incident_id=str(uuid.uuid4()),
            timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120)),
            type=incident_type or random.choice(incident_types),
            severity=severity or random.choice(list(IncidentSeverity)),
            location={
                "road_id": f"road-{random.randint(1,5)}",
                "road_name": f"Route {random.randint(1,10)}",
                "zone_id": zone_id or f"zone-{random.randint(1,5)}",
                "lat": 48.8566 + random.uniform(-0.1, 0.1),
                "lon": 2.3522 + random.uniform(-0.1, 0.1)
            },
            description=f"Incident on road - {random.choice(incident_types)}",
            estimated_duration_min=random.randint(15, 180),
            affected_lanes=random.randint(1, 2),
            status="active"
        )
        incidents.append(incident)
    
    return incidents

@router.post("/report")
async def report_incident(
    incident_type: str,
    lat: float,
    lon: float,
    description: str,
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
):
    """Report a new incident"""
    incident_id = str(uuid.uuid4())
    
    incident = {
        "incident_id": incident_id,
        "timestamp": datetime.now().isoformat(),
        "type": incident_type,
        "severity": severity,
        "location": {
            "lat": lat,
            "lon": lon,
            "zone_id": f"zone-{random.randint(1,5)}"
        },
        "description": description,
        "reported_by": "citizen",
        "status": "reported",
        "verification_status": "pending"
    }
    
    return APIResponse(
        success=True,
        data=incident
    )

@router.get("/{incident_id}")
async def get_incident_details(incident_id: str):
    """Get detailed information about a specific incident"""
    return {
        "incident_id": incident_id,
        "timestamp": datetime.now().isoformat(),
        "type": "accident",
        "severity": "high",
        "location": {
            "road_id": "road-1",
            "road_name": "Avenue Principale",
            "zone_id": "zone-1",
            "lat": 48.8566,
            "lon": 2.3522,
            "address": "123 Avenue Principale"
        },
        "description": "Multi-vehicle collision blocking 2 lanes",
        "estimated_duration_min": 60,
        "affected_lanes": 2,
        "total_lanes": 3,
        "status": "active",
        "response_teams": [
            {"type": "police", "status": "on_scene"},
            {"type": "ambulance", "status": "on_scene"},
            {"type": "tow_truck", "status": "en_route"}
        ],
        "traffic_impact": {
            "congestion_increase": "40%",
            "average_delay_min": 15,
            "affected_routes": ["route-1", "route-2"]
        },
        "updates": [
            {
                "timestamp": datetime.now().isoformat(),
                "message": "Emergency services on scene"
            }
        ]
    }

@router.patch("/{incident_id}/update")
async def update_incident(
    incident_id: str,
    status: Optional[str] = None,
    severity: Optional[IncidentSeverity] = None,
    estimated_duration_min: Optional[int] = None
):
    """Update incident information"""
    updates = {}
    
    if status:
        updates["status"] = status
    if severity:
        updates["severity"] = severity
    if estimated_duration_min:
        updates["estimated_duration_min"] = estimated_duration_min
    
    updates["last_updated"] = datetime.now().isoformat()
    
    return APIResponse(
        success=True,
        data={
            "incident_id": incident_id,
            "updates": updates,
            "message": "Incident updated successfully"
        }
    )

@router.get("/statistics/summary")
async def get_incident_statistics(
    start_date: datetime = Query(default=datetime.now() - timedelta(days=30)),
    end_date: datetime = Query(default=datetime.now())
):
    """Get incident statistics for a time period"""
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_incidents": random.randint(50, 200),
        "by_type": {
            "accident": random.randint(20, 60),
            "breakdown": random.randint(30, 70),
            "roadwork": random.randint(10, 30),
            "event": random.randint(5, 15),
            "flooding": random.randint(2, 8),
            "other": random.randint(5, 20)
        },
        "by_severity": {
            "low": random.randint(60, 100),
            "medium": random.randint(30, 60),
            "high": random.randint(10, 30),
            "critical": random.randint(2, 10)
        },
        "average_resolution_time_min": random.randint(30, 90),
        "peak_incident_hour": random.randint(7, 19),
        "most_affected_zones": [
            {"zone_id": "zone-1", "count": random.randint(20, 50)},
            {"zone_id": "zone-2", "count": random.randint(15, 40)},
            {"zone_id": "zone-3", "count": random.randint(10, 30)}
        ]
    }

@router.get("/heatmap")
async def get_incident_heatmap():
    """Get incident heatmap data for visualization"""
    points = []
    
    for _ in range(random.randint(20, 50)):
        points.append({
            "lat": 48.8566 + random.uniform(-0.1, 0.1),
            "lon": 2.3522 + random.uniform(-0.1, 0.1),
            "intensity": random.uniform(0.3, 1.0),
            "type": random.choice(["accident", "breakdown", "roadwork"])
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "points": points,
        "total_incidents": len(points),
        "time_window_hours": 24
    }

@router.post("/alert/subscribe")
async def subscribe_to_alerts(
    user_id: str,
    zone_ids: List[str],
    incident_types: List[str],
    severity_threshold: IncidentSeverity = IncidentSeverity.MEDIUM
):
    """Subscribe to incident alerts for specific zones"""
    subscription_id = str(uuid.uuid4())
    
    return APIResponse(
        success=True,
        data={
            "subscription_id": subscription_id,
            "user_id": user_id,
            "zones": zone_ids,
            "incident_types": incident_types,
            "severity_threshold": severity_threshold,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
    )
