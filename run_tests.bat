@echo off
echo ==========================================
echo  Running Unit Tests
echo ==========================================
echo.

echo [1/2] Installing test dependencies...
python -m pip install -r requirements-test.txt -q

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install test dependencies
    pause
    exit /b 1
)

echo.
echo [2/2] Running tests...
python -m pytest tests/ -v

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Some tests failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  All Tests Passed!
echo ==========================================
echo.
pause
