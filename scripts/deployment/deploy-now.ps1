# Deploy to bijenkhadka.com.au
# Server: root@187.127.115.70 | Password: [REDACTED]

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Deploying to bijenkhadka.com.au" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Server: $SSH_HOST" -ForegroundColor Yellow
Write-Host "Password: [REDACTED]`n" -ForegroundColor Yellow

Write-Host "Connecting to server..." -ForegroundColor Yellow
Write-Host "(Enter password when prompted)`n" -ForegroundColor Green

# Deployment script
$script = @'
#!/bin/bash
set -e

echo "Finding project directories..."

# Find backend
for dir in /var/www/realestate1-backend /root/realestate1-backend /opt/realestate1-backend; do
    if [ -d "$dir" ]; then
        BACKEND_DIR="$dir"
        break
    fi
done

# Find frontend
for dir in /var/www/realestate1-frontend /root/realestate1-frontend /opt/realestate1-frontend; do
    if [ -d "$dir" ]; then
        FRONTEND_DIR="$dir"
        break
    fi
done

if [ -z "$BACKEND_DIR" ] || [ -z "$FRONTEND_DIR" ]; then
    echo "ERROR: Could not find project directories"
    echo "Searching..."
    find /var/www /root /opt -name "realestate1-*" -type d 2>/dev/null
    exit 1
fi

echo "Backend: $BACKEND_DIR"
echo "Frontend: $FRONTEND_DIR"
echo ""

echo "========================================"
echo "DEPLOYING BACKEND"
echo "========================================"
cd "$BACKEND_DIR"
git pull origin main
[ -d venv ] && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn 2>/dev/null || pm2 restart realestate1-backend 2>/dev/null || true
echo "Backend deployed!"
echo ""

echo "========================================"
echo "DEPLOYING FRONTEND"
echo "========================================"
cd "$FRONTEND_DIR"
git pull origin main
npm install
npm run build
pm2 restart realestate1-frontend || pm2 start npm --name realestate1-frontend -- start
pm2 save
echo "Frontend deployed!"
echo ""

echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo "Website: https://bijenkhadka.com.au/"
echo "Admin: https://bijenkhadka.com.au/admin"
'@

# Save and execute
$tempFile = New-TemporaryFile
$script | Out-File -FilePath $tempFile.FullName -Encoding ASCII -NoNewline

try {
    Get-Content $tempFile.FullName | ssh "${SSH_USER}@${SSH_HOST}" "bash -s"
    Write-Host "`nDeployment completed successfully!`n" -ForegroundColor Green
    Write-Host "Visit: https://bijenkhadka.com.au/`n" -ForegroundColor Cyan
}
catch {
    Write-Host "`nDeployment failed: $_`n" -ForegroundColor Red
    Write-Host "Try manual deployment - see DEPLOY_TO_PRODUCTION.md`n" -ForegroundColor Yellow
}
finally {
    Remove-Item $tempFile.FullName -Force -ErrorAction SilentlyContinue
}
