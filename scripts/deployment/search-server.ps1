# Search Server for All Folders
# Server: root@187.127.115.70
# Password: [REDACTED]

$SSH_USER = "root"
$SSH_HOST = "187.127.115.70"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Searching Server for All Folders" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Server: $SSH_HOST" -ForegroundColor Yellow
Write-Host "Password: [REDACTED]`n" -ForegroundColor Yellow

# Create search script with Unix line endings
$searchScript = @'
#!/bin/bash
echo "========================================"
echo "COMPREHENSIVE SERVER SEARCH"
echo "========================================"
echo ""

echo "1. Searching for realestate folders..."
echo "----------------------------------------"
find / -maxdepth 4 -type d -name "*realestate*" 2>/dev/null
echo ""

echo "2. Contents of /var/www/"
echo "----------------------------------------"
ls -la /var/www/ 2>/dev/null || echo "Directory not found"
echo ""

echo "3. Contents of /root/"
echo "----------------------------------------"
ls -la /root/ 2>/dev/null || echo "Directory not found"
echo ""

echo "4. Contents of /opt/"
echo "----------------------------------------"
ls -la /opt/ 2>/dev/null || echo "Directory not found"
echo ""

echo "5. Contents of /home/"
echo "----------------------------------------"
ls -la /home/ 2>/dev/null || echo "Directory not found"
echo ""

echo "6. Git repositories"
echo "----------------------------------------"
find /var/www /root /opt /home -maxdepth 3 -name ".git" -type d 2>/dev/null | sed 's/\.git$//'
echo ""

echo "7. Django projects (manage.py)"
echo "----------------------------------------"
find /var/www /root /opt /home -maxdepth 3 -name "manage.py" -type f 2>/dev/null | xargs dirname 2>/dev/null
echo ""

echo "8. Node.js projects (package.json)"
echo "----------------------------------------"
find /var/www /root /opt /home -maxdepth 3 -name "package.json" -type f 2>/dev/null | xargs dirname 2>/dev/null
echo ""

echo "9. PM2 Processes"
echo "----------------------------------------"
if command -v pm2 &> /dev/null; then
    pm2 list
    echo ""
    pm2 info realestate1-frontend 2>/dev/null || echo "realestate1-frontend not found in PM2"
    echo ""
    pm2 info realestate1-backend 2>/dev/null || echo "realestate1-backend not found in PM2"
else
    echo "PM2 not installed"
fi
echo ""

echo "10. Systemd Services"
echo "----------------------------------------"
systemctl list-units --type=service --no-pager | grep -E 'gunicorn|django|realestate|nextjs|node' || echo "No relevant services found"
echo ""

echo "11. Nginx Configuration"
echo "----------------------------------------"
echo "Sites available:"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "Directory not found"
echo ""
echo "Sites enabled:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "Directory not found"
echo ""

echo "12. Running Processes"
echo "----------------------------------------"
echo "Python processes:"
ps aux | grep python | grep -v grep | head -5
echo ""
echo "Node processes:"
ps aux | grep node | grep -v grep | head -5
echo ""

echo "13. Listening Ports"
echo "----------------------------------------"
echo "Port 8000 (Backend):"
lsof -i :8000 2>/dev/null || echo "Nothing listening"
echo ""
echo "Port 3000 (Frontend):"
lsof -i :3000 2>/dev/null || echo "Nothing listening"
echo ""
echo "Port 80 (HTTP):"
lsof -i :80 2>/dev/null || echo "Nothing listening"
echo ""
echo "Port 443 (HTTPS):"
lsof -i :443 2>/dev/null || echo "Nothing listening"
echo ""

echo "========================================"
echo "SEARCH COMPLETE"
echo "========================================"
'@

Write-Host "Connecting to server and searching..." -ForegroundColor Yellow
Write-Host "(Enter password when prompted: [REDACTED])`n" -ForegroundColor Green

try {
    # Execute the search
    $output = $searchScript | ssh "${SSH_USER}@${SSH_HOST}" "bash -s" 2>&1
    
    # Display output
    Write-Host $output
    
    # Save to file
    $output | Out-File -FilePath "server-search-results.txt" -Encoding UTF8
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Search completed!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    Write-Host "Results saved to: server-search-results.txt`n" -ForegroundColor Cyan
    
    # Try to extract key information
    Write-Host "KEY FINDINGS:" -ForegroundColor Yellow
    Write-Host "-------------`n" -ForegroundColor Yellow
    
    if ($output -match "realestate1-backend") {
        Write-Host "✓ Found realestate1-backend" -ForegroundColor Green
    } else {
        Write-Host "✗ realestate1-backend not found" -ForegroundColor Red
    }
    
    if ($output -match "realestate1-frontend") {
        Write-Host "✓ Found realestate1-frontend" -ForegroundColor Green
    } else {
        Write-Host "✗ realestate1-frontend not found" -ForegroundColor Red
    }
    
    Write-Host "`nCheck server-search-results.txt for full details`n" -ForegroundColor Cyan
}
catch {
    Write-Host "`nError: $_`n" -ForegroundColor Red
    Write-Host "Please try manual search using commands in find-all-folders.txt`n" -ForegroundColor Yellow
}
