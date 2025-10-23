from typing import Optional, List
from datetime import datetime
from app.schemas.itinerary import ItineraryRequest, ItineraryResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseSummary
from app.services.llm_service import llm_service
from app.services.expense_service import expense_service
from app.core.database import get_supabase_client


class TravelService:
    """
    Main travel service that orchestrates all travel-related operations.
    
    This service provides a well-organized interface for:
    - Itinerary generation and management
    - Expense tracking
    - Travel planning coordination
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.itinerary_table = "itineraries"
    
    async def create_itinerary(
        self,
        user_id: str,
        request: ItineraryRequest
    ) -> ItineraryResponse:
        """
        Generate and save a personalized travel itinerary.
        
        Args:
            user_id: ID of the user requesting the itinerary
            request: Itinerary generation request with preferences
            
        Returns:
            Generated itinerary with daily plans
        """
        # Generate itinerary using LLM
        itinerary = await llm_service.generate_itinerary(request)
        
        # Save itinerary to database
        itinerary_data = {
            "user_id": user_id,
            "destination": itinerary.destination,
            "start_date": itinerary.start_date.isoformat(),
            "end_date": itinerary.end_date.isoformat(),
            "budget": itinerary.budget,
            "daily_itinerary": [day.model_dump() for day in itinerary.daily_itinerary],
            "total_estimated_cost": itinerary.total_estimated_cost,
            "recommendations": itinerary.recommendations,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table(self.itinerary_table).insert(itinerary_data).execute()
            if result.data:
                itinerary.id = result.data[0].get("id")
                itinerary.created_at = datetime.fromisoformat(result.data[0].get("created_at"))
        except Exception as e:
            print(f"Error saving itinerary: {e}")
            # Continue even if save fails - user still gets the generated itinerary
        
        return itinerary
    
    async def get_itinerary(self, itinerary_id: str, user_id: str) -> Optional[ItineraryResponse]:
        """
        Retrieve a saved itinerary.
        
        Args:
            itinerary_id: ID of the itinerary
            user_id: ID of the user (for authorization)
            
        Returns:
            Itinerary if found, None otherwise
        """
        try:
            result = self.supabase.table(self.itinerary_table)\
                .select("*")\
                .eq("id", itinerary_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if result.data:
                data = result.data[0]
                return ItineraryResponse(**data)
            return None
        except Exception as e:
            print(f"Error fetching itinerary: {e}")
            return None
    
    async def list_itineraries(self, user_id: str, limit: int = 20) -> List[ItineraryResponse]:
        """
        List all itineraries for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of itineraries to return
            
        Returns:
            List of itineraries
        """
        try:
            result = self.supabase.table(self.itinerary_table)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return [ItineraryResponse(**item) for item in result.data]
        except Exception as e:
            print(f"Error listing itineraries: {e}")
            return []
    
    async def delete_itinerary(self, itinerary_id: str, user_id: str) -> bool:
        """
        Delete an itinerary.
        
        Args:
            itinerary_id: ID of the itinerary to delete
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            result = self.supabase.table(self.itinerary_table)\
                .delete()\
                .eq("id", itinerary_id)\
                .eq("user_id", user_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting itinerary: {e}")
            return False
    
    async def track_expense(
        self,
        user_id: str,
        expense: ExpenseCreate
    ) -> ExpenseResponse:
        """
        Track a new travel expense.
        
        Args:
            user_id: User ID
            expense: Expense data
            
        Returns:
            Created expense record
        """
        return await expense_service.create_expense(user_id, expense)
    
    async def get_trip_expenses(
        self,
        user_id: str,
        itinerary_id: str
    ) -> List[ExpenseResponse]:
        """
        Get all expenses for a specific trip.
        
        Args:
            user_id: User ID
            itinerary_id: Itinerary ID
            
        Returns:
            List of expenses for the trip
        """
        return await expense_service.list_expenses(user_id, itinerary_id=itinerary_id)
    
    async def get_expense_summary(
        self,
        user_id: str,
        itinerary_id: Optional[str] = None
    ) -> ExpenseSummary:
        """
        Get expense summary with category breakdown.
        
        Args:
            user_id: User ID
            itinerary_id: Optional itinerary ID to filter by
            
        Returns:
            Expense summary with totals
        """
        return await expense_service.get_expense_summary(user_id, itinerary_id)
    
    async def get_budget_status(
        self,
        user_id: str,
        itinerary_id: str
    ) -> dict:
        """
        Get budget status for a trip (planned vs actual).
        
        Args:
            user_id: User ID
            itinerary_id: Itinerary ID
            
        Returns:
            Budget status with planned, spent, and remaining amounts
        """
        itinerary = await self.get_itinerary(itinerary_id, user_id)
        if not itinerary:
            return {
                "error": "Itinerary not found"
            }
        
        summary = await self.get_expense_summary(user_id, itinerary_id)
        
        planned_budget = itinerary.budget
        spent = summary.total_expenses
        remaining = planned_budget - spent
        
        return {
            "itinerary_id": itinerary_id,
            "planned_budget": planned_budget,
            "estimated_cost": itinerary.total_estimated_cost,
            "actual_spent": spent,
            "remaining": remaining,
            "spent_percentage": (spent / planned_budget * 100) if planned_budget > 0 else 0,
            "expense_breakdown": summary.by_category
        }


travel_service = TravelService()
