#!/bin/bash

# Navigation Fix Deployment Script
# Deploys the click event fix to production

set -e

echo "=========================================="
echo "Navigation Fix Deployment"
echo "=========================================="
echo ""

# Server details
SERVER="root@187.127.115.70"
APP_DIR="/opt/stacks/realestate1"

echo "Step 1: Pulling latest frontend code..."
ssh "$SERVER" << 'ENDSSH'
cd /opt/stacks/realestate1/frontend
git pull origin main
ENDSSH

echo ""
echo "Step 2: Rebuilding frontend container..."
ssh "$SERVER" << 'ENDSSH'
cd /opt/stacks/realestate1
docker compose build --no-cache realestate1-frontend
ENDSSH

echo ""
echo "Step 3: Restarting frontend container..."
ssh "$SERVER" << 'ENDSSH'
cd /opt/stacks/realestate1
docker compose up -d realestate1-frontend
ENDSSH

echo ""
echo "Step 4: Waiting for container to start..."
sleep 10

echo ""
echo "Step 5: Checking container status..."
ssh "$SERVER" << 'ENDSSH'
cd /opt/stacks/realestate1
docker compose ps | grep realestate1-frontend
ENDSSH

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Please test the navigation at: https://bijenkhadka.com.au/"
echo "Expected: Menu items work on first click"
echo ""
