@echo off
echo =========================================
echo  Infinite Research - Windows Installer
echo =========================================
echo.

echo [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [2/3] Testing installation...
python test_setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Setup test failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [3/3] Testing parallel search (no LMStudio needed)...
python test_parallel_search.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Search test failed. Check internet connection.
)

echo.
echo =========================================
echo  Installation Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Start LMStudio and load a model
echo 2. Start the server in LMStudio
echo 3. Edit config.yaml with your model name
echo 4. Run: python research_orchestrator.py "Your topic"
echo.
pause
