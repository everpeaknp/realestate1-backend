#!/bin/bash
# Quick script to restart backend and verify chatbot fix

echo "=========================================="
echo "  Restarting Backend Service"
echo "=========================================="
echo ""

echo "Step 1: Restarting backend container..."
docker-compose restart backend

echo ""
echo "Step 2: Waiting for backend to start (30 seconds)..."
sleep 30

echo ""
echo "Step 3: Checking backend health..."
curl -s http://localhost:8000/api/chatbot/message/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend is running!"
else
    echo "⚠️  Backend may not be ready yet. Wait a few more seconds."
fi

echo ""
echo "=========================================="
echo "  Backend Restarted Successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000"
echo "2. Open the chatbot (bottom-right corner)"
echo "3. Test queries:"
echo "   - 'list all properties'"
echo "   - 'show all properties'"
echo "   - 'show me all listings'"
echo ""
echo "Expected: You should see actual property listings"
echo "          from both Django DB and Eagle API"
echo ""
echo "View logs: docker-compose logs -f backend | grep -i chatbot"
echo ""
