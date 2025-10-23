# AI Travel Planner - Architecture Documentation

## System Overview

The AI Travel Planner is a full-stack web application that leverages artificial intelligence to generate personalized travel itineraries and track expenses. The system integrates multiple external APIs for enhanced functionality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue.js)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Home View  │  │  Itinerary   │  │   Expense    │          │
│  │              │  │  Management  │  │   Tracker    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Pinia Stores (State Management)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          API Services (Axios HTTP Client)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                          │  │
│  │  - Itinerary API  - Expense API  - Navigation API        │  │
│  │  - Voice API      - Auth API (future)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Service Layer                            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ Travel Service  │  │ Expense Service │               │  │
│  │  │ (Orchestrator)  │  │                 │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │  LLM Service    │  │ Navigation Svc  │               │  │
│  │  │  (Qwen/Doubao)  │  │  (Amap API)     │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  │  ┌─────────────────┐                                     │  │
│  │  │  Voice Service  │                                     │  │
│  │  │  (iFlytek API)  │                                     │  │
│  │  └─────────────────┘                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Supabase   │  │  Qwen/Doubao │  │  Amap API    │          │
│  │  (Database   │  │     (LLM)    │  │ (Navigation) │          │
│  │   & Auth)    │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐                                               │
│  │  iFlytek API │                                               │
│  │  (Voice)     │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer (Vue.js 3)

**Technology Stack:**
- Vue.js 3 with Composition API
- Vite for build tooling
- Pinia for state management
- Vue Router for navigation
- Axios for HTTP requests

**Key Components:**
1. **Views**
   - `Home.vue`: Landing page with feature overview
   - `CreateItinerary.vue`: Form for itinerary generation
   - `ItineraryList.vue`: Display all user itineraries
   - `ItineraryDetail.vue`: Detailed view of a single itinerary
   - `ExpenseTracker.vue`: Expense management interface

2. **Services**
   - API client configuration
   - Service modules for each backend API (itinerary, expense, navigation, voice)

3. **Stores**
   - Itinerary store: Manages itinerary state
   - Expense store: Manages expense tracking state

### Backend Layer (FastAPI)

**Technology Stack:**
- FastAPI (Python web framework)
- Pydantic for data validation
- Uvicorn as ASGI server
- Supabase Python client
- HTTPx for async HTTP requests

**Architecture Pattern:** Service-Oriented Architecture

**Core Services:**

1. **Travel Service (Orchestrator)**
   - Coordinates itinerary generation and expense tracking
   - Main interface for travel-related operations
   - Manages relationships between itineraries and expenses
   - Provides budget status and comparison

2. **LLM Service**
   - Integrates with Qwen (Alibaba Cloud) or Doubao (ByteDance)
   - Generates personalized itineraries based on user inputs
   - Processes travel preferences into detailed day plans
   - Estimates costs for activities

3. **Expense Service**
   - CRUD operations for expense records
   - Category-based expense tracking
   - Expense summary and analytics
   - Integration with Supabase database

4. **Navigation Service**
   - Integrates with Amap (高德地图) API
   - Location search functionality
   - Route planning with multiple modes (walking, transit, driving)
   - Distance and duration calculations

5. **Voice Service**
   - Integrates with iFlytek API
   - Speech-to-text conversion
   - Supports multiple languages (primarily Chinese)

**API Endpoints:**

```
/api/itineraries/
  - POST   /             Create itinerary
  - GET    /             List itineraries
  - GET    /{id}         Get itinerary details
  - DELETE /{id}         Delete itinerary
  - GET    /{id}/budget-status   Get budget status

/api/expenses/
  - POST   /             Create expense
  - GET    /             List expenses
  - GET    /summary      Get expense summary
  - GET    /{id}         Get expense details
  - PUT    /{id}         Update expense
  - DELETE /{id}         Delete expense

/api/navigation/
  - POST   /search       Search locations
  - POST   /route        Get route information

/api/voice/
  - POST   /recognize    Recognize speech
```

### Data Layer

**Supabase Database Schema:**

```sql
-- Itineraries Table
CREATE TABLE itineraries (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  destination TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  budget DECIMAL NOT NULL,
  daily_itinerary JSONB NOT NULL,
  total_estimated_cost DECIMAL NOT NULL,
  recommendations TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Expenses Table
CREATE TABLE expenses (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  itinerary_id UUID REFERENCES itineraries(id),
  category TEXT NOT NULL,
  amount DECIMAL NOT NULL,
  description TEXT NOT NULL,
  date TIMESTAMP NOT NULL,
  location TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### External API Integrations

1. **Supabase**
   - Purpose: Database and authentication
   - Used for: Storing itineraries, expenses, user data
   - Features: Real-time updates, row-level security

2. **Qwen (Alibaba Cloud) / Doubao (ByteDance)**
   - Purpose: AI-powered itinerary generation
   - Used for: Natural language processing, trip planning
   - Features: Context-aware responses, Chinese language support

3. **Amap (高德地图)**
   - Purpose: Location and navigation services
   - Used for: Place search, route planning, geocoding
   - Features: Multiple transport modes, Chinese POI database

4. **iFlytek**
   - Purpose: Voice recognition
   - Used for: Speech-to-text conversion
   - Features: High accuracy for Chinese language, real-time processing

## Data Flow

### Itinerary Generation Flow

```
1. User fills form in CreateItinerary.vue
2. Frontend sends POST to /api/itineraries/
3. Backend receives request at itinerary endpoint
4. Travel Service coordinates with LLM Service
5. LLM Service calls Qwen/Doubao API
6. LLM generates structured itinerary
7. Travel Service saves to Supabase
8. Response returned to frontend
9. User redirected to ItineraryDetail.vue
```

### Expense Tracking Flow

```
1. User adds expense in ExpenseTracker.vue
2. Frontend sends POST to /api/expenses/
3. Backend validates data with Pydantic schemas
4. Expense Service saves to Supabase
5. Frontend updates Expense Store
6. Summary is recalculated
7. UI updates to show new expense
```

### Navigation Flow

```
1. User searches location in itinerary form
2. Frontend calls Navigation Service
3. Backend queries Amap API
4. Results parsed and returned
5. Frontend displays location suggestions
6. User can request route planning
7. Backend calculates route via Amap
8. Step-by-step directions returned
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **CORS**: Configured to allow specific origins only
3. **Input Validation**: Pydantic schemas validate all inputs
4. **Authentication**: Mock implementation (ready for JWT)
5. **HTTPS**: Recommended for production deployment

## Scalability

1. **Async Operations**: FastAPI async endpoints for concurrent requests
2. **Caching**: Can be added for frequently accessed itineraries
3. **Load Balancing**: FastAPI can run multiple workers
4. **Database**: Supabase provides auto-scaling
5. **CDN**: Frontend static assets can be served via CDN

## Deployment Architecture

**Development:**
- Backend: `uvicorn --reload` on port 8000
- Frontend: `npm run dev` on port 5173

**Production:**
- Backend: Gunicorn + Uvicorn workers behind nginx
- Frontend: Built static files served by nginx or CDN
- Database: Supabase managed service
- Environment: Docker containers with docker-compose

## Future Enhancements

1. **Authentication**: Full JWT-based auth with Supabase
2. **Real-time Updates**: WebSocket for live expense tracking
3. **Offline Support**: PWA with service workers
4. **Mobile App**: React Native or Flutter
5. **Social Features**: Share itineraries, collaborative planning
6. **ML Models**: Personalized recommendations based on history
7. **Payment Integration**: Direct booking and payment
8. **Multi-language**: i18n support for international users
