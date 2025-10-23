from pydantic import BaseModel, Field
from typing import Optional, List


class LocationRequest(BaseModel):
    """Request model for location/navigation search."""
    query: str = Field(..., description="Search query (address, POI, etc.)")
    city: Optional[str] = Field(None, description="City to search in")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Forbidden City",
                "city": "Beijing"
            }
        }


class Location(BaseModel):
    """Location data model."""
    name: str
    address: str
    longitude: float
    latitude: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Forbidden City",
                "address": "4 Jingshan Front St, Dongcheng, Beijing",
                "longitude": 116.397026,
                "latitude": 39.918058
            }
        }


class RouteRequest(BaseModel):
    """Request model for route planning."""
    origin: str = Field(..., description="Starting point (address or coordinates)")
    destination: str = Field(..., description="Destination (address or coordinates)")
    mode: str = Field(default="transit", description="Travel mode: walking, transit, driving")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "Beijing Railway Station",
                "destination": "Forbidden City",
                "mode": "transit"
            }
        }


class RouteResponse(BaseModel):
    """Response model for route information."""
    distance: float = Field(..., description="Distance in kilometers")
    duration: float = Field(..., description="Duration in minutes")
    steps: List[str] = Field(..., description="Step-by-step directions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "distance": 3.5,
                "duration": 25.0,
                "steps": [
                    "Head north on Beijing Railway Station",
                    "Take subway line 2",
                    "Get off at Tiananmen East",
                    "Walk to Forbidden City"
                ]
            }
        }
