import json
import re
from typing import Optional, List
from datetime import timedelta

import httpx
from pydantic import ValidationError
from app.schemas.itinerary import (
    ItineraryRequest,
    ItineraryResponse,
    DayItinerary,
    ActivityItem,
)
from app.core.config import settings


class LLMService:
    """Service for Large Language Model interactions."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER

    async def generate_itinerary(
        self, request: ItineraryRequest, prompt: Optional[str] = None
    ) -> ItineraryResponse:
        """
        Generate personalized travel itinerary using LLM.

        Args:
            request: Itinerary generation request with user preferences

        Returns:
            Generated itinerary with daily plans
        """
        # Calculate number of days
        num_days = (request.end_date - request.start_date).days + 1

        # Create prompt for LLM if not provided
        prompt = prompt or self.create_itinerary_prompt(request)

        # Call appropriate LLM provider
        if self.provider == "qwen":
            itinerary_data = await self._generate_with_qwen(prompt, request)
        elif self.provider == "doubao":
            itinerary_data = await self._generate_with_doubao(prompt, request)
        else:
            itinerary_data = self._generate_fallback_itinerary(request, num_days)

        return itinerary_data

    def create_itinerary_prompt(
        self, request: ItineraryRequest, user_description: Optional[str] = None
    ) -> str:
        """Create detailed prompt for LLM itinerary generation."""
        num_days = (request.end_date - request.start_date).days + 1
        preferences_str = (
            ", ".join(request.preferences)
            if request.preferences
            else "general sightseeing"
        )

        prompt = f"""
        
{user_description.strip() if user_description else 'None'}

请按照以下JSON格式提供每天的行程（注意，一定要包含所有字段，尤其是location_address和is_sightseeing）：
{{
    "destination": "北京",
    "budget": 7000,
    "daily_itinerary": [
        {{
            "day": 1,
            "activities": [
                {{
                    "time": "09:00",
                    "activity": "参观天安门广场",
                    "location": "天安门广场",
                    "location_address": "北京市东城区东长安街",
                    "is_sightseeing": true,
                    "estimated_cost": 0.0,
                    "notes": "免费参观，建议早上去人少"
                }}
            ]
        }}
    ],
    "recommendations": "一些旅行建议",
}}
确保返回的内容是有效的JSON格式，且符合上述结构，所有的键和键值都必须包含。

