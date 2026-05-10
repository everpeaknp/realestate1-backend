@echo off
echo ==========================================
echo   Restarting Django Backend
echo ==========================================
echo.

echo Step 1: Finding Python processes...
tasklist | findstr python

echo.
echo Step 2: You need to manually restart the backend.
echo.
echo OPTION 1: If backend is running in a terminal
echo   - Go to the terminal running the backend
echo   - Press Ctrl+C to stop it
echo   - Run: python backend/manage.py runserver
echo.
echo OPTION 2: If backend is running as a service
echo   - Stop the service
echo   - Start it again
echo.
echo OPTION 3: Kill and restart
echo   - Find the Python process ID from the list above
echo   - Run: taskkill /PID [process_id] /F
echo   - Then run: python backend/manage.py runserver
echo.
echo After restarting, test the chatbot at http://localhost:3000
echo.
pause
