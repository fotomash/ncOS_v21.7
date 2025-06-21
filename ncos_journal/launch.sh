#!/bin/bash
# NCOS Voice Journal System Launcher

echo "🚀 Starting NCOS Voice Journal System..."
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -r requirements.txt -q

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $API_PID $DASHBOARD_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Start API server in background
echo ""
echo "Starting API server on port 8001..."
cd api && python main.py &
API_PID=$!
cd ..

# Wait for API to start
sleep 3

# Check if API is running
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ API failed to start"
    exit 1
fi

echo "✅ API server running"

# Start Streamlit dashboard
echo ""
echo "Starting dashboard on port 8501..."
cd dashboard && streamlit run zbar_journal_dashboard.py --server.port 8501 &
DASHBOARD_PID=$!
cd ..

# Wait for dashboard to start
sleep 3

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Starting voice interface..."
echo "=================================="
echo ""

# Start voice interface (this runs in foreground)
cd core && python ncos_voice_unified.py

# If voice interface exits, cleanup
cleanup
