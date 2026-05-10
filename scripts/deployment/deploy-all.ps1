# PowerShell Deployment Script for Windows
# Deploys both Backend and Frontend to production server

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"
$SSH_PASS = "[REDACTED]"

Write-Host "🚀 Starting Complete Deployment (Backend + Frontend)..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Create a temporary script file for remote execution
$remoteScript = @'
#!/bin/bash
set -e

echo ""
echo "================================================"
echo "🔧 BACKEND DEPLOYMENT"
echo "================================================"

# Find backend directory
if [ -d "/root/realestate1-backend" ]; then
    BACKEND_DIR="/root/realestate1-backend"
elif [ -d "~/realestate1-backend" ]; then
    BACKEND_DIR="~/realestate1-backend"
elif [ -d "/var/www/realestate1-backend" ]; then
    BACKEND_DIR="/var/www/realestate1-backend"
else
    echo "❌ Backend directory not found! Searching..."
    find / -name "realestate1-backend" -type d 2>/dev/null | head -1
    exit 1
fi

echo "📂 Found backend at: $BACKEND_DIR"
cd "$BACKEND_DIR"

echo "🔄 Pulling latest backend changes..."
git pull origin main || git pull origin master || git pull

echo "📦 Installing Python dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
pip install -r requirements.txt

echo "🗃️  Running database migrations..."
python manage.py migrate

echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Restarting backend..."
if systemctl list-units --type=service | grep -q gunicorn; then
    sudo systemctl restart gunicorn
elif systemctl list-units --type=service | grep -q realestate; then
    sudo systemctl restart realestate-backend
elif command -v pm2 &> /dev/null; then
    pm2 restart realestate1-backend || echo "Backend not in PM2"
fi

echo "✅ Backend deployment completed!"

echo ""
echo "================================================"
echo "🎨 FRONTEND DEPLOYMENT"
echo "================================================"

# Find frontend directory
if [ -d "/root/realestate1-frontend" ]; then
    FRONTEND_DIR="/root/realestate1-frontend"
elif [ -d "~/realestate1-frontend" ]; then
    FRONTEND_DIR="~/realestate1-frontend"
elif [ -d "/var/www/realestate1-frontend" ]; then
    FRONTEND_DIR="/var/www/realestate1-frontend"
else
    echo "❌ Frontend directory not found! Searching..."
    find / -name "realestate1-frontend" -type d 2>/dev/null | head -1
    exit 1
fi

echo "📂 Found frontend at: $FRONTEND_DIR"
cd "$FRONTEND_DIR"

echo "🔄 Pulling latest frontend changes..."
git pull origin main || git pull origin master || git pull

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building application..."
npm run build

echo "🔄 Restarting frontend..."
if command -v pm2 &> /dev/null; then
    pm2 restart realestate1-frontend || pm2 start npm --name "realestate1-frontend" -- start
    pm2 save
fi

echo "✅ Frontend deployment completed!"
echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
'@

# Save the script temporarily
$remoteScript | Out-File -FilePath "temp_deploy.sh" -Encoding ASCII

Write-Host "📤 Uploading deployment script to server..." -ForegroundColor Yellow

# Use plink (PuTTY) if available, otherwise use OpenSSH
try {
    # Try using OpenSSH with password
    Write-Host "Connecting to ${SSH_USER}@${SSH_HOST}..." -ForegroundColor Yellow
    Write-Host "Please enter password when prompted: $SSH_PASS" -ForegroundColor Green
    
    # Upload script
    scp temp_deploy.sh "${SSH_USER}@${SSH_HOST}:/tmp/deploy.sh"
    
    # Execute script
    ssh "${SSH_USER}@${SSH_HOST}" "chmod +x /tmp/deploy.sh; /tmp/deploy.sh; rm /tmp/deploy.sh"
    
    Write-Host ""
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Verify applications are running"
    Write-Host "   2. Test the website in your browser"
    Write-Host "   3. Check logs if needed"
}
catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Manual deployment steps:" -ForegroundColor Yellow
    Write-Host "   1. SSH into server: ssh ${SSH_USER}@${SSH_HOST}"
    Write-Host "   2. Password: $SSH_PASS"
    Write-Host "   3. Run the commands from deploy-all.sh manually"
}
finally {
    # Cleanup
    if (Test-Path "temp_deploy.sh") {
        Remove-Item "temp_deploy.sh"
    }
}
