#!/bin/bash
# Script to find project directories and CI/CD setup on server

echo "=========================================="
echo "Finding Project Directories"
echo "=========================================="
echo ""

echo "1. Searching for realestate1-backend..."
BACKEND=$(find /root /var/www /opt /home -name "realestate1-backend" -type d 2>/dev/null | head -1)
if [ -n "$BACKEND" ]; then
    echo "✅ Found backend at: $BACKEND"
    echo "   Git status:"
    cd "$BACKEND" && git status --short && git log --oneline -1
else
    echo "❌ Backend not found"
fi
echo ""

echo "2. Searching for realestate1-frontend..."
FRONTEND=$(find /root /var/www /opt /home -name "realestate1-frontend" -type d 2>/dev/null | head -1)
if [ -n "$FRONTEND" ]; then
    echo "✅ Found frontend at: $FRONTEND"
    echo "   Git status:"
    cd "$FRONTEND" && git status --short && git log --oneline -1
else
    echo "❌ Frontend not found"
fi
echo ""

echo "3. Checking for CI/CD configurations..."
echo "-------------------------------------------"

# Check for GitHub Actions
if [ -n "$BACKEND" ] && [ -d "$BACKEND/.github/workflows" ]; then
    echo "✅ Backend GitHub Actions found:"
    ls -la "$BACKEND/.github/workflows/"
fi

if [ -n "$FRONTEND" ] && [ -d "$FRONTEND/.github/workflows" ]; then
    echo "✅ Frontend GitHub Actions found:"
    ls -la "$FRONTEND/.github/workflows/"
fi

# Check for deployment scripts
echo ""
echo "4. Checking for deployment scripts..."
if [ -n "$BACKEND" ]; then
    echo "Backend deployment scripts:"
    ls -la "$BACKEND" | grep -E 'deploy|ci|cd|.sh$'
fi

if [ -n "$FRONTEND" ]; then
    echo "Frontend deployment scripts:"
    ls -la "$FRONTEND" | grep -E 'deploy|ci|cd|.sh$'
fi

# Check for systemd services
echo ""
echo "5. Checking systemd services..."
systemctl list-units --type=service | grep -E 'gunicorn|django|realestate|nextjs'

# Check PM2 processes
echo ""
echo "6. Checking PM2 processes..."
if command -v pm2 &> /dev/null; then
    pm2 list
else
    echo "PM2 not installed"
fi

# Check cron jobs
echo ""
echo "7. Checking cron jobs..."
crontab -l 2>/dev/null | grep -E 'realestate|deploy' || echo "No relevant cron jobs found"

# Check for webhooks
echo ""
echo "8. Checking for webhook configurations..."
if [ -n "$BACKEND" ]; then
    find "$BACKEND" -name "*webhook*" -o -name "*hook*" 2>/dev/null
fi
if [ -n "$FRONTEND" ]; then
    find "$FRONTEND" -name "*webhook*" -o -name "*hook*" 2>/dev/null
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Backend location: ${BACKEND:-Not found}"
echo "Frontend location: ${FRONTEND:-Not found}"
echo ""
