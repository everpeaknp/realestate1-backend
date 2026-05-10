# PowerShell Deployment Script for Production Server
# Server: root@187.127.115.70
# Password: [REDACTED]

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"

Write-Host "`n🚀 Starting Deployment..." -ForegroundColor Cyan
Write-Host "Server: $SSH_HOST" -ForegroundColor Yellow
Write-Host "Password: [REDACTED]`n" -ForegroundColor Yellow

# Create bash script content
$bashScript = @'
#!/bin/bash
set -e

echo ""
echo "================================================"
echo "🔧 BACKEND DEPLOYMENT"
echo "================================================"

# Find and navigate to backend
if [ -d "/root/realestate1-backend" ]; then
    cd /root/realestate1-backend
elif [ -d "$HOME/realestate1-backend" ]; then
    cd $HOME/realestate1-backend
elif [ -d "/var/www/realestate1-backend" ]; then
    cd /var/www/realestate1-backend
else
    echo "❌ Backend directory not found!"
    exit 1
fi

echo "📂 Backend directory: $(pwd)"
echo "🔄 Pulling latest changes..."
git pull origin main

echo "📦 Installing dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi
pip install -r requirements.txt

echo "🗃️  Running migrations..."
python manage.py migrate

echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Restarting backend service..."
sudo systemctl restart gunicorn 2>/dev/null || pm2 restart realestate1-backend 2>/dev/null || echo "Please restart manually"

echo "✅ Backend deployed!"

echo ""
echo "================================================"
echo "🎨 FRONTEND DEPLOYMENT"
echo "================================================"

# Find and navigate to frontend
if [ -d "/root/realestate1-frontend" ]; then
    cd /root/realestate1-frontend
elif [ -d "$HOME/realestate1-frontend" ]; then
    cd $HOME/realestate1-frontend
elif [ -d "/var/www/realestate1-frontend" ]; then
    cd /var/www/realestate1-frontend
else
    echo "❌ Frontend directory not found!"
    exit 1
fi

echo "📂 Frontend directory: $(pwd)"
echo "🔄 Pulling latest changes..."
git pull origin main

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building application..."
npm run build

echo "🔄 Restarting frontend service..."
pm2 restart realestate1-frontend || pm2 start npm --name realestate1-frontend -- start
pm2 save

echo "✅ Frontend deployed!"
echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
'@

# Save script to temp file
$tempScript = "temp_deploy_$(Get-Date -Format 'yyyyMMddHHmmss').sh"
$bashScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline

try {
    Write-Host "📤 Uploading deployment script..." -ForegroundColor Yellow
    scp $tempScript "${SSH_USER}@${SSH_HOST}:/tmp/deploy.sh"
    
    Write-Host "🚀 Executing deployment on server..." -ForegroundColor Yellow
    Write-Host "(You may need to enter password: [REDACTED])`n" -ForegroundColor Green
    
    ssh "${SSH_USER}@${SSH_HOST}" "bash /tmp/deploy.sh; rm /tmp/deploy.sh"
    
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   • Test the website in your browser" -ForegroundColor White
    Write-Host "   • Check logs if needed: ssh $SSH_USER@$SSH_HOST 'pm2 logs'" -ForegroundColor White
}
catch {
    Write-Host "`n❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`n💡 Try manual deployment:" -ForegroundColor Yellow
    Write-Host "   ssh $SSH_USER@$SSH_HOST" -ForegroundColor White
    Write-Host "   Password: [REDACTED]" -ForegroundColor White
}
finally {
    # Cleanup temp file
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
}
