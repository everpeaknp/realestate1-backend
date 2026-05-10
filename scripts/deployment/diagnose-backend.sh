#!/bin/bash
# Backend Diagnostic Script
# Run this on the server to diagnose the 502 error

echo "=========================================="
echo "Backend Diagnostic Report"
echo "=========================================="
echo ""

echo "1. Checking Nginx Status..."
echo "----------------------------"
systemctl is-active nginx && echo "✅ Nginx is running" || echo "❌ Nginx is NOT running"
echo ""

echo "2. Checking Gunicorn Status..."
echo "-------------------------------"
if systemctl list-units --type=service | grep -q gunicorn; then
    systemctl status gunicorn --no-pager
else
    echo "❌ Gunicorn service not found"
fi
echo ""

echo "3. Checking Python Processes..."
echo "--------------------------------"
ps aux | grep python | grep -v grep
echo ""

echo "4. Checking PM2 Processes..."
echo "-----------------------------"
if command -v pm2 &> /dev/null; then
    pm2 list
else
    echo "PM2 not installed"
fi
echo ""

echo "5. Finding Backend Directory..."
echo "--------------------------------"
BACKEND_DIRS=$(find /var/www /root /opt /home -name "realestate1-backend" -type d 2>/dev/null)
if [ -z "$BACKEND_DIRS" ]; then
    echo "❌ Backend directory not found!"
else
    echo "✅ Found backend at:"
    echo "$BACKEND_DIRS"
fi
echo ""

echo "6. Checking Port 8000..."
echo "------------------------"
if lsof -i :8000 &> /dev/null; then
    echo "✅ Something is listening on port 8000:"
    lsof -i :8000
else
    echo "❌ Nothing listening on port 8000"
fi
echo ""

echo "7. Recent Gunicorn Logs..."
echo "---------------------------"
if [ -f /var/log/gunicorn/error.log ]; then
    echo "Last 10 lines of gunicorn error log:"
    tail -10 /var/log/gunicorn/error.log
else
    echo "Checking journalctl..."
    journalctl -u gunicorn -n 10 --no-pager 2>/dev/null || echo "No gunicorn logs found"
fi
echo ""

echo "8. Recent Nginx Error Logs..."
echo "------------------------------"
if [ -f /var/log/nginx/error.log ]; then
    echo "Last 10 lines of nginx error log:"
    tail -10 /var/log/nginx/error.log
else
    echo "Nginx error log not found"
fi
echo ""

echo "9. Nginx Configuration..."
echo "--------------------------"
if [ -f /etc/nginx/sites-available/bijenkhadka.com.au ]; then
    echo "Found nginx config for bijenkhadka.com.au"
    grep -A 5 "location" /etc/nginx/sites-available/bijenkhadka.com.au | head -20
elif [ -f /etc/nginx/sites-available/default ]; then
    echo "Using default nginx config"
    grep -A 5 "location" /etc/nginx/sites-available/default | head -20
fi
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. If gunicorn is not running, restart it"
echo "2. If backend directory found, cd there and pull latest code"
echo "3. Check the logs above for specific errors"
