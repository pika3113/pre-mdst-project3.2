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
echo 🛑 Stopping any existing containers...
docker-compose down

echo.
echo 🔨 Building containers with authentication system...
docker-compose build --no-cache

echo.
echo 🚀 Starting Wordle with Authentication...
docker-compose up -d

echo.
echo 📋 Container Status:
docker-compose ps

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 Testing authentication system...
python test_auth_system.py

echo.
echo ====================================================
echo           🎮 Wordle is Ready! 🎮
echo ====================================================
echo.
echo 🌐 Game URL: http://localhost
echo 🔧 Backend API: http://localhost:8000
echo 📊 Backend Docs: http://localhost:8000/docs
echo.
echo 🔐 Authentication Features:
echo   • Create account with email/password
echo   • Login with Google OAuth
echo   • User profiles and statistics
echo.
echo 📝 To stop the game: docker-compose down
echo 📁 View logs: docker-compose logs -f
echo.
echo Happy Wordling! 🎯
pause
