# PowerShell script to sync local backend/media directory to production server

Write-Host "=== Syncing Media Files to Production ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SERVER = "root@187.127.115.70"
$REMOTE_MEDIA_DIR = "/opt/data/realestate1/backend/media"
$LOCAL_MEDIA_DIR = "backend/media"

# Check if local media directory exists
if (-not (Test-Path $LOCAL_MEDIA_DIR)) {
    Write-Host "Error: Local media directory not found: $LOCAL_MEDIA_DIR" -ForegroundColor Red
    exit 1
}

Write-Host "Local directory: $LOCAL_MEDIA_DIR"
Write-Host "Remote directory: $REMOTE_MEDIA_DIR"
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to sync media files to production? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Sync cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Syncing media files..." -ForegroundColor Green

# Use rsync if available (via WSL or Git Bash), otherwise use scp
$rsyncAvailable = Get-Command rsync -ErrorAction SilentlyContinue

if ($rsyncAvailable) {
    Write-Host "Using rsync for efficient sync..."
    rsync -av --progress "$LOCAL_MEDIA_DIR/" "${SERVER}:${REMOTE_MEDIA_DIR}/"
} else {
    Write-Host "rsync not found. Using scp (this may take longer)..."
    Write-Host "Note: Install rsync via WSL or Git Bash for faster syncing."
    scp -r "$LOCAL_MEDIA_DIR/*" "${SERVER}:${REMOTE_MEDIA_DIR}/"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to sync media files" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Setting correct permissions..." -ForegroundColor Green
ssh $SERVER "chown -R 1000:1000 $REMOTE_MEDIA_DIR && chmod -R 755 $REMOTE_MEDIA_DIR"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to set permissions. You may need to do this manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Verifying sync..." -ForegroundColor Green
Write-Host "Local file count:"
(Get-ChildItem -Path $LOCAL_MEDIA_DIR -Recurse -File).Count

Write-Host "Remote file count:"
ssh $SERVER "find $REMOTE_MEDIA_DIR -type f | wc -l"

Write-Host ""
Write-Host "Step 4: Testing media file access..." -ForegroundColor Green
Write-Host "Testing: https://bijenkhadka.com.au/media/cms/logos/b.png"
$response = Invoke-WebRequest -Uri "https://bijenkhadka.com.au/media/cms/logos/b.png" -Method Head -UseBasicParsing
Write-Host "Status: $($response.StatusCode) $($response.StatusDescription)"
Write-Host "Content-Type: $($response.Headers['Content-Type'])"

Write-Host ""
Write-Host "=== Sync Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Media files have been synced to production."
Write-Host "You can verify by visiting: https://bijenkhadka.com.au/media/"
