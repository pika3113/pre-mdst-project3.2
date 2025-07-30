@echo off
echo ================================
echo    Wordle Game Setup Check
echo ================================
echo.

REM Check Docker
echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Docker is installed
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Docker is running
    ) else (
        echo ✗ Docker is installed but not running
        echo   Please start Docker Desktop
    )
) else (
    echo ✗ Docker is not installed
    echo   Please install Docker Desktop from https://docker.com
)

echo.

REM Check if in correct directory
if exist "docker-compose.yml" (
    echo ✓ Found docker-compose.yml
) else (
    echo ✗ docker-compose.yml not found
    echo   Please run this from the project root directory
)

echo.

REM Check project structure
echo Checking project structure...
if exist "backend\Dockerfile" (
    echo ✓ Backend Dockerfile exists
) else (
    echo ✗ Backend Dockerfile missing
)

if exist "frontend\Dockerfile" (
    echo ✓ Frontend Dockerfile exists
) else (
    echo ✗ Frontend Dockerfile missing
)

if exist "backend\main.py" (
    echo ✓ Backend main.py exists
) else (
    echo ✗ Backend main.py missing
)

if exist "frontend\src\App.jsx" (
    echo ✓ Frontend App.jsx exists
) else (
    echo ✗ Frontend App.jsx missing
)

echo.
echo ================================
echo Setup check complete!
echo.
echo To start the game with Docker:
echo   start_docker.bat
echo.
echo To start manually:
echo   start_wordle_game.bat
echo ================================
pause
