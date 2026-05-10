# Deploy frontend fix to production server
# This script removes hardcoded fallback data from components

$SERVER = "187.127.115.70"
$USER = "root"
$PASSWORD = "[REDACTED]"
$PROJECT_PATH = "/opt/stacks/realestate1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Frontend Fix to Production" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create SSH command to execute on server
$sshCommand = @"
cd $PROJECT_PATH/frontend && \
echo '==> Pulling latest changes from GitHub...' && \
git pull origin main && \
echo '' && \
echo '==> Rebuilding frontend container (this will take a few minutes)...' && \
cd $PROJECT_PATH && \
docker compose build --no-cache realestate1-frontend && \
echo '' && \
echo '==> Restarting frontend container...' && \
docker compose up -d realestate1-frontend && \
echo '' && \
echo '==> Waiting for container to be healthy...' && \
sleep 10 && \
echo '' && \
echo '==> Checking container status...' && \
docker ps | grep realestate1-frontend && \
echo '' && \
echo '==> Recent frontend logs:' && \
docker logs realestate1-frontend --tail 50
"@

Write-Host "Connecting to server: $SERVER" -ForegroundColor Yellow
Write-Host ""

# Execute via SSH using sshpass
$env:SSHPASS = $PASSWORD
sshpass -e ssh -o StrictHostKeyChecking=no "$USER@$SERVER" $sshCommand

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Visit https://bijenkhadka.com.au/ to verify the fix" -ForegroundColor White
Write-Host "2. Check that real data from backend is now showing" -ForegroundColor White
Write-Host "3. If still showing fallback data, check browser console for API errors" -ForegroundColor White
Write-Host ""
