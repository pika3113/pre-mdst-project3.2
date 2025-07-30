@echo off
echo Starting Wordle Game with Docker...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running or not installed.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Building and starting containers...
docker-compose up --build -d

if %errorlevel% equ 0 (
    echo.
    echo ================================
    echo   Wordle Game is now running!
    echo ================================
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8000
    echo.
    echo Press any key to view logs...
    pause >nul
    docker-compose logs -f
) else (
    echo Error starting containers. Check the output above for details.
    pause
)
