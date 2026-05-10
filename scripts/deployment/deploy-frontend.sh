#!/bin/bash

# Frontend Deployment Script for realestate1-frontend
# Server: root@187.127.115.70
# Password: [REDACTED]

echo "🚀 Starting Frontend Deployment..."
echo "=================================="

# SSH connection details
SSH_USER="root"
SSH_HOST="187.127.115.70"
SSH_PASS="[REDACTED]"
PROJECT_DIR="realestate1-frontend"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Connecting to server...${NC}"

# Execute deployment commands on remote server
ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    set -e  # Exit on any error
    
    echo "📂 Navigating to project directory..."
    cd realestate1-frontend || { echo "❌ Project directory not found!"; exit 1; }
    
    echo "🔄 Pulling latest changes from Git..."
    git pull origin main || git pull origin master || git pull
    
    echo "📦 Installing dependencies..."
    npm install
    
    echo "🏗️  Building Next.js application..."
    npm run build
    
    echo "🔄 Restarting application..."
    # Check if PM2 is being used
    if command -v pm2 &> /dev/null; then
        echo "Using PM2 to restart..."
        pm2 restart realestate1-frontend || pm2 start npm --name "realestate1-frontend" -- start
        pm2 save
    else
        echo "⚠️  PM2 not found. Please restart the application manually with: npm start"
    fi
    
    echo "✅ Deployment completed successfully!"
    echo "=================================="
    
ENDSSH

echo -e "${GREEN}✅ Frontend deployment completed!${NC}"
echo ""
echo "📝 Next steps:"
echo "   1. Verify the application is running"
echo "   2. Check logs: ssh ${SSH_USER}@${SSH_HOST} 'pm2 logs realestate1-frontend'"
echo "   3. Test the website in your browser"
