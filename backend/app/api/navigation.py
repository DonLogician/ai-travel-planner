from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.location import (
    LocationRequest,
    Location,
    RouteRequest,
    RouteResponse
)
from app.services.navigation_service import navigation_service

router = APIRouter(prefix="/navigation", tags=["Navigation"])


@router.post("/search", response_model=List[Location])
async def search_location(request: LocationRequest):
    """
    Search for locations using Amap API.
    
    Returns a list of matching locations with coordinates.
    """
    try:
        locations = await navigation_service.search_location(request)
        return locations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching location: {str(e)}"
        )


@router.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    """
    Get route information between two locations using Amap API.
    
    Supports different travel modes: walking, transit, driving.
    """
    try:
        route = await navigation_service.get_route(request)
        return route
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting route: {str(e)}"
        )
