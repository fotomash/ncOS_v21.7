#!/bin/bash

echo "Stopping ncOS Journal services..."

# Kill processes on ports 8000 and 8501
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

echo "ncOS Journal services stopped."
