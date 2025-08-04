@echo off
title Wordle Game Launcher
color 0A
echo ============================================
echo           WORDLE GAME LAUNCHER
echo ============================================
echo.

echo [1/4] Activating Python virtual environment...
cd /d "C:\Users\pika\Desktop\pre-mdst\project 3-2"
call .venv\Scripts\activate.bat

echo [2/4] Starting Backend Server...
cd backend
start "Wordle Backend" cmd /k "python main.py"

echo [3/4] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [4/4] Starting Frontend Server...
cd ..\frontend
start "Wordle Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Press any key to close this launcher...
pause >nul
