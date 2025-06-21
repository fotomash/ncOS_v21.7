#!/bin/bash

# ncOS Journal Launch Script - Phoenix Edition

echo "🚀 Starting ncOS Journal System..."

# Create necessary directories
mkdir -p data logs

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements_journal.txt

# Start API server
echo "Starting API server on port 8001..."
cd api
python main.py > ../logs/api.log 2>&1 &
API_PID=$!
cd ..

# Wait for API to start
sleep 3

# Start Dashboard
echo "Starting Dashboard on port 8501..."
cd dashboard
streamlit run app.py --server.port 8501 > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
cd ..

echo ""
echo "✨ ncOS Journal System is running!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔌 API: http://localhost:8001"
echo "📝 API Docs: http://localhost:8001/docs"
echo ""
echo "Process IDs:"
echo "  API: $API_PID"
echo "  Dashboard: $DASHBOARD_PID"
