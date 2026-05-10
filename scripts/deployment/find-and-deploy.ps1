# Find Projects and Deploy Script
# Server: root@187.127.115.70
# Password: [REDACTED]

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"
$SSH_PASS = "[REDACTED]"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Finding Projects and CI/CD Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Server: $SSH_HOST" -ForegroundColor Yellow
Write-Host "Password: $SSH_PASS`n" -ForegroundColor Yellow

# Create the search script
$searchScript = @'
#!/bin/bash

echo "=========================================="
echo "1. FINDING PROJECT DIRECTORIES"
echo "=========================================="

# Search for backend
echo "Searching for realestate1-backend..."
BACKEND=$(find /root /var/www /opt /home -maxdepth 3 -name "realestate1-backend" -type d 2>/dev/null | head -1)

if [ -n "$BACKEND" ]; then
    echo "BACKEND_FOUND: $BACKEND"
    cd "$BACKEND"
    echo "BACKEND_GIT_BRANCH: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "BACKEND_LAST_COMMIT: $(git log --oneline -1 2>/dev/null || echo 'unknown')"
else
    echo "BACKEND_FOUND: NOT_FOUND"
fi

# Search for frontend
echo ""
echo "Searching for realestate1-frontend..."
FRONTEND=$(find /root /var/www /opt /home -maxdepth 3 -name "realestate1-frontend" -type d 2>/dev/null | head -1)

if [ -n "$FRONTEND" ]; then
    echo "FRONTEND_FOUND: $FRONTEND"
    cd "$FRONTEND"
    echo "FRONTEND_GIT_BRANCH: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "FRONTEND_LAST_COMMIT: $(git log --oneline -1 2>/dev/null || echo 'unknown')"
else
    echo "FRONTEND_FOUND: NOT_FOUND"
fi

echo ""
echo "=========================================="
echo "2. CHECKING CI/CD SETUP"
echo "=========================================="

# Check GitHub Actions
if [ -n "$BACKEND" ] && [ -d "$BACKEND/.github/workflows" ]; then
    echo "BACKEND_GITHUB_ACTIONS: YES"
    ls "$BACKEND/.github/workflows/"
else
    echo "BACKEND_GITHUB_ACTIONS: NO"
fi

if [ -n "$FRONTEND" ] && [ -d "$FRONTEND/.github/workflows" ]; then
    echo "FRONTEND_GITHUB_ACTIONS: YES"
    ls "$FRONTEND/.github/workflows/"
else
    echo "FRONTEND_GITHUB_ACTIONS: NO"
fi

# Check systemd services
echo ""
echo "SYSTEMD_SERVICES:"
systemctl list-units --type=service --no-pager | grep -E 'gunicorn|django|realestate|nextjs' || echo "None found"

# Check PM2
echo ""
echo "PM2_PROCESSES:"
if command -v pm2 &> /dev/null; then
    pm2 list
else
    echo "PM2 not installed"
fi

# Check backend service status
echo ""
echo "=========================================="
echo "3. SERVICE STATUS"
echo "=========================================="

if systemctl is-active --quiet gunicorn; then
    echo "GUNICORN_STATUS: RUNNING"
else
    echo "GUNICORN_STATUS: NOT_RUNNING"
fi

if systemctl is-active --quiet nginx; then
    echo "NGINX_STATUS: RUNNING"
else
    echo "NGINX_STATUS: NOT_RUNNING"
fi

# Check what's listening on port 8000
echo ""
echo "PORT_8000:"
lsof -i :8000 2>/dev/null || echo "Nothing listening"

# Check what's listening on port 3000
echo ""
echo "PORT_3000:"
lsof -i :3000 2>/dev/null || echo "Nothing listening"

echo ""
echo "=========================================="
echo "SEARCH COMPLETE"
echo "=========================================="
'@

# Save script to temp file
$tempFile = New-TemporaryFile
$searchScript | Out-File -FilePath $tempFile.FullName -Encoding ASCII -NoNewline

try {
    Write-Host "Connecting to server and searching..." -ForegroundColor Yellow
    Write-Host "(Enter password when prompted: $SSH_PASS)`n" -ForegroundColor Green
    
    # Upload and execute script
    $output = Get-Content $tempFile.FullName | ssh "${SSH_USER}@${SSH_HOST}" "bash -s" 2>&1
    
    Write-Host $output
    
    # Parse output
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUMMARY" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    if ($output -match "BACKEND_FOUND: (.+)") {
        $backendPath = $matches[1]
        if ($backendPath -ne "NOT_FOUND") {
            Write-Host "Backend Location: $backendPath" -ForegroundColor Green
        } else {
            Write-Host "Backend Location: NOT FOUND" -ForegroundColor Red
        }
    }
    
    if ($output -match "FRONTEND_FOUND: (.+)") {
        $frontendPath = $matches[1]
        if ($frontendPath -ne "NOT_FOUND") {
            Write-Host "Frontend Location: $frontendPath" -ForegroundColor Green
        } else {
            Write-Host "Frontend Location: NOT FOUND" -ForegroundColor Red
        }
    }
    
    if ($output -match "GUNICORN_STATUS: (.+)") {
        $status = $matches[1]
        if ($status -eq "RUNNING") {
            Write-Host "Backend Service: RUNNING" -ForegroundColor Green
        } else {
            Write-Host "Backend Service: NOT RUNNING (This is why you see 502 error!)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n"
}
catch {
    Write-Host "`nError: $_`n" -ForegroundColor Red
}
finally {
    Remove-Item $tempFile.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host "Next steps saved to: SERVER_INFO.txt`n" -ForegroundColor Cyan
