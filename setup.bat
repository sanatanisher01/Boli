@echo off
echo ========================================
echo    BoliBazaar Setup Script
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo Creating database migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo Error creating migrations!
    pause
    exit /b 1
)

echo.
echo Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error applying migrations!
    pause
    exit /b 1
)

echo.
echo Setting up sample data...
python setup.py
if %errorlevel% neq 0 (
    echo Error setting up sample data!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Login Credentials:
echo   Admin: username=admin, password=admin123
echo   Demo User: username=demo, password=demo123
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000
echo.
pause