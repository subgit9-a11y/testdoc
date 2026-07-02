@echo off
echo ============================================================
echo Firebase Authentication Migration - Application Startup
echo ============================================================
echo.

echo Checking Firebase credential file...
if exist "firebase-service-account.json" (
    echo [OK] Firebase credential file found
) else (
    if exist "aiastra\firebase-service-account.json" (
        echo [WARNING] Firebase credential file found in aiastra folder
        echo Consider copying it to root directory
    ) else (
        echo [ERROR] Firebase credential file not found!
        echo Please ensure firebase-service-account.json exists
        pause
        exit /b 1
    )
)

echo.
echo Starting Astra application with Firebase Authentication...
echo.

python main.py

pause
