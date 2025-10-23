import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_itinerary():
    """Test itinerary creation endpoint."""
    itinerary_request = {
        "destination": "Beijing",
        "start_date": "2024-03-15",
        "end_date": "2024-03-17",
        "budget": 5000.0,
        "preferences": ["cultural", "food"],
        "additional_notes": "Prefer public transportation"
    }
    
    response = client.post("/api/itineraries/", json=itinerary_request)
    assert response.status_code == 201
    data = response.json()
    assert data["destination"] == "Beijing"
    assert "daily_itinerary" in data
    assert len(data["daily_itinerary"]) == 3  # 3 days


def test_expense_creation():
    """Test expense creation endpoint."""
    expense_data = {
        "category": "food",
        "amount": 120.5,
        "description": "Dinner at local restaurant",
        "location": "Beijing"
    }
    
    response = client.post("/api/expenses/", json=expense_data)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 120.5
    assert data["category"] == "food"


def test_location_search():
    """Test location search endpoint."""
    search_request = {
        "query": "Forbidden City",
        "city": "Beijing"
    }
    
    response = client.post("/api/navigation/search", json=search_request)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_route_planning():
    """Test route planning endpoint."""
    route_request = {
        "origin": "Beijing Railway Station",
        "destination": "Forbidden City",
        "mode": "transit"
    }
    
    response = client.post("/api/navigation/route", json=route_request)
    assert response.status_code == 200
    data = response.json()
    assert "distance" in data
    assert "duration" in data
    assert "steps" in data
