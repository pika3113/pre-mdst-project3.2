@echo off
echo ========================================
echo Wordle Authentication Setup Helper
echo ========================================

REM Check if Node.js is available for secret generation
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Generating secure JWT secret key...
    echo.
    for /f %%i in ('node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"') do set JWT_SECRET=%%i
    echo Generated JWT Secret: %JWT_SECRET%
    echo.
) else (
    echo Node.js not found. You'll need to generate a JWT secret manually.
    echo You can use an online generator or install Node.js.
    echo.
    set JWT_SECRET=your-very-secure-jwt-secret-key-change-this-in-production
)

REM Create .env file from template
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul
    
    REM Replace the JWT secret in .env file
    if defined JWT_SECRET (
        powershell -Command "(Get-Content .env) -replace 'your-very-secure-jwt-secret-key-change-this-in-production', '%JWT_SECRET%' | Set-Content .env"
        echo Updated .env file with generated JWT secret.
    )
    
    echo.
    echo ✅ Created .env file!
    echo.
) else (
    echo .env file already exists.
    echo.
)

echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Edit the .env file and add your Google OAuth credentials:
echo    - GOOGLE_CLIENT_ID=your_client_id
echo    - GOOGLE_CLIENT_SECRET=your_client_secret
echo.
echo 2. Get Google OAuth credentials from:
echo    https://console.cloud.google.com/
echo.
echo 3. In Google Console, set redirect URI to:
echo    http://localhost:3000/auth/google/callback
echo.
echo 4. Run: start_wordle_with_auth.bat
echo.
echo ========================================
echo Current .env file contents:
echo ========================================
if exist .env (
    type .env
) else (
    echo No .env file found.
)
echo.
pause
