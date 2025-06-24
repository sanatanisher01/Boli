@echo off
echo ========================================
echo    Starting BoliBazaar Server
echo ========================================
echo.
echo Server will start at: http://127.0.0.1:8000
echo.
echo Login Credentials:
echo   Admin: admin / admin123
echo   Demo User: demo / demo123
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver