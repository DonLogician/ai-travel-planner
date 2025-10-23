# API Documentation

## Base URL

```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## Authentication

Currently using mock authentication. In production, all endpoints (except health check) should require JWT authentication.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

## Endpoints

### Health Check

#### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "app": "AI Travel Planner",
  "version": "1.0.0"
}
```

---

## Itinerary Endpoints

### Create Itinerary

#### POST /itineraries/

Generate a new AI-powered travel itinerary.

**Request Body:**
```json
{
  "destination": "Beijing",
  "start_date": "2024-03-15",
  "end_date": "2024-03-20",
  "budget": 5000.0,
  "preferences": ["cultural", "food"],
  "additional_notes": "Prefer public transportation"
}
```

**Parameters:**
- `destination` (string, required): Destination city or location
- `start_date` (date, required): Trip start date (YYYY-MM-DD)
- `end_date` (date, required): Trip end date (YYYY-MM-DD)
- `budget` (number, required): Total budget for the trip
- `preferences` (array, optional): Travel preferences (cultural, adventure, relaxation, food, shopping, nature, nightlife)
- `additional_notes` (string, optional): Additional user requirements

**Response:** `201 Created`
```json
{
  "id": "uuid-string",
  "destination": "Beijing",
  "start_date": "2024-03-15",
  "end_date": "2024-03-20",
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
          "notes": "Book tickets in advance"
        }
      ],
      "total_estimated_cost": 500.0
    }
  ],
  "total_estimated_cost": 2500.0,
  "recommendations": "Use subway for transportation. Book accommodations in advance.",
  "created_at": "2024-03-01T10:00:00"
}
```

### List Itineraries

#### GET /itineraries/

Get all itineraries for the current user.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of results (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "destination": "Beijing",
    "start_date": "2024-03-15",
    "end_date": "2024-03-20",
    "budget": 5000.0,
    "daily_itinerary": [...],
    "total_estimated_cost": 2500.0,
    "created_at": "2024-03-01T10:00:00"
  }
]
```

### Get Itinerary

#### GET /itineraries/{id}

Get a specific itinerary by ID.

**Path Parameters:**
- `id` (string, required): Itinerary UUID

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "destination": "Beijing",
  "start_date": "2024-03-15",
  "end_date": "2024-03-20",
  "budget": 5000.0,
  "daily_itinerary": [...],
  "total_estimated_cost": 2500.0,
  "recommendations": "...",
  "created_at": "2024-03-01T10:00:00"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Itinerary not found"
}
```

### Delete Itinerary

#### DELETE /itineraries/{id}

Delete an itinerary.

**Path Parameters:**
- `id` (string, required): Itinerary UUID

**Response:** `204 No Content`

**Error Response:** `404 Not Found`

### Get Budget Status

#### GET /itineraries/{id}/budget-status

Get budget status comparison (planned vs actual).

**Path Parameters:**
- `id` (string, required): Itinerary UUID

**Response:** `200 OK`
```json
{
  "itinerary_id": "uuid-string",
  "planned_budget": 5000.0,
  "estimated_cost": 2500.0,
  "actual_spent": 1200.0,
  "remaining": 3800.0,
  "spent_percentage": 24.0,
  "expense_breakdown": {
    "food": 500.0,
    "transportation": 300.0,
    "accommodation": 400.0
  }
}
```

---

## Expense Endpoints

### Create Expense

#### POST /expenses/

Create a new expense record.

**Request Body:**
```json
{
  "itinerary_id": "uuid-string",
  "category": "food",
  "amount": 120.5,
  "description": "Dinner at local restaurant",
  "location": "Beijing"
}
```

**Parameters:**
- `itinerary_id` (string, optional): Associated itinerary UUID
- `category` (string, required): Category (accommodation, food, transportation, activities, shopping, other)
- `amount` (number, required): Expense amount
- `description` (string, required): Description
- `date` (datetime, optional): Expense date (defaults to now)
- `location` (string, optional): Location where expense occurred

