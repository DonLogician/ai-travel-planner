# AI Travel Planner

A comprehensive AI-powered travel planning platform with personalized itinerary generation and smart expense tracking.

## Features

### 🤖 AI-Powered Itinerary Generation
- Generate personalized day-by-day travel plans using advanced LLM models (Qwen or Doubao)
- Customizable based on destination, dates, budget, and travel preferences
- Detailed activity suggestions with time schedules and estimated costs

### 💰 Smart Expense Tracking
- Track travel expenses by category (accommodation, food, transportation, activities, shopping)
- Real-time budget monitoring with planned vs. actual spending comparison
- Expense summary with category breakdowns

### 🗺️ Navigation & Location Services
- Integrated with Amap (高德地图) API for location search
- Route planning with multiple transport modes (walking, transit, driving)
- Distance and duration estimates

### 🎤 Voice Recognition
- Voice input powered by iFlytek API
- Support for multiple languages
- Hands-free expense entry and destination search

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database & Auth**: Supabase
- **LLM Integration**: Qwen (Alibaba Cloud) / Doubao (ByteDance)
- **APIs**: 
  - iFlytek for voice recognition
  - Amap for navigation and location services

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios

## Project Structure

```
ai-travel-planner/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── itinerary.py   # Itinerary endpoints
│   │   │   ├── expense.py     # Expense tracking endpoints
│   │   │   ├── navigation.py  # Navigation/location endpoints
│   │   │   └── voice.py       # Voice recognition endpoint
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings and configuration
│   │   │   └── database.py    # Database connection
│   │   ├── services/          # Business logic services
│   │   │   ├── travel_service.py     # Main travel service orchestrator
│   │   │   ├── llm_service.py        # LLM integration for itinerary generation
│   │   │   ├── expense_service.py    # Expense tracking logic
│   │   │   ├── navigation_service.py # Amap API integration
│   │   │   └── voice_service.py      # iFlytek API integration
│   │   └── schemas/           # Pydantic models
│   │       ├── itinerary.py   # Itinerary schemas
│   │       ├── expense.py     # Expense schemas
│   │       ├── location.py    # Location/navigation schemas
│   │       └── user.py        # User and voice schemas
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/                  # Vue.js frontend
│   ├── src/
│   │   ├── views/            # Page components
│   │   │   ├── Home.vue
│   │   │   ├── CreateItinerary.vue
│   │   │   ├── ItineraryList.vue
│   │   │   ├── ItineraryDetail.vue
│   │   │   └── ExpenseTracker.vue
│   │   ├── services/         # API services
│   │   │   ├── api.js
│   │   │   ├── itinerary.js
│   │   │   ├── expense.js
│   │   │   ├── navigation.js
│   │   │   └── voice.js
│   │   ├── stores/           # Pinia stores
│   │   │   ├── itinerary.js
│   │   │   └── expense.js
│   │   ├── router/           # Vue Router config
│   │   └── App.vue           # Main app component
│   ├── package.json
│   └── .env                  # Frontend environment variables
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+ and npm
- Supabase account
- API keys for:
  - Qwen (Alibaba Cloud) or Doubao (ByteDance)
  - Amap (高德地图)
  - iFlytek (optional, for voice features)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Configure your `.env` file with your API keys and settings:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# iFlytek API Configuration (Optional)
IFLYTEK_APP_ID=your_iflytek_app_id
IFLYTEK_API_KEY=your_iflytek_api_key
IFLYTEK_API_SECRET=your_iflytek_api_secret

# Amap API Configuration
AMAP_API_KEY=your_amap_api_key

# LLM Configuration (Choose one)
# For Qwen (Alibaba Cloud)
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-turbo

# For Doubao (ByteDance)
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_MODEL=doubao-pro

# Use which LLM provider: qwen or doubao
LLM_PROVIDER=qwen

# Secret Key for JWT
SECRET_KEY=your-secret-key-change-this-in-production
```

6. Set up Supabase database tables:

Create the following tables in your Supabase project:

**itineraries table:**
```sql
CREATE TABLE itineraries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
```

**expenses table:**
```sql
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

7. Run the backend server:
```bash
cd app
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- Alternative docs: `http://localhost:8000/api/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure the `.env` file (already created with default values):
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Creating an Itinerary

1. Navigate to "Plan Trip" in the navigation menu
2. Fill in your travel details:
   - Destination
   - Start and end dates
   - Budget
   - Travel preferences (cultural, food, adventure, etc.)
   - Additional notes
3. Click "Generate Itinerary"
4. View your AI-generated day-by-day plan with activities and estimated costs

### Tracking Expenses

1. Navigate to "Expenses" in the navigation menu
2. Click "+ Add Expense"
3. Fill in expense details:
   - Category (accommodation, food, transportation, etc.)
   - Amount
   - Description
   - Location (optional)
4. View expense summary and breakdown by category
5. Compare against your planned budget in the itinerary detail view

### Using Navigation Features

The navigation features are integrated into the itinerary generation:
- Location searches use Amap API for accurate results
- Route planning suggests optimal transportation methods
- Distance and time estimates help with planning

### Voice Input (Optional)

If you have configured iFlytek API credentials:
- Use voice commands to quickly add expenses
- Voice-enabled destination search
- Hands-free interaction for better user experience

## API Endpoints

### Itineraries
- `POST /api/itineraries/` - Create a new itinerary
- `GET /api/itineraries/` - List all itineraries
- `GET /api/itineraries/{id}` - Get specific itinerary
- `DELETE /api/itineraries/{id}` - Delete an itinerary
- `GET /api/itineraries/{id}/budget-status` - Get budget status

### Expenses
- `POST /api/expenses/` - Create a new expense
- `GET /api/expenses/` - List expenses (with filters)
- `GET /api/expenses/summary` - Get expense summary
- `GET /api/expenses/{id}` - Get specific expense
- `PUT /api/expenses/{id}` - Update an expense
- `DELETE /api/expenses/{id}` - Delete an expense

### Navigation
- `POST /api/navigation/search` - Search for locations
- `POST /api/navigation/route` - Get route information

### Voice Recognition
- `POST /api/voice/recognize` - Recognize speech from audio

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Follow the service-oriented architecture pattern
- Add new endpoints in `app/api/`
- Add business logic in `app/services/`
- Define data models in `app/schemas/`

### Frontend Development
- Components should be modular and reusable
- Use Pinia stores for state management
- API calls go through service files in `src/services/`
- Follow Vue 3 Composition API best practices

## Production Deployment

### Backend
1. Set `DEBUG=False` in production `.env`
2. Use a production-grade WSGI server like Gunicorn
3. Set up proper CORS origins
4. Use environment variables for all secrets
5. Enable HTTPS

### Frontend
1. Build the production bundle:
```bash
npm run build
```
2. Serve the `dist` folder with a web server (nginx, Apache, etc.)
3. Configure proper API base URL for production

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: This is a demonstration project. For production use, implement proper authentication, error handling, rate limiting, and security measures.