#!/bin/bash
# Script to sync local backend/media directory to production server

echo "=== Syncing Media Files to Production ==="
echo ""

# Configuration
SERVER="root@187.127.115.70"
REMOTE_MEDIA_DIR="/opt/data/realestate1/backend/media"
LOCAL_MEDIA_DIR="backend/media"

# Check if local media directory exists
if [ ! -d "$LOCAL_MEDIA_DIR" ]; then
    echo "Error: Local media directory not found: $LOCAL_MEDIA_DIR"
    exit 1
fi

echo "Local directory: $LOCAL_MEDIA_DIR"
echo "Remote directory: $REMOTE_MEDIA_DIR"
echo ""

# Ask for confirmation
read -p "Do you want to sync media files to production? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Sync cancelled."
    exit 0
fi

echo ""
echo "Step 1: Syncing media files..."
rsync -av --progress "$LOCAL_MEDIA_DIR/" "$SERVER:$REMOTE_MEDIA_DIR/"

if [ $? -ne 0 ]; then
    echo "Error: Failed to sync media files"
    exit 1
fi

echo ""
echo "Step 2: Setting correct permissions..."
ssh $SERVER "chown -R 1000:1000 $REMOTE_MEDIA_DIR && chmod -R 755 $REMOTE_MEDIA_DIR"

if [ $? -ne 0 ]; then
    echo "Warning: Failed to set permissions. You may need to do this manually."
fi

echo ""
echo "Step 3: Verifying sync..."
echo "Local file count:"
find "$LOCAL_MEDIA_DIR" -type f | wc -l

echo "Remote file count:"
ssh $SERVER "find $REMOTE_MEDIA_DIR -type f | wc -l"

echo ""
echo "Step 4: Testing media file access..."
echo "Testing: https://bijenkhadka.com.au/media/cms/logos/b.png"
curl -s -I https://bijenkhadka.com.au/media/cms/logos/b.png | grep -E "(HTTP|Content-Type)"

echo ""
echo "=== Sync Complete ==="
echo ""
echo "Media files have been synced to production."
echo "You can verify by visiting: https://bijenkhadka.com.au/media/"
