@echo off
REM NCOS Voice Journal System Launcher for Windows

echo Starting NCOS Voice Journal System...
echo ==================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Checking dependencies...
pip install -r requirements.txt -q

REM Start API server
echo.
echo Starting API server on port 8001...
start /B cmd /c "cd api && python main.py"

REM Wait for API to start
timeout /t 3 /nobreak > nul

REM Start Streamlit dashboard
echo Starting dashboard on port 8501...
start /B cmd /c "cd dashboard && streamlit run zbar_journal_dashboard.py --server.port 8501"

REM Wait for dashboard to start
timeout /t 3 /nobreak > nul

echo.
echo All services started!
echo.
echo Dashboard: http://localhost:8501
echo API Docs: http://localhost:8001/docs
echo.
echo Starting voice interface...
echo ==================================
echo.

REM Start voice interface
cd core
python ncos_voice_unified.py

REM Cleanup on exit
echo.
echo Shutting down services...
taskkill /F /FI "WindowTitle eq *main.py*" > nul 2>&1
taskkill /F /FI "WindowTitle eq *streamlit*" > nul 2>&1
echo All services stopped
pause
