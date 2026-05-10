# Simple PowerShell Deployment Script
$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"

Write-Host "🚀 Deploying to production server..." -ForegroundColor Cyan
Write-Host "Password: [REDACTED]" -ForegroundColor Yellow
Write-Host ""

# Backend deployment
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🔧 BACKEND DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

ssh "${SSH_USER}@${SSH_HOST}" @"
cd realestate1-backend || cd /root/realestate1-backend || cd /var/www/realestate1-backend || exit 1
git pull origin main
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn 2>/dev/null || pm2 restart realestate1-backend 2>/dev/null || true
echo 'Backend deployed!'
"@

Write-Host ""

# Frontend deployment  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎨 FRONTEND DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

ssh "${SSH_USER}@${SSH_HOST}" @"
cd realestate1-frontend || cd /root/realestate1-frontend || cd /var/www/realestate1-frontend || exit 1
git pull origin main
npm install
npm run build
pm2 restart realestate1-frontend || pm2 start npm --name realestate1-frontend -- start
pm2 save
echo 'Frontend deployed!'
"@

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
