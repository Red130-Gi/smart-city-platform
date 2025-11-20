from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import sys
import os

# Try to import from ml-models if available, otherwise use fallback
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../ml-models'))
    from future_prediction import FutureTrafficPredictor
    from route_recommendation import RouteRecommendationSystem, Route
except ImportError:
    # Fallback implementations if ML modules not available
    FutureTrafficPredictor = None
    RouteRecommendationSystem = None
    Route = None
from database import get_mongodb, get_redis
import json
from datetime import datetime as dt

router = APIRouter()

# Initialize ML models
future_predictor = None
route_recommender = None

class FuturePredictionRequest(BaseModel):
    """Request model for future traffic prediction"""
    road: str = Field(..., description="Road or sensor ID")
    datetime: datetime = Field(..., description="Target datetime for prediction")
    
class FuturePredictionResponse(BaseModel):
    """Response model for future traffic prediction"""
    road_id: str
    target_datetime: str
    predicted_speed_kmh: float
    predicted_flow: Optional[float] = None
    predicted_density: Optional[float] = None
    congestion_level: str
    confidence: float
    prediction_horizon_hours: float
    model_used: str
    alternatives: Optional[List[str]] = None

class RouteRecommendationRequest(BaseModel):
    """Request model for route recommendation"""
    origin_lat: float = Field(..., description="Origin latitude")
    origin_lon: float = Field(..., description="Origin longitude")
    destination_lat: float = Field(..., description="Destination latitude")
    destination_lon: float = Field(..., description="Destination longitude")
    datetime: datetime = Field(..., description="Planned departure time")
    preferences: Optional[Dict] = Field(default=None, description="User preferences")
    max_routes: int = Field(default=3, ge=1, le=5, description="Maximum number of routes")

class RouteResponse(BaseModel):
    """Response model for a single route"""
    route_id: str
    roads: List[str]
    total_distance_km: float
    estimated_duration_minutes: float
    average_speed_kmh: float
    congestion_score: float
    congestion_level: str
    alternative_reason: Optional[str] = None
    waypoints: Optional[List[Dict]] = None
    segments: Optional[List[Dict]] = None

class RouteRecommendationResponse(BaseModel):
    """Response model for route recommendations"""
    origin: Dict
    destination: Dict
    departure_time: str
    routes: List[RouteResponse]
    best_route_id: str
    comparison: Optional[Dict] = None

def initialize_models():
    """Initialize ML models on startup"""
    global future_predictor, route_recommender
    
    try:
        if FutureTrafficPredictor is not None:
            # Initialize future predictor
            future_predictor = FutureTrafficPredictor(model_type='ensemble')
            
            # Try to load pre-trained models
            model_path = "/app/models/saved"
            if os.path.exists(model_path):
                future_predictor.load_models(model_path)
                print("Loaded pre-trained models")
            else:
                print("No pre-trained models found, using default initialization")
            
            # Initialize route recommender
            if RouteRecommendationSystem is not None:
                route_recommender = RouteRecommendationSystem(predictor=future_predictor)
            else:
                route_recommender = None
            
            # Load road network if available
            if route_recommender is not None:
                network_path = "/app/data/road_network.pkl"
                if os.path.exists(network_path):
                    import pickle
                    with open(network_path, 'rb') as f:
                        road_network_data = pickle.load(f)
                        route_recommender.build_road_network(road_network_data)
                        print("Loaded road network")
            
            print("Models initialized successfully")
        else:
            print("ML modules not available, using fallback mode")
            future_predictor = None
            route_recommender = None
        
    except Exception as e:
        print(f"Error initializing models: {e}")
        # Use fallback mode
        future_predictor = None
        route_recommender = None

# Initialize models on module load
initialize_models()

