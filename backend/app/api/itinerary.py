from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.itinerary import ItineraryRequest, ItineraryResponse
from app.services.travel_service import travel_service

router = APIRouter(prefix="/itineraries", tags=["Itineraries"])


# Mock authentication dependency (replace with real auth)
async def get_current_user_id() -> str:
    """Mock function to get current user ID. Replace with real authentication."""
    return "user_123"


@router.post("/", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
async def create_itinerary(
    request: ItineraryRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate a personalized travel itinerary based on user preferences.
    
    This endpoint uses AI (Qwen or Doubao) to create a detailed day-by-day
    itinerary including activities, locations, and estimated costs.
    """
    try:
        itinerary = await travel_service.create_itinerary(user_id, request)
        return itinerary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating itinerary: {str(e)}"
        )


@router.get("/", response_model=List[ItineraryResponse])
async def list_itineraries(
    limit: int = 20,
    user_id: str = Depends(get_current_user_id)
):
    """
    List all itineraries for the current user.
    """
    try:
        itineraries = await travel_service.list_itineraries(user_id, limit)
        return itineraries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching itineraries: {str(e)}"
        )


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific itinerary by ID.
    """
    itinerary = await travel_service.get_itinerary(itinerary_id, user_id)
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return itinerary


@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete an itinerary.
    """
    success = await travel_service.delete_itinerary(itinerary_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found or could not be deleted"
        )
    return None


@router.get("/{itinerary_id}/budget-status")
async def get_budget_status(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get budget status for a trip (planned vs actual spending).
    """
    try:
        status_data = await travel_service.get_budget_status(user_id, itinerary_id)
        if "error" in status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_data["error"]
            )
        return status_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting budget status: {str(e)}"
        )
