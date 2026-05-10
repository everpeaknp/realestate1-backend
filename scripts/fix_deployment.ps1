# PowerShell script to fix the services table issue on production server

$SERVER = "root@187.127.115.70"
$PASSWORD = "[REDACTED]"
$APP_DIR = "/opt/stacks/realestate1"
$BACKEND_DIR = "$APP_DIR/backend"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fixing Services Table on Production" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Step 1: Copy the fix script to server
Write-Host ""
Write-Host "Step 1: Uploading fix script to server..." -ForegroundColor Yellow
scp fix_services_table.py "${SERVER}:${BACKEND_DIR}/"

# Step 2: Stop the backend container
Write-Host ""
Write-Host "Step 2: Stopping backend container..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR && docker compose stop realestate1-backend"

# Step 3: Run the fix script
Write-Host ""
Write-Host "Step 3: Running fix script..." -ForegroundColor Yellow
ssh $SERVER "cd $BACKEND_DIR && docker compose run --rm realestate1-backend python fix_services_table.py"

# Step 4: Run migrations
Write-Host ""
Write-Host "Step 4: Running migrations..." -ForegroundColor Yellow
ssh $SERVER "cd $BACKEND_DIR && docker compose run --rm realestate1-backend python manage.py migrate services"

# Step 5: Start containers
Write-Host ""
Write-Host "Step 5: Starting containers..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR && docker compose up -d"

# Step 6: Check container status
Write-Host ""
Write-Host "Step 6: Checking container status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
ssh $SERVER "cd $APP_DIR && docker compose ps"

# Step 7: Check backend logs
Write-Host ""
Write-Host "Step 7: Checking backend logs (last 20 lines)..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR && docker compose logs --tail=20 realestate1-backend"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment fix completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://187.127.115.70:3000" -ForegroundColor White
Write-Host "Backend: http://187.127.115.70:8000" -ForegroundColor White
