from typing import Optional, List
import json
from datetime import date, timedelta
from app.schemas.itinerary import (
    ItineraryRequest, 
    ItineraryResponse, 
    DayItinerary, 
    ActivityItem
)
from app.core.config import settings


class LLMService:
    """Service for Large Language Model interactions."""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
    async def generate_itinerary(self, request: ItineraryRequest) -> ItineraryResponse:
        """
        Generate personalized travel itinerary using LLM.
        
        Args:
            request: Itinerary generation request with user preferences
            
        Returns:
            Generated itinerary with daily plans
        """
        # Calculate number of days
        num_days = (request.end_date - request.start_date).days + 1
        
        # Create prompt for LLM
        prompt = self._create_itinerary_prompt(request, num_days)
        
        # Call appropriate LLM provider
        if self.provider == "qwen":
            itinerary_data = await self._generate_with_qwen(prompt, request)
        elif self.provider == "doubao":
            itinerary_data = await self._generate_with_doubao(prompt, request)
        else:
            itinerary_data = self._generate_fallback_itinerary(request, num_days)
        
        return itinerary_data
    
    def _create_itinerary_prompt(self, request: ItineraryRequest, num_days: int) -> str:
        """Create detailed prompt for LLM itinerary generation."""
        preferences_str = ", ".join(request.preferences) if request.preferences else "general sightseeing"
        
        prompt = f"""Create a detailed {num_days}-day travel itinerary for {request.destination}.

Trip Details:
- Destination: {request.destination}
- Duration: {request.start_date} to {request.end_date} ({num_days} days)
- Total Budget: ¥{request.budget}
- Preferences: {preferences_str}
{f'- Additional Notes: {request.additional_notes}' if request.additional_notes else ''}

Please provide a day-by-day itinerary in JSON format with the following structure:
{{
    "daily_itinerary": [
        {{
            "day": 1,
            "activities": [
                {{
                    "time": "09:00",
                    "activity": "Activity description",
                    "location": "Location name",
                    "estimated_cost": 100.0,
                    "notes": "Additional tips"
                }}
            ]
        }}
    ],
    "recommendations": "General tips and recommendations for the trip"
}}

Ensure activities are realistic, costs are reasonable, and the itinerary fits within the budget."""
        
        return prompt
    
    async def _generate_with_qwen(self, prompt: str, request: ItineraryRequest) -> ItineraryResponse:
        """Generate itinerary using Qwen (Alibaba Cloud) API."""
        # In a real implementation, this would call the Qwen API
        # For now, return a structured fallback response
        import httpx
        
        # Qwen API endpoint (example - adjust based on actual API)
        # This is a placeholder - actual implementation would need proper Qwen SDK
        try:
            async with httpx.AsyncClient() as client:
                # Placeholder for Qwen API call
                # response = await client.post(
                #     "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                #     headers={"Authorization": f"Bearer {settings.QWEN_API_KEY}"},
                #     json={"model": settings.QWEN_MODEL, "input": {"prompt": prompt}}
                # )
                pass
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
        
        # Fallback to structured generation
        num_days = (request.end_date - request.start_date).days + 1
        return self._generate_fallback_itinerary(request, num_days)
    
    async def _generate_with_doubao(self, prompt: str, request: ItineraryRequest) -> ItineraryResponse:
        """Generate itinerary using Doubao (ByteDance) API."""
        # In a real implementation, this would call the Doubao API
        # For now, return a structured fallback response
        import httpx
        
        # Doubao API endpoint (example - adjust based on actual API)
        try:
            async with httpx.AsyncClient() as client:
                # Placeholder for Doubao API call
                # response = await client.post(
                #     "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                #     headers={"Authorization": f"Bearer {settings.DOUBAO_API_KEY}"},
                #     json={"model": settings.DOUBAO_MODEL, "messages": [{"role": "user", "content": prompt}]}
                # )
                pass
        except Exception as e:
            print(f"Error calling Doubao API: {e}")
        
        # Fallback to structured generation
        num_days = (request.end_date - request.start_date).days + 1
        return self._generate_fallback_itinerary(request, num_days)
    
    def _generate_fallback_itinerary(self, request: ItineraryRequest, num_days: int) -> ItineraryResponse:
        """Generate a basic structured itinerary as fallback."""
        daily_itineraries = []
        daily_budget = request.budget / num_days
        
        for day in range(num_days):
            current_date = request.start_date + timedelta(days=day)
            
            # Create sample activities based on preferences
            activities = self._generate_day_activities(
                day + 1,
                request.destination,
                request.preferences,
                daily_budget
            )
            
            day_cost = sum(act.estimated_cost or 0 for act in activities)
            
            daily_itineraries.append(DayItinerary(
                day=day + 1,
                date=current_date,
                activities=activities,
                total_estimated_cost=day_cost
            ))
        
        total_cost = sum(d.total_estimated_cost for d in daily_itineraries)
        
        return ItineraryResponse(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            daily_itinerary=daily_itineraries,
            total_estimated_cost=total_cost,
            recommendations=self._generate_recommendations(request)
        )
    
    def _generate_day_activities(
        self, 
        day: int, 
        destination: str, 
        preferences: List[str],
        daily_budget: float
    ) -> List[ActivityItem]:
        """Generate sample activities for a day."""
        activities = [
            ActivityItem(
                time="09:00",
                activity=f"Morning exploration in {destination}",
                location=f"{destination} city center",
                estimated_cost=daily_budget * 0.15,
                notes="Start early to avoid crowds"
            ),
            ActivityItem(
                time="12:00",
                activity="Lunch at local restaurant",
                location=f"Local restaurant in {destination}",
                estimated_cost=daily_budget * 0.20,
                notes="Try local specialties"
            ),
            ActivityItem(
                time="14:00",
                activity=f"Visit popular attraction",
                location=f"Main attraction in {destination}",
                estimated_cost=daily_budget * 0.25,
                notes="Book tickets in advance if possible"
            ),
            ActivityItem(
                time="18:00",
                activity="Evening leisure and dinner",
                location=f"{destination} downtown",
                estimated_cost=daily_budget * 0.30,
                notes="Enjoy local cuisine and nightlife"
            )
        ]
        
        return activities
    
    def _generate_recommendations(self, request: ItineraryRequest) -> str:
        """Generate general recommendations for the trip."""
        recs = [
            f"For traveling in {request.destination}, consider using public transportation to save costs.",
            "Book accommodations and major attractions in advance for better prices.",
            "Keep some emergency funds separate from your daily budget.",
            "Download offline maps for easier navigation.",
        ]
        
        if "food" in request.preferences:
            recs.append("Explore local food markets for authentic cuisine at lower prices.")
        if "cultural" in request.preferences:
            recs.append("Many museums offer free admission on certain days.")
        
        return " ".join(recs)


llm_service = LLMService()
