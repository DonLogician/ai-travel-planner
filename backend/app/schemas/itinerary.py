from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date as DateType, datetime
from enum import Enum


class PreferenceType(str, Enum):
    """Travel preference types."""

    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    FOOD = "food"
    SHOPPING = "shopping"
    NATURE = "nature"
    NIGHTLIFE = "nightlife"


class ItineraryRequest(BaseModel):
    """Request model for itinerary generation."""

    destination: str = Field(..., description="Destination city or location")
    start_date: DateType = Field(..., description="Trip start date")
    end_date: DateType = Field(..., description="Trip end date")
    budget: float = Field(..., gt=0, description="Total budget for the trip")
    preferences: List[PreferenceType] = Field(
        default=[], description="Travel preferences"
    )
    additional_notes: Optional[str] = Field(
        None, description="Additional user preferences or requirements"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Beijing",
                "start_date": "2024-03-15",
                "end_date": "2024-03-20",
                "budget": 5000.0,
                "preferences": ["cultural", "food"],
                "additional_notes": "Prefer public transportation",
            }
        }


class ActivityItem(BaseModel):
    """Individual activity in itinerary."""

    time: str = Field(..., description="Activity time")
    activity: str = Field(..., description="Activity description")
    location: str = Field(..., description="Activity location")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    notes: Optional[str] = Field(None, description="Additional notes")


class DayItinerary(BaseModel):
    """Itinerary for a single day."""

    day: int = Field(..., description="Day number")
    date: DateType = Field(..., description="Date")
    activities: List[ActivityItem] = Field(..., description="List of activities")
    total_estimated_cost: float = Field(
        0.0, description="Total estimated cost for the day"
    )


class ItineraryResponse(BaseModel):
    """Response model for generated itinerary."""

    id: Optional[str] = Field(None, description="Itinerary ID")
    destination: str
    start_date: DateType
    end_date: DateType
    budget: float
    daily_itinerary: List[DayItinerary] = Field(..., description="Day-by-day itinerary")
    total_estimated_cost: float = Field(..., description="Total estimated cost")
    recommendations: Optional[str] = Field(None, description="General recommendations")
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Beijing",
                "start_date": "2024-03-15",
                "end_date": "2024-03-17",
                "budget": 5000.0,
                "daily_itinerary": [
                    {
                        "day": 1,
                        "date": "2024-03-15",
                        "activities": [
                            {
                                "time": "09:00",
                                "activity": "Visit Forbidden City",
                                "location": "Forbidden City",
                                "estimated_cost": 60.0,
                                "notes": "Book tickets in advance",
                            }
                        ],
                        "total_estimated_cost": 500.0,
                    }
                ],
                "total_estimated_cost": 1500.0,
                "recommendations": "Use subway for transportation",
            }
        }


class ItineraryTextRequest(BaseModel):
    """Request model for natural language itinerary creation."""

    text: str = Field(..., min_length=5, description="Raw user description of the trip")
    language: str = Field(default="zh", description="Language code of the description")
    start_date: Optional[DateType] = Field(
        None, description="Optional explicit start date"
    )
    duration_days: Optional[int] = Field(
        None, description="Optional explicit duration in days"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "我想带孩子去东京玩 5 天，预算 8000 元，喜欢动漫和美食。",
                "language": "zh",
            }
        }


class ItineraryFromTextResponse(BaseModel):
    """Response model when generating an itinerary from free-form text."""

    itinerary: ItineraryResponse
    prompt: str = Field(..., description="LLM prompt used for generation")
    parsed_request: ItineraryRequest = Field(
        ..., description="Structured request parsed from text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "itinerary": {
                    "destination": "Tokyo",
                    "start_date": "2024-07-01",
                    "end_date": "2024-07-05",
                    "budget": 8000,
                    "daily_itinerary": [],
                    "total_estimated_cost": 7800,
                    "recommendations": "Book theme park tickets in advance",
                },
                "prompt": "Create a detailed 5-day travel itinerary for Tokyo...",
                "parsed_request": {
                    "destination": "Tokyo",
                    "start_date": "2024-07-01",
                    "end_date": "2024-07-05",
                    "budget": 8000,
                    "preferences": ["food", "cultural"],
                    "additional_notes": "Travelling with kids",
                },
            }
        }
