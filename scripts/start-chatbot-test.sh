#!/bin/bash

# Chatbot Quick Start & Test Script
# This script helps you start the backend, frontend, and test the chatbot

echo "🚀 Lily White Real Estate - Chatbot Quick Start"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to test backend health
test_backend() {
    echo -e "${BLUE}Testing backend health...${NC}"
    response=$(curl -s http://localhost:8000/api/chatbot/health/)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 0
    else
        echo -e "${RED}❌ Backend is not responding${NC}"
        return 1
    fi
}

# Function to test chat API
test_chat() {
    echo -e "${BLUE}Testing chat API...${NC}"
    response=$(curl -s -X POST http://localhost:8000/api/chatbot/chat/ \
        -H "Content-Type: application/json" \
        -d '{"message":"Hello, I am looking for a 3 bedroom house","user_name":"Test User","user_email":"test@example.com","user_phone":"+61400000000"}')
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Chat API is working!${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 0
    else
        echo -e "${RED}❌ Chat API is not responding${NC}"
        return 1
    fi
}

# Main menu
echo "What would you like to do?"
echo ""
echo "1) Check if services are running"
echo "2) Start backend only"
echo "3) Start frontend only"
echo "4) Start both backend and frontend"
echo "5) Test backend health"
echo "6) Test chat API"
echo "7) Run full diagnostic (opens browser)"
echo "8) Open frontend in browser"
echo "9) Exit"
echo ""
read -p "Enter your choice (1-9): " choice

case $choice in
    1)
        echo ""
        echo "Checking services..."
        echo ""
        
        if check_port 8000; then
            echo -e "${GREEN}✅ Backend is running on port 8000${NC}"
        else
            echo -e "${RED}❌ Backend is NOT running on port 8000${NC}"
            echo -e "${YELLOW}   Start it with: cd backend && python manage.py runserver${NC}"
        fi
        
        if check_port 3000; then
            echo -e "${GREEN}✅ Frontend is running on port 3000${NC}"
        else
            echo -e "${RED}❌ Frontend is NOT running on port 3000${NC}"
            echo -e "${YELLOW}   Start it with: cd frontend && npm run dev${NC}"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}Starting backend...${NC}"
        echo ""
        
        if check_port 8000; then
            echo -e "${YELLOW}⚠️  Backend is already running on port 8000${NC}"
            read -p "Do you want to restart it? (y/n): " restart
            if [ "$restart" = "y" ]; then
                echo "Stopping existing backend..."
                pkill -f "manage.py runserver" 2>/dev/null
                sleep 2
            else
                exit 0
            fi
        fi
        
        cd backend
        echo "Starting Django development server..."
        python manage.py runserver
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Starting frontend...${NC}"
        echo ""
        
        if check_port 3000; then
            echo -e "${YELLOW}⚠️  Frontend is already running on port 3000${NC}"
            read -p "Do you want to restart it? (y/n): " restart
            if [ "$restart" = "y" ]; then
                echo "Stopping existing frontend..."
                pkill -f "next dev" 2>/dev/null
                sleep 2
            else
                exit 0
            fi
        fi
        
        cd frontend
        echo "Starting Next.js development server..."
        npm run dev
        ;;
        
    4)
        echo ""
        echo -e "${BLUE}Starting both backend and frontend...${NC}"
        echo ""
        
        # Start backend in background
        if check_port 8000; then
            echo -e "${YELLOW}⚠️  Backend is already running${NC}"
        else
            echo "Starting backend..."
            cd backend
            python manage.py runserver > /dev/null 2>&1 &
            BACKEND_PID=$!
            cd ..
            echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
        fi
        
        # Wait a bit for backend to start
        sleep 3
        
        # Start frontend in background
        if check_port 3000; then
            echo -e "${YELLOW}⚠️  Frontend is already running${NC}"
        else
            echo "Starting frontend..."
            cd frontend
            npm run dev > /dev/null 2>&1 &
            FRONTEND_PID=$!
            cd ..
            echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}🎉 Both services are starting!${NC}"
        echo ""
        echo "Backend: http://localhost:8000"
        echo "Frontend: http://localhost:3000"
        echo ""
        echo "Press Ctrl+C to stop both services"
        
        # Wait for user to press Ctrl+C
        trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;
        
    5)
        echo ""
        if check_port 8000; then
            test_backend
        else
            echo -e "${RED}❌ Backend is not running${NC}"
            echo -e "${YELLOW}Start it with: cd backend && python manage.py runserver${NC}"
        fi
        ;;
        
    6)
        echo ""
        if check_port 8000; then
            test_chat
        else
            echo -e "${RED}❌ Backend is not running${NC}"
            echo -e "${YELLOW}Start it with: cd backend && python manage.py runserver${NC}"
        fi
        ;;
        
    7)
        echo ""
        echo -e "${BLUE}Opening diagnostic tool in browser...${NC}"
        
        # Detect OS and open browser
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open frontend/diagnose-chatbot-detailed.html
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open frontend/diagnose-chatbot-detailed.html
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            # Windows
            start frontend/diagnose-chatbot-detailed.html
        else
            echo -e "${YELLOW}Please open this file manually:${NC}"
            echo "frontend/diagnose-chatbot-detailed.html"
        fi
        ;;
        
    8)
        echo ""
        echo -e "${BLUE}Opening frontend in browser...${NC}"
        
        if ! check_port 3000; then
            echo -e "${RED}❌ Frontend is not running${NC}"
            echo -e "${YELLOW}Start it with: cd frontend && npm run dev${NC}"
            exit 1
        fi
        
        # Detect OS and open browser
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open http://localhost:3000
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open http://localhost:3000
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            # Windows
            start http://localhost:3000
        else
            echo -e "${YELLOW}Please open this URL manually:${NC}"
            echo "http://localhost:3000"
        fi
        ;;
        
    9)
        echo ""
        echo "Goodbye! 👋"
        exit 0
        ;;
        
    *)
        echo ""
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
