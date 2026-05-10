#!/bin/bash

# Deployment Script for Real Estate Application
# This script pushes code to GitHub and deploys to production server

set -e  # Exit on error

echo "🚀 Starting deployment process..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SERVER_USER="root"
SERVER_HOST="187.127.115.70"
SERVER_PATH="/opt/stacks/realestate1"
BRANCH="main"

# Step 1: Push to GitHub
echo -e "${BLUE}📤 Step 1: Pushing to GitHub...${NC}"
cd backend
git add .
git status

read -p "Do you want to commit and push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    read -p "Enter commit message: " commit_msg
    git commit -m "$commit_msg"
    git push origin $BRANCH
    echo -e "${GREEN}✅ Pushed to GitHub${NC}"
else
    echo -e "${RED}❌ Deployment cancelled${NC}"
    exit 1
fi

cd ..

# Step 2: Deploy Backend to Server
echo -e "${BLUE}📥 Step 2: Deploying backend to server...${NC}"
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
    set -e
    cd /opt/stacks/realestate1/backend
    
    echo "Pulling latest changes..."
    git pull origin main
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo "Running migrations..."
    python manage.py migrate
    
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    
    echo "Restarting services..."
    # Add your service restart command here
    # systemctl restart gunicorn
    # or docker-compose restart backend
    
    echo "✅ Backend deployment complete!"
ENDSSH

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Step 3: Deploy Frontend (optional)
read -p "Do you want to deploy frontend too? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${BLUE}📥 Step 3: Deploying frontend to server...${NC}"
    
    cd frontend
    git add .
    git commit -m "$commit_msg" || echo "No changes to commit"
    git push origin $BRANCH || echo "Already up to date"
    cd ..
    
    ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
        set -e
        cd /opt/stacks/realestate1/frontend
        
        echo "Pulling latest changes..."
        git pull origin main
        
        echo "Installing dependencies..."
        npm install
        
        echo "Building frontend..."
        npm run build
        
        echo "Restarting frontend service..."
        # Add your service restart command here
        # pm2 restart frontend
        # or docker-compose restart frontend
        
        echo "✅ Frontend deployment complete!"
ENDSSH
    
    echo -e "${GREEN}✅ Frontend deployment completed!${NC}"
fi

echo -e "${GREEN}🎉 All done! Your application is deployed.${NC}"
