#!/bin/bash
# Execute Phoenix Session Merge (v2 - Smarter Path Detection)

echo "🔥 Phoenix Session Merge Execution Script (v2)"
echo "=========================================="

# --- Smarter Path Detection ---
# Find the correct NCOS project root where the 'src' and 'config' dirs live.
NCOS_ROOT_DIR=$(find . -type d -name 'ncOS_v21.7-*' -print -quit)

if [ -n "$NCOS_ROOT_DIR" ]; then
    echo "✅ Found project root at: $NCOS_ROOT_DIR"
    cd "$NCOS_ROOT_DIR"
else
    echo "⚠️ Could not find nested project directory. Running in current directory."
fi
# --- End of Path Detection ---


# Check if we're in the right directory (now checking for src/agents)
if [ ! -d "config" ] || [ ! -d "src/agents" ]; then
    echo "❌ Error: Could not find 'config' and 'src/agents' directories."
    echo "   Please ensure you are in the correct NCOS project structure."
    exit 1
fi

# Create Phoenix structure
echo "📁 Creating Phoenix directory structure..."
mkdir -p phoenix_session/core
mkdir -p phoenix_session/adapters

# Copy optimized Phoenix controller from the parent directory
echo "📦 Installing Phoenix components..."
# Note: Adjust the path if ncos_session_optimized.py is not in the parent directory
cp ../ncos_session_optimized.py phoenix_session/core/

# Create __init__ files
echo '"""Phoenix Session Module"""' > phoenix_session/__init__.py
echo '"""Phoenix Core Module"""' > phoenix_session/core/__init__.py
echo '"""Phoenix Adapters Module"""' > phoenix_session/adapters/__init__.py

echo "✅ Phoenix Session scaffolding complete!"
echo "   Next, follow Step 3 from the guide to implement the adapters."