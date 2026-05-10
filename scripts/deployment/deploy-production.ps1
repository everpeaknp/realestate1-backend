# Production Deployment Script for bijenkhadka.com.au
# This script deploys both backend and frontend to production

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"
$DOMAIN = "bijenkhadka.com.au"

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploying to $DOMAIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nServer: $SSH_HOST" -ForegroundColor Yellow
Write-Host "Password: [REDACTED]`n" -ForegroundColor Yellow

Write-Host "📋 Deployment Steps:" -ForegroundColor White
Write-Host "   1. Connect to server via SSH" -ForegroundColor Gray
Write-Host "   2. Pull latest backend code" -ForegroundColor Gray
Write-Host "   3. Update backend dependencies and migrate DB" -ForegroundColor Gray
Write-Host "   4. Pull latest frontend code" -ForegroundColor Gray
Write-Host "   5. Build and restart frontend" -ForegroundColor Gray
Write-Host "`n"

Write-Host "🔐 Connecting to production server..." -ForegroundColor Yellow
Write-Host "   (Enter password when prompted: [REDACTED])`n" -ForegroundColor Green

# Create deployment commands
$deployCommands = @"
echo '================================================'
echo '🔍 Locating project directories...'
echo '================================================'

# Find backend directory
if [ -d '/var/www/realestate1-backend' ]; then
    BACKEND_DIR='/var/www/realestate1-backend'
elif [ -d '/root/realestate1-backend' ]; then
    BACKEND_DIR='/root/realestate1-backend'
elif [ -d '/opt/realestate1-backend' ]; then
    BACKEND_DIR='/opt/realestate1-backend'
else
    echo '❌ Backend directory not found!'
    echo 'Searching...'
    BACKEND_DIR=`$(find /var/www /root /opt /home -name 'realestate1-backend' -type d 2>/dev/null | head -1)
    if [ -z "`$BACKEND_DIR" ]; then
        echo '❌ Could not locate backend directory'
        exit 1
    fi
fi

# Find frontend directory
if [ -d '/var/www/realestate1-frontend' ]; then
    FRONTEND_DIR='/var/www/realestate1-frontend'
elif [ -d '/root/realestate1-frontend' ]; then
    FRONTEND_DIR='/root/realestate1-frontend'
elif [ -d '/opt/realestate1-frontend' ]; then
    FRONTEND_DIR='/opt/realestate1-frontend'
else
    echo '❌ Frontend directory not found!'
    echo 'Searching...'
    FRONTEND_DIR=`$(find /var/www /root /opt /home -name 'realestate1-frontend' -type d 2>/dev/null | head -1)
    if [ -z "`$FRONTEND_DIR" ]; then
        echo '❌ Could not locate frontend directory'
        exit 1
    fi
fi

echo "✅ Backend found at: `$BACKEND_DIR"
echo "✅ Frontend found at: `$FRONTEND_DIR"
echo ''

echo '================================================'
echo '🔧 DEPLOYING BACKEND'
echo '================================================'
cd "`$BACKEND_DIR"
echo "📂 Working directory: `$(pwd)"

echo '🔄 Pulling latest code...'
git pull origin main

echo '📦 Activating virtual environment...'
if [ -d 'venv' ]; then
    source venv/bin/activate
elif [ -d '.venv' ]; then
    source .venv/bin/activate
fi

echo '📦 Installing dependencies...'
pip install -r requirements.txt

echo '🗃️  Running migrations...'
python manage.py migrate

echo '📊 Collecting static files...'
python manage.py collectstatic --noinput

echo '🔄 Restarting backend service...'
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    echo '✅ Gunicorn restarted'
elif systemctl is-active --quiet realestate-backend; then
    sudo systemctl restart realestate-backend
    echo '✅ Backend service restarted'
elif command -v pm2 >/dev/null 2>&1; then
    pm2 restart realestate1-backend 2>/dev/null || echo '⚠️  Backend not in PM2'
else
    echo '⚠️  Could not restart backend automatically'
fi

echo '✅ Backend deployment complete!'
echo ''

echo '================================================'
echo '🎨 DEPLOYING FRONTEND'
echo '================================================'
cd "`$FRONTEND_DIR"
echo "📂 Working directory: `$(pwd)"

echo '🔄 Pulling latest code...'
git pull origin main

echo '📦 Installing dependencies...'
npm install

echo '🏗️  Building Next.js application...'
npm run build

echo '🔄 Restarting frontend service...'
if command -v pm2 >/dev/null 2>&1; then
    pm2 restart realestate1-frontend || pm2 start npm --name realestate1-frontend -- start
    pm2 save
    echo '✅ Frontend restarted via PM2'
elif systemctl is-active --quiet nextjs; then
    sudo systemctl restart nextjs
    echo '✅ Next.js service restarted'
else
    echo '⚠️  Could not restart frontend automatically'
fi

echo '✅ Frontend deployment complete!'
echo ''

echo '================================================'
echo '✅ DEPLOYMENT SUCCESSFUL!'
echo '================================================'
echo ''
echo '🌐 Your website is now live at:'
echo "   https://$DOMAIN/"
echo "   https://$DOMAIN/admin"
echo ''
echo '📊 Service Status:'
systemctl is-active --quiet gunicorn && echo '   ✅ Backend (Gunicorn): Running' || echo '   ⚠️  Backend: Check status'
systemctl is-active --quiet nginx && echo '   ✅ Nginx: Running' || echo '   ⚠️  Nginx: Check status'
command -v pm2 >/dev/null 2>&1 && pm2 list | grep -q realestate1-frontend && echo '   ✅ Frontend (PM2): Running' || echo '   ⚠️  Frontend: Check status'
echo ''
"@

# Execute deployment
try {
    # Write commands to temp file
    $tempFile = [System.IO.Path]::GetTempFileName()
    $deployCommands | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline
    
    # Execute via SSH
    Get-Content $tempFile | ssh "${SSH_USER}@${SSH_HOST}" "bash -s"
    
    # Cleanup
    Remove-Item $tempFile -Force
    
    Write-Host "`n✅ Deployment completed successfully!`n" -ForegroundColor Green
    Write-Host "🌐 Visit your website:" -ForegroundColor Cyan
    Write-Host "   Frontend: https://$DOMAIN/" -ForegroundColor White
    Write-Host "   Admin:    https://$DOMAIN/admin`n" -ForegroundColor White
    
    Write-Host "📝 Post-deployment checklist:" -ForegroundColor Yellow
    Write-Host "   [ ] Test homepage" -ForegroundColor Gray
    Write-Host "   [ ] Test admin panel" -ForegroundColor Gray
    Write-Host "   [ ] Test property listings" -ForegroundColor Gray
    Write-Host "   [ ] Test contact form" -ForegroundColor Gray
    Write-Host "   [ ] Check browser console for errors`n" -ForegroundColor Gray
}
catch {
    Write-Host "`n❌ Deployment failed!`n" -ForegroundColor Red
    Write-Host "Error: $_`n" -ForegroundColor Red
    Write-Host "💡 Try manual deployment:" -ForegroundColor Yellow
    Write-Host "   1. Open PowerShell" -ForegroundColor White
    Write-Host "   2. Run: ssh $SSH_USER@$SSH_HOST" -ForegroundColor White
    Write-Host "   3. Enter password: [REDACTED]" -ForegroundColor White
    Write-Host "   4. Follow steps in DEPLOY_TO_PRODUCTION.md`n" -ForegroundColor White
}
