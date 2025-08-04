@echo off
echo ====================================================
echo         Wordle Game with Authentication
echo ====================================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo.
    echo Run setup_auth.bat first to create your .env file
    echo with JWT secret and Google OAuth credentials.
    echo.
    pause
    exit /b 1
)

echo ✅ Found .env file
echo.

REM Stop any existing containers
echo Stopping any existing containers...
docker-compose down

echo.
echo Building containers
docker-compose build --no-cache

echo.
echo Starting...
docker-compose up -d

echo.
echo Container Status:
docker-compose ps

echo.
echo ====================================================
echo                       Ready! 
echo ====================================================
echo.
echo Game URL: http://localhost
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo.
echo Authentication Features:
echo   • Create account with email/password
echo   • Login with Google OAuth
echo   • User profiles and statistics
echo.
echo To stop the game: docker-compose down
echo View logs: docker-compose logs -f
echo.
pause
