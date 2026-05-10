# Deployment Script for Real Estate Application (PowerShell)
# This script pushes code to GitHub and deploys to production server

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment process..." -ForegroundColor Cyan

# Configuration
$SERVER_USER = "root"
$SERVER_HOST = "187.127.115.70"
$SERVER_PATH = "/opt/stacks/realestate1"
$BRANCH = "main"

# Step 1: Check Git status
Write-Host "`n📋 Checking Git status..." -ForegroundColor Blue
Set-Location backend
git status

$continue = Read-Host "`nDo you want to commit and push? (y/n)"
if ($continue -ne "y") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 1
}

# Step 2: Commit and Push
$commitMsg = Read-Host "Enter commit message"
git add .
git commit -m $commitMsg
git push origin $BRANCH
Write-Host "✅ Pushed to GitHub" -ForegroundColor Green

Set-Location ..

# Step 3: Deploy to Server
Write-Host "`n📥 Deploying backend to server..." -ForegroundColor Blue

$deployScript = @"
cd /opt/stacks/realestate1/backend
echo 'Pulling latest changes...'
git pull origin main
echo 'Installing dependencies...'
pip install -r requirements.txt
echo 'Running migrations...'
python manage.py migrate
echo 'Collecting static files...'
python manage.py collectstatic --noinput
echo '✅ Backend deployment complete!'
"@

ssh "$SERVER_USER@$SERVER_HOST" $deployScript

Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green

# Step 4: Deploy Frontend (optional)
$deployFrontend = Read-Host "`nDo you want to deploy frontend too? (y/n)"
if ($deployFrontend -eq "y") {
    Write-Host "`n📥 Deploying frontend to server..." -ForegroundColor Blue
    
    Set-Location frontend
    git add .
    git commit -m $commitMsg -ErrorAction SilentlyContinue
    git push origin $BRANCH -ErrorAction SilentlyContinue
    Set-Location ..
    
    $frontendScript = @"
cd /opt/stacks/realestate1/frontend
echo 'Pulling latest changes...'
git pull origin main
echo 'Installing dependencies...'
npm install
echo 'Building frontend...'
npm run build
echo '✅ Frontend deployment complete!'
"@
    
    ssh "$SERVER_USER@$SERVER_HOST" $frontendScript
    Write-Host "`n✅ Frontend deployment completed!" -ForegroundColor Green
}

Write-Host "`n🎉 All done! Your application is deployed." -ForegroundColor Green
