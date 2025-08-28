#!/bin/bash

# Sales Intelligence Platform Startup Script

echo "🚀 Starting Sales Intelligence Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ from https://python.org/${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}❌ pip is not installed. Please install pip${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies found${NC}"

# Setup backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update the .env file with your API keys and database configuration${NC}"
fi

# Setup database (PostgreSQL)
echo -e "${BLUE}Setting up database...${NC}"

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Please start PostgreSQL service${NC}"
    echo "   - On macOS: brew services start postgresql"
    echo "   - On Ubuntu: sudo systemctl start postgresql"
    echo "   - On Windows: Start PostgreSQL service from Services"
fi

# Create database if it doesn't exist
echo "Creating database (if not exists)..."
createdb sales_intelligence 2>/dev/null || echo "Database may already exist"

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Setup frontend
echo -e "${BLUE}Setting up frontend...${NC}"
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cp .env.example .env
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"

# Start services
echo -e "${BLUE}Starting services...${NC}"

# Start backend in background
echo "Starting backend server..."
cd ../backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo -e "${GREEN}🎉 Sales Intelligence Platform is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}🔧 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📖 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait