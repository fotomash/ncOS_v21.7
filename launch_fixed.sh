#!/bin/bash

echo "Starting ncOS Journal v2.0..."

# Kill any existing processes on ports 8000 and 8501
echo "Checking for existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start API server
echo "Starting API server..."
cd "$SCRIPT_DIR"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start dashboard
echo "Starting dashboard..."
cd "$SCRIPT_DIR"
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

echo ""
echo "ncOS Journal is running!"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Dashboard: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop..."

# Function to handle cleanup
cleanup() {
    echo ""
    echo "Stopping ncOS Journal..."
    kill $API_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    # Also kill any lingering processes
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    echo "ncOS Journal stopped."
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT

# Wait indefinitely
while true; do
    sleep 1
done
