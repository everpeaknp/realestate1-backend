#!/bin/bash
# Script to fix the services table issue on production server

set -e  # Exit on error

SERVER="root@187.127.115.70"
APP_DIR="/opt/stacks/realestate1"
BACKEND_DIR="$APP_DIR/backend"

echo "=========================================="
echo "Fixing Services Table on Production"
echo "=========================================="

# Step 1: Copy the fix script to server
echo ""
echo "Step 1: Uploading fix script to server..."
scp fix_services_table.py "$SERVER:$BACKEND_DIR/"

# Step 2: Stop the backend container
echo ""
echo "Step 2: Stopping backend container..."
ssh "$SERVER" "cd $APP_DIR && docker compose stop realestate1-backend"

# Step 3: Run the fix script
echo ""
echo "Step 3: Running fix script..."
ssh "$SERVER" "cd $BACKEND_DIR && docker compose run --rm realestate1-backend python fix_services_table.py"

# Step 4: Run migrations
echo ""
echo "Step 4: Running migrations..."
ssh "$SERVER" "cd $BACKEND_DIR && docker compose run --rm realestate1-backend python manage.py migrate services"

# Step 5: Start containers
echo ""
echo "Step 5: Starting containers..."
ssh "$SERVER" "cd $APP_DIR && docker compose up -d"

# Step 6: Check container status
echo ""
echo "Step 6: Checking container status..."
sleep 5
ssh "$SERVER" "cd $APP_DIR && docker compose ps"

# Step 7: Check backend logs
echo ""
echo "Step 7: Checking backend logs (last 20 lines)..."
ssh "$SERVER" "cd $APP_DIR && docker compose logs --tail=20 realestate1-backend"

echo ""
echo "=========================================="
echo "✓ Deployment fix completed!"
echo "=========================================="
echo ""
echo "To verify:"
echo "  - Frontend: http://187.127.115.70:3000"
echo "  - Backend: http://187.127.115.70:8000"
echo ""
echo "To view live logs:"
echo "  ssh $SERVER 'cd $APP_DIR && docker compose logs -f'"
