#!/bin/bash
# Script to update production server to use local backend/media directory

echo "=== Updating Production to Use Local backend/media Directory ==="
echo ""

# SSH connection details
SERVER="root@187.127.115.70"
PROJECT_DIR="/opt/stacks/realestate1"

echo "Step 1: Backing up current compose.yml..."
ssh $SERVER "cd $PROJECT_DIR && cp compose.yml compose.yml.backup-$(date +%Y%m%d-%H%M%S)"

echo ""
echo "Step 2: Updating compose.yml to use local backend/media..."
ssh $SERVER "cd $PROJECT_DIR && cat > compose.yml << 'EOF'
services:
  realestate1-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: realestate1-backend
    env_file:
      - ./backend.env
    volumes:
      # Use local backend/media directory instead of external volume
      - ./backend/media:/app/media
      # Database volume (keep external for data persistence)
      - /opt/data/realestate1/backend:/app/data
    ports:
      - \"8000:8000\"
    networks:
      - realestate1_network
    restart: unless-stopped

  realestate1-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: realestate1-frontend
    env_file:
      - ./frontend.env
    ports:
      - \"3000:3000\"
    networks:
      - realestate1_network
    restart: unless-stopped
    depends_on:
      - realestate1-backend

networks:
  realestate1_network:
    driver: bridge
EOF
"

echo ""
echo "Step 3: Copying media files from external volume to local backend/media..."
ssh $SERVER "cd $PROJECT_DIR && rsync -av --progress /opt/data/realestate1/backend/media/ ./backend/media/"

echo ""
echo "Step 4: Setting correct permissions on backend/media..."
ssh $SERVER "cd $PROJECT_DIR && chown -R 1000:1000 ./backend/media && chmod -R 755 ./backend/media"

echo ""
echo "Step 5: Restarting containers with new configuration..."
ssh $SERVER "cd $PROJECT_DIR && docker compose down && docker compose up -d"

echo ""
echo "Step 6: Waiting for containers to start..."
sleep 10

echo ""
echo "Step 7: Verifying deployment..."
ssh $SERVER "cd $PROJECT_DIR && docker compose ps"

echo ""
echo "Step 8: Testing media file access..."
echo "Testing: https://bijenkhadka.com.au/media/cms/logos/b.png"
curl -s -I https://bijenkhadka.com.au/media/cms/logos/b.png | grep -E "(HTTP|Content-Type)"

echo ""
echo "=== Update Complete ==="
echo ""
echo "Media files are now served from: $PROJECT_DIR/backend/media"
echo "This directory is part of the git repository and will be version controlled."
echo ""
echo "To add new media files:"
echo "1. Add files to backend/media/ directory locally"
echo "2. Commit and push to git"
echo "3. Pull on production server: cd $PROJECT_DIR/backend && git pull"
echo "4. Files will be automatically available"
