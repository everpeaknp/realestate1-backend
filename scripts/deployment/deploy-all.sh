#!/bin/bash

# Complete Deployment Script for Backend and Frontend
# Server: root@187.127.115.70
# Password: [REDACTED]

echo "🚀 Starting Complete Deployment (Backend + Frontend)..."
echo "========================================================"

# SSH connection details
SSH_USER="root"
SSH_HOST="187.127.115.70"
BACKEND_DIR="realestate1-backend"
FRONTEND_DIR="realestate1-frontend"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Connecting to server...${NC}"

# Execute deployment commands on remote server
ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    set -e  # Exit on any error
    
    echo ""
    echo "================================================"
    echo "🔧 BACKEND DEPLOYMENT"
    echo "================================================"
    
    echo "📂 Navigating to backend directory..."
    cd /opt/stacks/realestate1/backend || { echo "❌ Backend directory not found!"; exit 1; }
    
    echo "🔄 Pulling latest backend changes from Git..."
    git pull origin main || git pull origin master || git pull
    
    echo "📦 Installing Python dependencies..."
    source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    
    echo "🗃️  Running database migrations..."
    python manage.py migrate
    
    echo "📊 Collecting static files..."
    python manage.py collectstatic --noinput
    
    echo "🔄 Restarting backend service..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl restart gunicorn || sudo systemctl restart realestate-backend || echo "⚠️  Please restart backend service manually"
    elif command -v pm2 &> /dev/null; then
        pm2 restart realestate1-backend || echo "⚠️  Backend not running in PM2"
    else
        echo "⚠️  Please restart the backend service manually"
    fi
    
    echo "✅ Backend deployment completed!"
    
    echo ""
    echo "================================================"
    echo "🎨 FRONTEND DEPLOYMENT"
    echo "================================================"
    
    echo "📂 Navigating to frontend directory..."
    cd /opt/stacks/realestate1/frontend || { echo "❌ Frontend directory not found!"; exit 1; }
    
    echo "🔄 Pulling latest frontend changes from Git..."
    git pull origin main || git pull origin master || git pull
    
    echo "📦 Installing Node.js dependencies..."
    npm install
    
    echo "🏗️  Building Next.js application..."
    npm run build
    
    echo "🔄 Restarting frontend application..."
    if command -v pm2 &> /dev/null; then
        pm2 restart realestate1-frontend || pm2 start npm --name "realestate1-frontend" -- start
        pm2 save
    else
        echo "⚠️  PM2 not found. Please restart the application manually with: npm start"
    fi
    
    echo "✅ Frontend deployment completed!"
    
    echo ""
    echo "================================================"
    echo "✅ COMPLETE DEPLOYMENT FINISHED!"
    echo "================================================"
    
ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Both Backend and Frontend deployed successfully!${NC}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Verify both applications are running"
    echo "   2. Check backend logs: ssh ${SSH_USER}@${SSH_HOST} 'tail -f /var/log/gunicorn/error.log'"
    echo "   3. Check frontend logs: ssh ${SSH_USER}@${SSH_HOST} 'pm2 logs realestate1-frontend'"
    echo "   4. Test the website in your browser"
else
    echo -e "${RED}❌ Deployment failed! Check the error messages above.${NC}"
    exit 1
fi