@router.post("/predict/future", response_model=FuturePredictionResponse)
async def predict_future_traffic(
    request: FuturePredictionRequest,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    mongodb=Depends(get_mongodb)
):
    """
    Predict future traffic conditions for a specific road and datetime
    
    This endpoint uses advanced ML models (LSTM, XGBoost, Prophet) to predict
    traffic conditions up to 7 days in the future.
    """
    try:
        # Check cache first
        cache_key = f"prediction:{request.road}:{request.datetime.isoformat()}"
        cached_result = await redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Perform prediction
        if future_predictor:
            prediction = future_predictor.predict_future(
                road_id=request.road,
                target_datetime=request.datetime
            )
            
            # Convert congestion score to level
            if 'congestion_level' not in prediction:
                if 'predicted_speed_kmh' in prediction:
                    speed = prediction['predicted_speed_kmh']
                    if speed >= 45:
                        congestion_level = 'low'
                    elif speed >= 30:
                        congestion_level = 'medium'
                    elif speed >= 15:
                        congestion_level = 'high'
                    else:
                        congestion_level = 'severe'
                else:
                    congestion_level = 'unknown'
            else:
                congestion_level = prediction['congestion_level']
            
            # Find alternative roads if congestion is high
            alternatives = None
            if congestion_level in ['high', 'severe']:
                alternatives = await get_alternative_roads(request.road, mongodb)
            
            response = FuturePredictionResponse(
                road_id=request.road,
                target_datetime=request.datetime.isoformat(),
                predicted_speed_kmh=prediction.get('predicted_speed_kmh', 30.0),
                predicted_flow=prediction.get('predicted_flow'),
                predicted_density=prediction.get('predicted_density'),
                congestion_level=congestion_level,
                confidence=prediction.get('confidence', 0.75),
                prediction_horizon_hours=prediction.get('prediction_horizon_hours', 0),
                model_used=prediction.get('model_used', 'ensemble'),
                alternatives=alternatives
            )
            
            # Cache result for 5 minutes
            await redis_client.setex(
                cache_key,
                300,
                response.model_dump_json()
            )
            
            # Log prediction to database in background
            background_tasks.add_task(
                log_prediction,
                mongodb,
                request.road,
                request.datetime,
                prediction
            )
            
            return response
            
        else:
            # Fallback prediction
            return FuturePredictionResponse(
                road_id=request.road,
                target_datetime=request.datetime.isoformat(),
                predicted_speed_kmh=35.0,
                congestion_level='medium',
                confidence=0.5,
                prediction_horizon_hours=(request.datetime - datetime.now()).total_seconds() / 3600,
                model_used='fallback',
                alternatives=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/predict/traffic")
async def predict_traffic_simple(
    road: str = Query(..., description="Road ID"),
    datetime: str = Query(..., description="Target datetime (ISO format)"),
    redis_client=Depends(get_redis)
):
    """
    Simple GET endpoint for traffic prediction (as specified in requirements)
    
    Example: GET /predict/traffic?road=X&datetime=2024-01-15T13:00:00
    """
    try:
        target_datetime = dt.fromisoformat(datetime.replace('Z', '+00:00'))
        
        # Create request object and call main prediction endpoint
        request = FuturePredictionRequest(
            road=road,
            datetime=target_datetime
        )
        
        # Use the main prediction logic
        if future_predictor:
            prediction = future_predictor.predict_future(
                road_id=road,
                target_datetime=target_datetime
            )
            
            return {
                "road": road,
                "datetime": datetime,
                "prediction": {
                    "speed_kmh": prediction.get('predicted_speed_kmh', 30.0),
                    "congestion": prediction.get('congestion_level', 'medium'),
                    "confidence": prediction.get('confidence', 0.75)
                },
                "status": "success"
            }
        else:
            return {
                "road": road,
                "datetime": datetime,
                "prediction": {
                    "speed_kmh": 35.0,
                    "congestion": "medium",
                    "confidence": 0.5
                },
                "status": "fallback"
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/recommend/routes", response_model=RouteRecommendationResponse)
async def recommend_routes(
    request: RouteRecommendationRequest,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    mongodb=Depends(get_mongodb)
):
    """
    Recommend optimal routes based on future traffic predictions
    
    This endpoint analyzes multiple routes and recommends the best options
    based on predicted traffic conditions at the planned departure time.
    """
    try:
        # Check cache
        cache_key = f"routes:{request.origin_lat}:{request.origin_lon}:{request.destination_lat}:{request.destination_lon}:{request.datetime.isoformat()}"
        cached_result = await redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Get route recommendations
        if route_recommender:
            routes = route_recommender.recommend_routes(
                origin=(request.origin_lat, request.origin_lon),
                destination=(request.destination_lat, request.destination_lon),
                target_datetime=request.datetime,
                max_routes=request.max_routes,
                preferences=request.preferences
            )
            
            # Convert routes to response format
            route_responses = []
            for route in routes:
                route_details = route_recommender.get_route_details(route)
                route_responses.append(RouteResponse(
                    route_id=route.route_id,
                    roads=route.roads,
                    total_distance_km=route.total_distance,
                    estimated_duration_minutes=route.estimated_duration,
                    average_speed_kmh=route.average_speed,
                    congestion_score=route.congestion_score,
                    congestion_level=_congestion_score_to_level(route.congestion_score),
                    alternative_reason=route.alternative_reason,
                    waypoints=[{'lat': wp[0], 'lon': wp[1]} for wp in route.waypoints] if route.waypoints else None,
                    segments=route_details.get('segments')
                ))
            
            # Create comparison
            comparison = None
            if len(routes) > 1:
                comparison_df = route_recommender.compare_routes(routes)
                comparison = comparison_df.to_dict('records')
            
            response = RouteRecommendationResponse(
                origin={'lat': request.origin_lat, 'lon': request.origin_lon},
                destination={'lat': request.destination_lat, 'lon': request.destination_lon},
                departure_time=request.datetime.isoformat(),
                routes=route_responses,
                best_route_id=route_responses[0].route_id if route_responses else "none",
                comparison=comparison
            )
            
            # Cache for 10 minutes
            await redis_client.setex(
                cache_key,
                600,
                response.model_dump_json()
            )
            
            # Log recommendation in background
            background_tasks.add_task(
                log_recommendation,
                mongodb,
                request,
                route_responses
            )
            
            return response
            
        else:
            # Fallback routes
            return _create_fallback_routes(request)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route recommendation error: {str(e)}")

@router.get("/recommend/route")
async def recommend_route_simple(
    origin: str = Query(..., description="Origin coordinates (lat,lon)"),
    destination: str = Query(..., description="Destination coordinates (lat,lon)"),
    datetime: str = Query(..., description="Departure datetime (ISO format)"),
    redis_client=Depends(get_redis)
):
    """
    Simple GET endpoint for route recommendation (as specified in requirements)
    
    Example: GET /recommend/route?origin=48.8566,2.3522&destination=48.8606,2.3376&datetime=2024-01-15T13:00:00
    """
    try:
        # Parse coordinates
        origin_parts = origin.split(',')
        dest_parts = destination.split(',')
        
        if len(origin_parts) != 2 or len(dest_parts) != 2:
            raise ValueError("Coordinates must be in format 'lat,lon'")
        
        origin_lat = float(origin_parts[0])
        origin_lon = float(origin_parts[1])
        dest_lat = float(dest_parts[0])
        dest_lon = float(dest_parts[1])
        target_datetime = dt.fromisoformat(datetime.replace('Z', '+00:00'))
        
        # Create request and call main endpoint
        request = RouteRecommendationRequest(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            destination_lat=dest_lat,
            destination_lon=dest_lon,
            datetime=target_datetime,
            max_routes=3
        )
        
        # Get recommendations
        if route_recommender:
            routes = route_recommender.recommend_routes(
                origin=(origin_lat, origin_lon),
                destination=(dest_lat, dest_lon),
                target_datetime=target_datetime,
                max_routes=3
            )
            
            # Format response
            route_list = []
            for route in routes:
                route_list.append({
                    "route_id": route.route_id,
                    "distance_km": round(route.total_distance, 1),
                    "duration_minutes": round(route.estimated_duration, 0),
                    "congestion": _congestion_score_to_level(route.congestion_score),
                    "reason": route.alternative_reason or "Primary route"
                })
            
            return {
                "origin": origin,
                "destination": destination,
                "datetime": datetime,
                "routes": route_list,
                "status": "success"
            }
        else:
            return {
                "origin": origin,
                "destination": destination,
                "datetime": datetime,
                "routes": [
                    {
                        "route_id": "route_1",
                        "distance_km": 5.2,
                        "duration_minutes": 15,
                        "congestion": "medium",
                        "reason": "Primary route"
                    }
                ],
                "status": "fallback"
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route recommendation error: {str(e)}")

@router.get("/forecast/{road_id}")
async def get_traffic_forecast(
    road_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Forecast horizon in hours"),
    interval: int = Query(default=1, ge=1, le=24, description="Interval between predictions in hours"),
    mongodb=Depends(get_mongodb),
    redis_client=Depends(get_redis)
):
    """
    Get traffic forecast for a specific road
    
    Returns predictions at regular intervals for the specified time horizon.
    """
    try:
        # Check cache
        cache_key = f"forecast:{road_id}:{hours}:{interval}"
        cached_result = await redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Generate forecast
        current_time = datetime.now()
        forecast_data = []
        
        for i in range(0, hours, interval):
            target_time = current_time + timedelta(hours=i)
            
            if future_predictor:
                prediction = future_predictor.predict_future(
                    road_id=road_id,
                    target_datetime=target_time
                )
                
                forecast_data.append({
                    "datetime": target_time.isoformat(),
                    "hours_ahead": i,
                    "predicted_speed_kmh": prediction.get('predicted_speed_kmh', 30.0),
                    "congestion_level": prediction.get('congestion_level', 'medium'),
                    "confidence": prediction.get('confidence', 0.75)
                })
            else:
                # Fallback forecast
                forecast_data.append({
                    "datetime": target_time.isoformat(),
                    "hours_ahead": i,
                    "predicted_speed_kmh": 35.0 + (i % 24 - 12) * 0.5,  # Simple variation
                    "congestion_level": "medium",
                    "confidence": 0.5
                })
        
        result = {
            "road_id": road_id,
            "forecast_start": current_time.isoformat(),
            "forecast_hours": hours,
            "interval_hours": interval,
            "predictions": forecast_data
        }
        
        # Cache for 30 minutes
        await redis_client.setex(
            cache_key,
            1800,
            json.dumps(result)
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

# Helper functions
def _congestion_score_to_level(score: float) -> str:
    """Convert congestion score to text level"""
    if score < 0.2:
        return "free"
    elif score < 0.4:
        return "light"
    elif score < 0.6:
        return "moderate"
    elif score < 0.8:
        return "heavy"
    else:
        return "severe"

def _create_fallback_routes(request: RouteRecommendationRequest) -> RouteRecommendationResponse:
    """Create fallback routes when recommender is unavailable"""
    routes = [
        RouteResponse(
            route_id="route_fallback_1",
            roads=["main_road"],
            total_distance_km=5.2,
            estimated_duration_minutes=15.0,
            average_speed_kmh=20.8,
            congestion_score=0.5,
            congestion_level="moderate",
            alternative_reason=None,
            waypoints=[
                {'lat': request.origin_lat, 'lon': request.origin_lon},
                {'lat': request.destination_lat, 'lon': request.destination_lon}
            ]
        ),
        RouteResponse(
            route_id="route_fallback_2",
            roads=["highway_1", "highway_2"],
            total_distance_km=6.8,
            estimated_duration_minutes=12.0,
            average_speed_kmh=34.0,
            congestion_score=0.3,
            congestion_level="light",
            alternative_reason="Faster travel time",
            waypoints=[
                {'lat': request.origin_lat, 'lon': request.origin_lon},
                {'lat': request.destination_lat, 'lon': request.destination_lon}
            ]
        )
    ]
    
    return RouteRecommendationResponse(
        origin={'lat': request.origin_lat, 'lon': request.origin_lon},
        destination={'lat': request.destination_lat, 'lon': request.destination_lon},
        departure_time=request.datetime.isoformat(),
        routes=routes,
        best_route_id="route_fallback_1",
        comparison=None
    )

async def get_alternative_roads(road_id: str, mongodb) -> List[str]:
    """Get alternative roads for a congested road"""
    # This would query the database for nearby alternative roads
    # For now, return sample alternatives
    return [f"alt_{road_id}_1", f"alt_{road_id}_2"]

async def log_prediction(mongodb, road_id: str, target_datetime: datetime, prediction: Dict):
    """Log prediction to database"""
    try:
        collection = mongodb.predictions
        await collection.insert_one({
            "road_id": road_id,
            "target_datetime": target_datetime,
            "prediction": prediction,
            "created_at": datetime.now()
        })
    except Exception as e:
        print(f"Error logging prediction: {e}")

async def log_recommendation(mongodb, request: RouteRecommendationRequest, routes: List[RouteResponse]):
    """Log route recommendation to database"""
    try:
        collection = mongodb.route_recommendations
        await collection.insert_one({
            "origin": {'lat': request.origin_lat, 'lon': request.origin_lon},
            "destination": {'lat': request.destination_lat, 'lon': request.destination_lon},
            "datetime": request.datetime,
            "routes": [route.model_dump() for route in routes],
            "created_at": datetime.now()
        })
    except Exception as e:
        print(f"Error logging recommendation: {e}")
