#!/bin/bash

# AI Travel Planner - Quick Setup Script
# This script sets up both backend and frontend for development

set -e

echo "========================================="
echo "AI Travel Planner - Quick Setup"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Setup Backend
echo "========================================="
echo "Setting up Backend..."
echo "========================================="

cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your API keys!"
fi

echo "✅ Backend setup complete"
echo ""

# Setup Frontend
echo "========================================="
echo "Setting up Frontend..."
echo "========================================="

cd ../frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
fi

echo "✅ Frontend setup complete"
echo ""

# Final instructions
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API keys in backend/.env:"
echo "   - SUPABASE_URL and SUPABASE_KEY (required)"
echo "   - QWEN_API_KEY or DOUBAO_API_KEY (required for AI features)"
echo "   - AMAP_API_KEY (optional, for navigation)"
echo "   - IFLYTEK credentials (optional, for voice)"
echo ""
echo "2. Set up Supabase database tables (see README.md)"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   cd app && python -m uvicorn main:app --reload"
echo ""
echo "4. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open http://localhost:5173 in your browser"
echo ""
echo "For more information, see README.md"
echo ""
