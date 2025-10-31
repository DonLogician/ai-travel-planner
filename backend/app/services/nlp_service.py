"""Utility service to interpret natural language itinerary requests."""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import List

from app.schemas.itinerary import (
    ItineraryRequest,
    ItineraryTextRequest,
    PreferenceType,
)

# Basic keyword mapping for preferences
_PREFERENCE_KEYWORDS = {
    PreferenceType.FOOD: ["美食", "吃", "餐饮"],
    PreferenceType.CULTURAL: ["文化", "历史", "博物馆"],
    PreferenceType.ADVENTURE: ["冒险", "徒步", "探险"],
    PreferenceType.RELAXATION: ["放松", "休闲", "度假", "spa"],
    PreferenceType.SHOPPING: ["购物", "买", "血拼"],
    PreferenceType.NATURE: ["自然", "公园", "山", "海"],
    PreferenceType.NIGHTLIFE: ["夜生活", "酒吧", "club", "夜店"],
}


class NaturalLanguageItineraryService:
    """Parse free-form text into structured itinerary requests."""

    def parse_text_request(
        self, text_request: ItineraryTextRequest
    ) -> ItineraryRequest:
        text = text_request.text.strip()
        duration_days = text_request.duration_days or self._extract_days(text) or 5
        start_date = text_request.start_date or (date.today() + timedelta(days=7))
        end_date = start_date + timedelta(days=duration_days - 1)
        budget = self._extract_budget(text) or 6000.0
        destination = self._extract_destination(text) or "理想目的地"
        preferences = self._extract_preferences(text)
        notes = self._extract_notes(text)

        return ItineraryRequest(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            preferences=preferences,
            additional_notes=notes,
        )

    def _extract_days(self, text: str) -> int | None:
        match = re.search(r"(\d{1,2})\s*天", text)
        if match:
            return max(int(match.group(1)), 1)
        return None

    def _extract_budget(self, text: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(万)?\s*元", text)
        if not match:
            return None
        amount = float(match.group(1))
        if match.group(2):
            amount *= 10000
        return amount

    def _extract_destination(self, text: str) -> str | None:
        match = re.search(
            r"(去|到)([\u4e00-\u9fa5A-Za-z\s]+?)(?:玩|旅游|旅行|出差|度假|[，。,!?])",
            text,
        )
        if match:
            candidate = match.group(2).strip()
            return candidate.replace(" ", "")
        return None

    def _extract_preferences(self, text: str) -> List[PreferenceType]:
        detected: List[PreferenceType] = []
        for preference, keywords in _PREFERENCE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                detected.append(preference)
        return detected

    def _extract_notes(self, text: str) -> str | None:
        keywords = ["孩子", "家庭", "朋友", "商务", "蜜月"]
        collected = [kw for kw in keywords if kw in text]
        if not collected:
            return None
        return "，".join(collected)


natural_language_service = NaturalLanguageItineraryService()
