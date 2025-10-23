from typing import Optional, List
import httpx
from app.schemas.location import (
    LocationRequest,
    Location,
    RouteRequest,
    RouteResponse
)
from app.core.config import settings


class NavigationService:
    """Service for location and navigation using Amap (高德地图) API."""
    
    def __init__(self):
        self.api_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def search_location(self, request: LocationRequest) -> List[Location]:
        """
        Search for locations using Amap Place Search API.
        
        Args:
            request: Location search request
            
        Returns:
            List of matching locations
        """
        if not self.api_key:
            # Return mock data if API key not configured
            return [
                Location(
                    name=request.query,
                    address=f"Sample address in {request.city or 'China'}",
                    longitude=116.397026,
                    latitude=39.918058
                )
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                # Amap Place Search API
                params = {
                    "key": self.api_key,
                    "keywords": request.query,
                    "types": "",  # All types
                    "city": request.city or "",
                    "output": "json"
                }
                
                response = await client.get(
                    f"{self.base_url}/place/text",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1" and data.get("pois"):
                        locations = []
                        for poi in data["pois"][:5]:  # Return top 5 results
                            location_parts = poi.get("location", "0,0").split(",")
                            locations.append(Location(
                                name=poi.get("name", ""),
                                address=poi.get("address", ""),
                                longitude=float(location_parts[0]),
                                latitude=float(location_parts[1])
                            ))
                        return locations
        except Exception as e:
            print(f"Error searching location: {e}")
        
        # Fallback
        return [
            Location(
                name=request.query,
                address=f"Location in {request.city or 'China'}",
                longitude=116.397026,
                latitude=39.918058
            )
        ]
    
    async def get_route(self, request: RouteRequest) -> RouteResponse:
        """
        Get route information using Amap Direction API.
        
        Args:
            request: Route request with origin and destination
            
        Returns:
            Route information with distance, duration, and steps
        """
        if not self.api_key:
            # Return mock route if API key not configured
            return RouteResponse(
                distance=5.0,
                duration=30.0,
                steps=[
                    f"Start from {request.origin}",
                    "Follow the suggested route",
                    f"Arrive at {request.destination}"
                ]
            )
        
        try:
            async with httpx.AsyncClient() as client:
                # Amap Direction API endpoint depends on mode
                endpoint = self._get_direction_endpoint(request.mode)
                
                params = {
                    "key": self.api_key,
                    "origin": request.origin,
                    "destination": request.destination,
                    "output": "json"
                }
                
                # Add mode-specific parameters
                if request.mode == "transit":
                    params["city"] = "beijing"  # Default city, should be dynamic
                    params["cityd"] = "beijing"
                
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return self._parse_route_response(data, request.mode)
        except Exception as e:
            print(f"Error getting route: {e}")
        
        # Fallback
        return RouteResponse(
            distance=5.0,
            duration=30.0,
            steps=[
                f"Start from {request.origin}",
                f"Travel via {request.mode}",
                f"Arrive at {request.destination}"
            ]
        )
    
    def _get_direction_endpoint(self, mode: str) -> str:
        """Get the appropriate Amap API endpoint for the travel mode."""
        endpoints = {
            "walking": "direction/walking",
            "transit": "direction/transit/integrated",
            "driving": "direction/driving"
        }
        return endpoints.get(mode, "direction/walking")
    
    def _parse_route_response(self, data: dict, mode: str) -> RouteResponse:
        """Parse Amap API response into RouteResponse."""
        try:
            if mode == "walking":
                route = data.get("route", {})
                paths = route.get("paths", [])
                if paths:
                    path = paths[0]
                    distance = float(path.get("distance", 0)) / 1000  # Convert to km
                    duration = float(path.get("duration", 0)) / 60  # Convert to minutes
                    
                    steps = []
                    for step in path.get("steps", []):
                        steps.append(step.get("instruction", ""))
                    
                    return RouteResponse(
                        distance=distance,
                        duration=duration,
                        steps=steps
                    )
            
            elif mode == "transit":
                route = data.get("route", {})
                transits = route.get("transits", [])
                if transits:
                    transit = transits[0]
                    distance = float(transit.get("distance", 0)) / 1000
                    duration = float(transit.get("duration", 0)) / 60
                    
                    steps = []
                    for segment in transit.get("segments", []):
                        walking = segment.get("walking", {})
                        if walking.get("steps"):
                            for step in walking["steps"]:
                                steps.append(step.get("instruction", ""))
                        
                        bus = segment.get("bus", {})
                        if bus.get("buslines"):
                            for busline in bus["buslines"]:
                                steps.append(f"Take {busline.get('name', 'transit')}")
                    
                    return RouteResponse(
                        distance=distance,
                        duration=duration,
                        steps=steps
                    )
            
            elif mode == "driving":
                route = data.get("route", {})
                paths = route.get("paths", [])
                if paths:
                    path = paths[0]
                    distance = float(path.get("distance", 0)) / 1000
                    duration = float(path.get("duration", 0)) / 60
                    
                    steps = []
                    for step in path.get("steps", []):
                        steps.append(step.get("instruction", ""))
                    
                    return RouteResponse(
                        distance=distance,
                        duration=duration,
                        steps=steps
                    )
        except Exception as e:
            print(f"Error parsing route: {e}")
        
        # Fallback
        return RouteResponse(
            distance=0.0,
            duration=0.0,
            steps=["Unable to parse route"]
        )


navigation_service = NavigationService()
