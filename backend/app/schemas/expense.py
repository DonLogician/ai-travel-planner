from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class ExpenseCategory(str, Enum):
    """Expense category types."""

    ACCOMMODATION = "accommodation"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ACTIVITIES = "activities"
    SHOPPING = "shopping"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    """Request model for creating an expense."""

    itinerary_id: str = Field(..., min_length=1, description="Associated itinerary ID")
    category: ExpenseCategory = Field(..., description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount")
    description: str = Field(..., description="Expense description")
    date: datetime = Field(default_factory=datetime.now, description="Expense date")
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "itinerary_id": "abc123",
                "category": "food",
                "amount": 120.5,
                "description": "Dinner at local restaurant",
            }
        },
    )


class ExpenseUpdate(BaseModel):
    """Request model for updating an expense."""

    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    itinerary_id: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class ExpenseResponse(BaseModel):
    """Response model for expense."""

    id: str
    user_id: str
    itinerary_id: Optional[str]
    category: ExpenseCategory
    amount: float
    description: str
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "id": "exp123",
                "user_id": "user456",
                "itinerary_id": "itin789",
                "category": "food",
                "amount": 120.5,
                "description": "Dinner at local restaurant",
                "date": "2024-03-15T19:30:00",
                "created_at": "2024-03-15T20:00:00",
            }
        },
    )


class ExpenseSummary(BaseModel):
    """Summary of expenses."""

    total_expenses: float
    by_category: dict[ExpenseCategory, float]
    count: int
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "total_expenses": 1500.0,
                "by_category": {
                    "food": 500.0,
                    "transportation": 300.0,
                    "accommodation": 600.0,
                    "activities": 100.0,
                },
                "count": 15,
            }
        },
    )
