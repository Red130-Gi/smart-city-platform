import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import networkx as nx
from geopy.distance import geodesic
import heapq
from future_prediction import FutureTrafficPredictor

@dataclass
class Route:
    """Route information structure"""
    route_id: str
    roads: List[str]
    total_distance: float
    estimated_duration: float
    congestion_score: float
    average_speed: float
    alternative_reason: Optional[str] = None
    waypoints: Optional[List[Tuple[float, float]]] = None

class RouteRecommendationSystem:
    """Intelligent route recommendation system based on future traffic predictions"""
    
    def __init__(self, predictor: Optional[FutureTrafficPredictor] = None):
        """
        Initialize the route recommendation system
        
        Args:
            predictor: Future traffic predictor instance
        """
        self.predictor = predictor or FutureTrafficPredictor()
        self.road_network = None
        self.road_metadata = {}
        self.historical_patterns = {}
        
    def build_road_network(self, roads_data: pd.DataFrame):
        """
        Build road network graph from data
        
        Args:
            roads_data: DataFrame with road information
        """
        self.road_network = nx.DiGraph()
        
        for _, road in roads_data.iterrows():
            # Add road segments as edges
            self.road_network.add_edge(
                road['start_junction'],
                road['end_junction'],
                road_id=road['road_id'],
                distance=road['distance_km'],
                speed_limit=road['speed_limit'],
                road_type=road.get('road_type', 'standard'),
                lanes=road.get('lanes', 2),
                capacity=road.get('capacity', 1000)
            )
            
            # Store metadata
            self.road_metadata[road['road_id']] = {
                'name': road.get('road_name', f"Road {road['road_id']}"),
                'type': road.get('road_type', 'standard'),
                'coordinates': {
                    'start': (road['start_lat'], road['start_lon']),
                    'end': (road['end_lat'], road['end_lon'])
                }
            }
    
    def recommend_routes(self,
                        origin: Tuple[float, float],
                        destination: Tuple[float, float],
                        target_datetime: datetime,
                        max_routes: int = 3,
                        preferences: Optional[Dict] = None) -> List[Route]:
        """
        Recommend optimal routes based on future traffic predictions
        
        Args:
            origin: Origin coordinates (lat, lon)
            destination: Destination coordinates (lat, lon)
            target_datetime: Planned departure time
            max_routes: Maximum number of routes to return
            preferences: User preferences (e.g., avoid_highways, prefer_scenic)
        
        Returns:
            List of recommended routes sorted by score
        """
        if self.road_network is None:
            return self._fallback_recommendations(origin, destination)
        
        # Find nearest nodes to origin and destination
        origin_node = self._find_nearest_node(origin)
        destination_node = self._find_nearest_node(destination)
        
        if origin_node is None or destination_node is None:
            return self._fallback_recommendations(origin, destination)
        
        # Find multiple candidate routes
        candidate_routes = self._find_candidate_routes(
            origin_node, 
            destination_node,
            k=max_routes * 2  # Find more candidates for scoring
        )
        
        # Score and rank routes based on future predictions
        scored_routes = []
        for route_path in candidate_routes:
            route = self._evaluate_route(route_path, target_datetime, preferences)
            if route:
                scored_routes.append(route)
        
        # Sort by combined score (lower is better)
        scored_routes.sort(key=lambda x: x.congestion_score * 0.4 + 
                                        x.estimated_duration * 0.4 + 
                                        x.total_distance * 0.2)
        
        # Mark alternative routes
        if len(scored_routes) > 1:
            best_route = scored_routes[0]
            for route in scored_routes[1:]:
                if route.congestion_score < best_route.congestion_score:
                    route.alternative_reason = "Lower congestion predicted"
                elif route.estimated_duration < best_route.estimated_duration:
                    route.alternative_reason = "Faster travel time"
                elif route.total_distance < best_route.total_distance:
                    route.alternative_reason = "Shorter distance"
                else:
                    route.alternative_reason = "Alternative route"
        
        return scored_routes[:max_routes]
    
    def _find_nearest_node(self, coordinates: Tuple[float, float]) -> Optional[str]:
        """Find nearest node in road network to given coordinates"""
        if not self.road_network.nodes():
            return None
        
        min_distance = float('inf')
        nearest_node = None
        
        for node in self.road_network.nodes():
            if 'pos' in self.road_network.nodes[node]:
                node_pos = self.road_network.nodes[node]['pos']
                distance = geodesic(coordinates, node_pos).kilometers
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node
        
        return nearest_node
    
    def _find_candidate_routes(self, origin: str, destination: str, k: int = 5) -> List[List[str]]:
        """Find k shortest/alternative paths between origin and destination"""
        try:
            # Find shortest path
            shortest_path = nx.shortest_path(
                self.road_network, 
                origin, 
                destination,
                weight='distance'
            )
            
            # Find alternative paths using different strategies
            paths = [shortest_path]
            
            # Try alternative weight functions
            for weight in ['travel_time', 'congestion']:
                try:
                    alt_path = nx.shortest_path(
                        self.road_network,
                        origin,
                        destination,
                        weight=weight
                    )
                    if alt_path not in paths:
                        paths.append(alt_path)
                except:
                    pass
            
            # Use k-shortest paths algorithm if available
            try:
                from networkx.algorithms import simple_paths
                k_paths = list(simple_paths.shortest_simple_paths(
                    self.road_network,
                    origin,
                    destination,
                    weight='distance'
                ))[:k]
                paths.extend([p for p in k_paths if p not in paths])
            except:
                pass
            
            return paths[:k]
        
        except nx.NetworkXNoPath:
            return []
    
    def _evaluate_route(self,
                       route_path: List[str],
                       target_datetime: datetime,
                       preferences: Optional[Dict] = None) -> Optional[Route]:
        """Evaluate a route based on future predictions and preferences"""
        if len(route_path) < 2:
            return None
        
        roads = []
        total_distance = 0
        estimated_duration = 0
        congestion_scores = []
        speeds = []
        current_time = target_datetime
        
        # Process each segment of the route
        for i in range(len(route_path) - 1):
            start_node = route_path[i]
            end_node = route_path[i + 1]
            
            # Get edge data
            edge_data = self.road_network.get_edge_data(start_node, end_node)
            if not edge_data:
                continue
            
            road_id = edge_data['road_id']
            distance = edge_data['distance']
            speed_limit = edge_data.get('speed_limit', 50)
            
            roads.append(road_id)
            total_distance += distance
            
            # Predict traffic conditions for this segment
            if self.predictor:
                prediction = self.predictor.predict_future(
                    road_id,
                    current_time
                )
                
                if 'predicted_speed_kmh' in prediction:
                    predicted_speed = prediction['predicted_speed_kmh']
                    congestion_score = self._calculate_congestion_score(
                        predicted_speed, 
                        speed_limit
                    )
                else:
                    predicted_speed = speed_limit * 0.7  # Default to 70% of speed limit
                    congestion_score = 0.3
            else:
                # Fallback if no predictor available
                predicted_speed = self._estimate_speed(road_id, current_time, speed_limit)
                congestion_score = self._calculate_congestion_score(
                    predicted_speed,
                    speed_limit
                )
            
            speeds.append(predicted_speed)
            congestion_scores.append(congestion_score)
            
            # Calculate time for this segment
            segment_duration = (distance / predicted_speed) * 60  # minutes
            estimated_duration += segment_duration
            current_time += timedelta(minutes=segment_duration)
        
        if not roads:
            return None
        
        # Calculate average metrics
        avg_congestion = np.mean(congestion_scores) if congestion_scores else 0.5
        avg_speed = np.mean(speeds) if speeds else 30
        
        # Apply preference modifiers
        if preferences:
            if preferences.get('avoid_highways') and self._has_highways(roads):
                avg_congestion += 0.1
            if preferences.get('prefer_scenic') and not self._is_scenic(roads):
                avg_congestion += 0.05
        
        # Create route object
        route = Route(
            route_id=f"route_{hash(tuple(roads)) % 10000}",
            roads=roads,
            total_distance=total_distance,
            estimated_duration=estimated_duration,
            congestion_score=avg_congestion,
            average_speed=avg_speed,
            waypoints=self._get_waypoints(route_path)
        )
        
        return route
    
    def _calculate_congestion_score(self, actual_speed: float, speed_limit: float) -> float:
        """Calculate congestion score (0=free flow, 1=severe congestion)"""
        speed_ratio = actual_speed / speed_limit
        
        if speed_ratio >= 0.9:
            return 0.0  # Free flow
        elif speed_ratio >= 0.7:
            return 0.3  # Light congestion
        elif speed_ratio >= 0.5:
            return 0.6  # Moderate congestion
        elif speed_ratio >= 0.3:
            return 0.8  # Heavy congestion
        else:
            return 1.0  # Severe congestion
    
    def _estimate_speed(self, road_id: str, datetime: datetime, speed_limit: float) -> float:
        """Estimate speed based on historical patterns when predictor unavailable"""
        hour = datetime.hour
        day_of_week = datetime.weekday()
        
        # Simple heuristic based on time patterns
        if day_of_week < 5:  # Weekday
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
                return speed_limit * 0.5
            elif 10 <= hour <= 16:  # Daytime
                return speed_limit * 0.75
            else:  # Night/early morning
                return speed_limit * 0.9
        else:  # Weekend
            if 10 <= hour <= 18:  # Daytime
                return speed_limit * 0.7
            else:
                return speed_limit * 0.85
    
    def _has_highways(self, roads: List[str]) -> bool:
        """Check if route contains highways"""
        for road_id in roads:
            if road_id in self.road_metadata:
                if self.road_metadata[road_id].get('type') == 'highway':
                    return True
        return False
    
    def _is_scenic(self, roads: List[str]) -> bool:
        """Check if route is scenic"""
        for road_id in roads:
            if road_id in self.road_metadata:
                if 'scenic' in self.road_metadata[road_id].get('tags', []):
                    return True
        return False
    
    def _get_waypoints(self, route_path: List[str]) -> List[Tuple[float, float]]:
        """Get waypoints for visualization"""
        waypoints = []
        for node in route_path:
            if 'pos' in self.road_network.nodes[node]:
                waypoints.append(self.road_network.nodes[node]['pos'])
        return waypoints
    
    def _fallback_recommendations(self, 
                                 origin: Tuple[float, float],
                                 destination: Tuple[float, float]) -> List[Route]:
        """Provide fallback recommendations when network unavailable"""
        # Calculate direct distance
        direct_distance = geodesic(origin, destination).kilometers
        
        # Generate sample routes
        routes = []
        
        # Route 1: Direct route
        routes.append(Route(
            route_id="direct_route",
            roads=["main_road"],
            total_distance=direct_distance * 1.2,
            estimated_duration=direct_distance * 2.5,  # Assume 24 km/h average
            congestion_score=0.5,
            average_speed=24,
            alternative_reason=None,
            waypoints=[origin, destination]
        ))
        
        # Route 2: Highway route
        routes.append(Route(
            route_id="highway_route",
            roads=["highway_1", "highway_2"],
            total_distance=direct_distance * 1.4,
            estimated_duration=direct_distance * 1.8,  # Faster but longer
            congestion_score=0.3,
            average_speed=35,
            alternative_reason="Faster travel time",
            waypoints=[origin, destination]
        ))
        
        # Route 3: Scenic route
        routes.append(Route(
            route_id="scenic_route",
            roads=["coastal_road", "park_avenue"],
            total_distance=direct_distance * 1.6,
            estimated_duration=direct_distance * 3.0,
            congestion_score=0.2,
            average_speed=20,
            alternative_reason="Less congested, scenic route",
            waypoints=[origin, destination]
        ))
        
        return routes
    
    def update_historical_patterns(self, traffic_data: pd.DataFrame):
        """Update historical traffic patterns for better predictions"""
        for road_id in traffic_data['road_id'].unique():
            road_data = traffic_data[traffic_data['road_id'] == road_id]
            
            # Calculate patterns by hour and day of week
            patterns = road_data.groupby(
                [road_data['timestamp'].dt.hour,
                 road_data['timestamp'].dt.dayofweek]
            )['speed_kmh'].agg(['mean', 'std']).reset_index()
            
            self.historical_patterns[road_id] = patterns
    
    def get_route_details(self, route: Route) -> Dict:
        """Get detailed information about a route"""
        details = {
            'route_id': route.route_id,
            'summary': {
                'distance': f"{route.total_distance:.1f} km",
                'duration': f"{route.estimated_duration:.0f} minutes",
                'average_speed': f"{route.average_speed:.1f} km/h",
                'congestion_level': self._congestion_to_text(route.congestion_score)
            },
            'segments': []
        }
        
        for road_id in route.roads:
            if road_id in self.road_metadata:
                metadata = self.road_metadata[road_id]
                details['segments'].append({
                    'road_id': road_id,
                    'name': metadata['name'],
                    'type': metadata.get('type', 'standard')
                })
            else:
                details['segments'].append({
                    'road_id': road_id,
                    'name': f"Road {road_id}",
                    'type': 'unknown'
                })
        
        if route.alternative_reason:
            details['recommendation_reason'] = route.alternative_reason
        
        if route.waypoints:
            details['waypoints'] = [
                {'lat': wp[0], 'lon': wp[1]} 
                for wp in route.waypoints
            ]
        
        return details
    
    def _congestion_to_text(self, congestion_score: float) -> str:
        """Convert congestion score to text description"""
        if congestion_score < 0.2:
            return "Free flow"
        elif congestion_score < 0.4:
            return "Light traffic"
        elif congestion_score < 0.6:
            return "Moderate traffic"
        elif congestion_score < 0.8:
            return "Heavy traffic"
        else:
            return "Severe congestion"
    
    def compare_routes(self, routes: List[Route]) -> pd.DataFrame:
        """Create comparison table of routes"""
        comparison_data = []
        
        for i, route in enumerate(routes):
            comparison_data.append({
                'Route': f"Route {i+1}",
                'Distance (km)': round(route.total_distance, 1),
                'Duration (min)': round(route.estimated_duration, 0),
                'Avg Speed (km/h)': round(route.average_speed, 1),
                'Congestion': self._congestion_to_text(route.congestion_score),
                'Reason': route.alternative_reason or "Primary route"
            })
        
        return pd.DataFrame(comparison_data)
