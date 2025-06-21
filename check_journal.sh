#!/bin/bash

echo "=== ncOS Journal Diagnostic ==="
echo ""

echo "Checking Python environment:"
which python
python --version
echo ""

echo "Checking required packages:"
for pkg in fastapi uvicorn streamlit pandas pyarrow pydantic; do
    if python -c "import $pkg" 2>/dev/null; then
        echo "✓ $pkg installed"
    else
        echo "✗ $pkg NOT installed"
    fi
done
echo ""

echo "Checking ports:"
if lsof -i:8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use by:"
    lsof -i:8000 | grep LISTEN
else
    echo "✓ Port 8000 is available"
fi

if lsof -i:8501 >/dev/null 2>&1; then
    echo "⚠️  Port 8501 is in use by:"
    lsof -i:8501 | grep LISTEN
else
    echo "✓ Port 8501 is available"
fi
echo ""

echo "Checking directory structure:"
if [ -d "ncos_journal" ]; then
    echo "✓ ncos_journal directory exists"
    if [ -f "ncos_journal/api/main.py" ]; then
        echo "✓ API main.py found"
    else
        echo "✗ API main.py NOT found"
    fi
    if [ -f "ncos_journal/dashboard/app.py" ]; then
        echo "✓ Dashboard app.py found"
    else
        echo "✗ Dashboard app.py NOT found"
    fi
else
    echo "✗ ncos_journal directory NOT found"
fi
echo ""

echo "=== End Diagnostic ==="
