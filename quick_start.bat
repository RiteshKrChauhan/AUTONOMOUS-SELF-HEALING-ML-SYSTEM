@echo off
REM Quick Start Script for Windows

echo ==========================================
echo 🚀 AUTONOMOUS ML SYSTEM - QUICK START
echo ==========================================
echo.

REM Step 1: Verify system
echo Step 1: Verifying system...
python verify_system.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Verification failed. Please fix issues above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Step 2: Running main pipeline...
echo ==========================================
echo.

python main.py

echo.
echo ==========================================
echo ✅ PIPELINE COMPLETE!
echo ==========================================
echo.
echo 📁 Check generated files:
echo   - logs\          (governance logs)
echo   - plots\         (visualizations)
echo   - mlflow.db      (experiment tracking)
echo.
echo 🔍 View MLflow UI:
echo   mlflow ui
echo   Then open: http://localhost:5000
echo.
echo 🎉 System is working!
echo.
pause
