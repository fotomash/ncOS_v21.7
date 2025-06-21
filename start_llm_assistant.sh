#!/bin/bash
# ncOS Journal LLM Assistant Auto-Start Script

echo "Starting ncOS Journal LLM Assistant..."

# Set environment variables
export JOURNAL_DATA_DIR="./journal_data"
export LOG_DIR="$JOURNAL_DATA_DIR/logs"
export LLM_PORT=8002

# Create necessary directories
mkdir -p $LOG_DIR

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY not set. LLM will run in fallback mode."
    echo "To use full LLM features, set: export OPENAI_API_KEY='your-key-here'"
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill existing LLM assistant if running
if check_port $LLM_PORT; then
    echo "Stopping existing LLM assistant on port $LLM_PORT..."
    lsof -ti:$LLM_PORT | xargs kill -9 2>/dev/null
    sleep 2
fi

# Start the LLM assistant
echo "Starting LLM assistant on port $LLM_PORT..."
nohup python llm_assistant.py > $LOG_DIR/llm_assistant.log 2>&1 &
LLM_PID=$!

# Wait for service to start
sleep 3

# Check if service started successfully
if check_port $LLM_PORT; then
    echo "✓ LLM Assistant started successfully (PID: $LLM_PID)"
    echo "  Access at: http://localhost:$LLM_PORT"
    echo "  WebSocket: ws://localhost:$LLM_PORT/ws"
    
    # Save PID for stop script
    echo $LLM_PID > $JOURNAL_DATA_DIR/llm_assistant.pid
else
    echo "✗ Failed to start LLM Assistant"
    exit 1
fi

# Optional: Start with main journal system
if [ "$1" == "--with-journal" ]; then
    echo "Starting main journal system..."
    ./launch_fixed.sh
fi

echo "LLM Assistant is ready!"
