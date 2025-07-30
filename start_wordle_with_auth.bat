@echo off
echo ========================================
echo Starting Wordle with Authentication
echo ========================================

REM Check if .env file exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo.
    echo For full authentication features, you need to:
    echo 1. Copy .env.example to .env
    echo 2. Set up Google OAuth credentials
    echo 3. Generate a secure JWT secret key
    echo.
    echo The app will still work with basic email/password auth,
    echo but Google OAuth will be disabled.
    echo.
    pause
)

echo.
echo Building and starting containers...
echo This may take a few minutes on first run.
echo.

REM Build and start containers
docker-compose down
docker-compose build
docker-compose up -d

REM Wait a moment for services to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Wordle is starting up!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
echo Features available:
echo ✅ Classic Wordle gameplay
echo ✅ User registration and login
echo ✅ Google OAuth (if configured)
echo ✅ User profiles and avatars
echo ✅ Persistent game statistics
echo.

REM Check if services are healthy
echo Checking service health...
timeout /t 10 /nobreak >nul

docker-compose ps

echo.
echo Setup complete! Check the URLs above.
echo.
echo To stop the application: docker-compose down
echo To view logs: docker-compose logs -f
echo.
pause