仅回复有效的JSON，禁用markdown，禁用小标题，禁用分点。
"""

        return prompt

    async def _generate_with_qwen(
        self, prompt: str, request: ItineraryRequest
    ) -> ItineraryResponse:
        """Generate itinerary using Qwen (Alibaba Cloud) API."""
        num_days = (request.end_date - request.start_date).days + 1

        if not settings.QWEN_API_KEY:
            print("Qwen API key not configured, using fallback itinerary.")
            return self._generate_fallback_itinerary(request, num_days)

        endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {settings.QWEN_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.QWEN_MODEL or "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个旅行规划师，帮助用户制定个性化的旅行行程。",
                    },
                    {"role": "user", "content": prompt},
                ]
            },
            "parameters": {
                "result_format": "json",
            },
        }

        raw_content: Optional[str] = None
        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                raw_content = (
                    result.get("output", {}).get("text")
                    or result.get("output", {})
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
                    or result.get("choices", [{}])[0].get("message", {}).get("content")
                )
        except httpx.HTTPError as exc:
            print(f"Error calling Qwen API: {exc}")
        except Exception as exc:  # pragma: no cover - defensive guard
            print(f"Unexpected error calling Qwen API: {exc}")

        itinerary = self._parse_llm_itinerary_response(raw_content, request)
        if itinerary:
            return itinerary

        print("Falling back to template itinerary due to invalid LLM response.")
        return self._generate_fallback_itinerary(request, num_days)

    async def _generate_with_doubao(
        self, prompt: str, request: ItineraryRequest
    ) -> ItineraryResponse:
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

    def _generate_fallback_itinerary(
        self, request: ItineraryRequest, num_days: int
    ) -> ItineraryResponse:
        """Generate a basic structured itinerary as fallback."""
        daily_itineraries = []
        daily_budget = request.budget / num_days

        for day in range(num_days):
            current_date = request.start_date + timedelta(days=day)

            # Create sample activities based on preferences
            activities = self._generate_day_activities(
                day + 1, request.destination, request.preferences, daily_budget
            )

            day_cost = sum(act.estimated_cost or 0 for act in activities)

            daily_itineraries.append(
                DayItinerary(
                    day=day + 1,
                    date=current_date,
                    activities=activities,
                    total_estimated_cost=day_cost,
                )
            )

        total_cost = sum(d.total_estimated_cost for d in daily_itineraries)

        return ItineraryResponse(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            daily_itinerary=daily_itineraries,
            total_estimated_cost=total_cost,
            recommendations=self._generate_recommendations(request),
        )

    def _generate_day_activities(
        self, day: int, destination: str, preferences: List[str], daily_budget: float
    ) -> List[ActivityItem]:
        """Generate sample activities for a day."""
        activities = [
            ActivityItem(
                time="09:00",
                activity=f"Morning exploration in {destination}",
                location=f"{destination} city center",
                location_address=None,
                is_sightseeing=True,
                estimated_cost=daily_budget * 0.15,
                notes="Start early to avoid crowds",
            ),
            ActivityItem(
                time="12:00",
                activity="Lunch at local restaurant",
                location=f"Local restaurant in {destination}",
                location_address=None,
                is_sightseeing=False,
                estimated_cost=daily_budget * 0.20,
                notes="Try local specialties",
            ),
            ActivityItem(
                time="14:00",
                activity=f"Visit popular attraction",
                location=f"Main attraction in {destination}",
                location_address=None,
                is_sightseeing=True,
                estimated_cost=daily_budget * 0.25,
                notes="Book tickets in advance if possible",
            ),
            ActivityItem(
                time="18:00",
                activity="Evening leisure and dinner",
                location=f"{destination} downtown",
                location_address=None,
                is_sightseeing=False,
                estimated_cost=daily_budget * 0.30,
                notes="Enjoy local cuisine and nightlife",
            ),
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
            recs.append(
                "Explore local food markets for authentic cuisine at lower prices."
            )
        if "cultural" in request.preferences:
            recs.append("Many museums offer free admission on certain days.")

        return " ".join(recs)

    def _parse_llm_itinerary_response(
        self, raw_content: Optional[str], request: ItineraryRequest
    ) -> Optional[ItineraryResponse]:
        """Try to convert LLM output into an ItineraryResponse."""

        if not raw_content:
            return None

        if isinstance(raw_content, list):
            parts = []
            for segment in raw_content:
                if isinstance(segment, dict):
                    if segment.get("text"):
                        parts.append(str(segment["text"]))
                    elif isinstance(segment.get("content"), str):
                        parts.append(segment["content"])
                    else:
                        parts.append(str(segment))
                else:
                    parts.append(str(segment))
            raw_content = "".join(parts)

        if not isinstance(raw_content, str):
            return None

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_content, re.S)
            if not match:
                return None
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return None

        if not isinstance(data, dict):
            return None

        destination_value = data.get("destination")
        if isinstance(destination_value, str):
            destination_value = destination_value.strip()
        elif isinstance(destination_value, list):
            joined = " ".join(str(item).strip() for item in destination_value if item)
            destination_value = joined.strip() if joined else None
        elif destination_value is not None:
            destination_value = str(destination_value).strip()

        data["destination"] = destination_value or request.destination
        data.setdefault("start_date", request.start_date.isoformat())
        data.setdefault("end_date", request.end_date.isoformat())
        data["budget"] = (
            self._coerce_currency_value(data.get("budget", request.budget))
            or request.budget
        )

        daily = data.get("daily_itinerary")
        if not isinstance(daily, list):
            return None

        normalized_days = []
        for index, day in enumerate(daily):
            if not isinstance(day, dict):
                continue
            normalized = dict(day)
            normalized.setdefault("day", day.get("day") or index + 1)
            if not normalized.get("date"):
                normalized["date"] = (
                    request.start_date + timedelta(days=index)
                ).isoformat()

            activities = normalized.get("activities") or []
            if isinstance(activities, dict):
                activities = [activities]
            normalized_activities = []
            for activity in activities:
                if not isinstance(activity, dict):
                    continue

                normalized_activity = dict(activity)

                for text_field in ("time", "activity", "location", "notes"):
                    value = normalized_activity.get(text_field)
                    coerced = self._coerce_text(value)
                    if coerced is not None:
                        normalized_activity[text_field] = coerced
                    elif text_field in normalized_activity:
                        normalized_activity[text_field] = value

                estimated = normalized_activity.get("estimated_cost")
                normalized_activity["estimated_cost"] = self._coerce_currency_value(
                    estimated
                )

                coerced_address = self._coerce_text(
                    normalized_activity.get("location_address")
                )
                normalized_activity["location_address"] = coerced_address

                sightseeing_value = self._coerce_bool(
                    normalized_activity.get("is_sightseeing")
                )
                normalized_activity["is_sightseeing"] = sightseeing_value

                normalized_activities.append(normalized_activity)
            normalized["activities"] = normalized_activities

            if (
                "total_estimated_cost" not in normalized
                or normalized["total_estimated_cost"] is None
            ):
                normalized["total_estimated_cost"] = sum(
                    (activity.get("estimated_cost") or 0)
                    for activity in normalized_activities
                )
            else:
                normalized["total_estimated_cost"] = (
                    self._coerce_currency_value(normalized.get("total_estimated_cost"))
                    or 0
                )

            normalized_days.append(normalized)

        if not normalized_days:
            return None

        data["daily_itinerary"] = normalized_days

        if not data.get("total_estimated_cost"):
            data["total_estimated_cost"] = sum(
                (self._coerce_currency_value(day.get("total_estimated_cost")) or 0)
                for day in normalized_days
            )
        else:
            data["total_estimated_cost"] = (
                self._coerce_currency_value(data.get("total_estimated_cost")) or 0
            )

        try:
            return ItineraryResponse(**data)
        except ValidationError as exc:
            print(f"LLM response validation error: {exc}")
            return None

    def _coerce_currency_value(self, value) -> Optional[float]:
        """Convert various currency formats into float."""

        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            cleaned = value.strip()
            cleaned = cleaned.replace("￥", "").replace("¥", "")
            cleaned = cleaned.replace(",", "")
            match = re.search(r"(-?\d+(?:\.\d+)?)", cleaned)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    return None

        return None

    def _coerce_text(self, value) -> Optional[str]:
        """Normalize textual fields from LLM output."""

        if value is None:
            return None

        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None

        if isinstance(value, (int, float)):
            return str(value)

        if isinstance(value, list):
            joined = " ".join(str(item).strip() for item in value if item)
            return joined.strip() or None

        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)

        return str(value).strip() or None

    def _coerce_bool(self, value) -> Optional[bool]:
        """Attempt to normalize boolean-like values."""

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "y", "1", "是", "ok"}:
                return True
            if lowered in {"false", "no", "n", "0", "否"}:
                return False

        return None


llm_service = LLMService()