**Response:** `201 Created`
```json
{
  "id": "uuid-string",
  "user_id": "user-id",
  "itinerary_id": "uuid-string",
  "category": "food",
  "amount": 120.5,
  "description": "Dinner at local restaurant",
  "date": "2024-03-15T19:30:00",
  "location": "Beijing",
  "created_at": "2024-03-15T20:00:00",
  "updated_at": "2024-03-15T20:00:00"
}
```

### List Expenses

#### GET /expenses/

List expenses with optional filters.

**Query Parameters:**
- `itinerary_id` (string, optional): Filter by itinerary
- `category` (string, optional): Filter by category
- `limit` (integer, optional): Maximum number of results (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "user_id": "user-id",
    "itinerary_id": "uuid-string",
    "category": "food",
    "amount": 120.5,
    "description": "Dinner at local restaurant",
    "date": "2024-03-15T19:30:00",
    "location": "Beijing",
    "created_at": "2024-03-15T20:00:00"
  }
]
```

### Get Expense Summary

#### GET /expenses/summary

Get expense summary with category breakdown.

**Query Parameters:**
- `itinerary_id` (string, optional): Filter by itinerary

**Response:** `200 OK`
```json
{
  "total_expenses": 1500.0,
  "by_category": {
    "food": 500.0,
    "transportation": 300.0,
    "accommodation": 600.0,
    "activities": 100.0
  },
  "count": 15
}
```

### Get Expense

#### GET /expenses/{id}

Get a specific expense by ID.

**Path Parameters:**
- `id` (string, required): Expense UUID

**Response:** `200 OK`

### Update Expense

#### PUT /expenses/{id}

Update an existing expense.

**Path Parameters:**
- `id` (string, required): Expense UUID

**Request Body:**
```json
{
  "category": "shopping",
  "amount": 150.0,
  "description": "Updated description"
}
```

**Response:** `200 OK`

### Delete Expense

#### DELETE /expenses/{id}

Delete an expense.

**Path Parameters:**
- `id` (string, required): Expense UUID

**Response:** `204 No Content`

---

## Navigation Endpoints

### Search Location

#### POST /navigation/search

Search for locations using Amap API.

**Request Body:**
```json
{
  "query": "Forbidden City",
  "city": "Beijing"
}
```

**Parameters:**
- `query` (string, required): Search query
- `city` (string, optional): City to search in

**Response:** `200 OK`
```json
[
  {
    "name": "Forbidden City",
    "address": "4 Jingshan Front St, Dongcheng, Beijing",
    "longitude": 116.397026,
    "latitude": 39.918058
  }
]
```

### Get Route

#### POST /navigation/route

Get route information between two locations.

**Request Body:**
```json
{
  "origin": "Beijing Railway Station",
  "destination": "Forbidden City",
  "mode": "transit"
}
```

**Parameters:**
- `origin` (string, required): Starting point
- `destination` (string, required): Destination
- `mode` (string, optional): Travel mode (walking, transit, driving) - default: transit

**Response:** `200 OK`
```json
{
  "distance": 3.5,
  "duration": 25.0,
  "steps": [
    "Head north on Beijing Railway Station",
    "Take subway line 2",
    "Get off at Tiananmen East",
    "Walk to Forbidden City"
  ]
}
```

---

## Voice Recognition Endpoints

### Recognize Speech

#### POST /voice/recognize

Convert speech to text using iFlytek API.

**Request Body:**
```json
{
  "audio_data": "base64_encoded_audio_string",
  "language": "zh_cn"
}
```

**Parameters:**
- `audio_data` (string, required): Base64 encoded audio data
- `language` (string, optional): Language code (default: zh_cn)

**Response:** `200 OK`
```json
{
  "text": "我想去北京旅游三天",
  "confidence": 0.95
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: <error message>"
}
```

---

## Rate Limiting

Rate limiting is not currently implemented but recommended for production:
- 100 requests per minute per user for general endpoints
- 10 requests per minute for AI-powered itinerary generation
- 50 requests per minute for expense tracking

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
