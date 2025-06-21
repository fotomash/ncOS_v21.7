# ncOS LLM Assistant Setup Instructions

## Quick Start (Local)

1. **Set OpenAI API Key** (optional but recommended):
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x start_llm_assistant.sh
   ```

3. **Start LLM Assistant only**:
   ```bash
   ./start_llm_assistant.sh
   ```

4. **Start with full journal system**:
   ```bash
   ./start_llm_assistant.sh --with-journal
   ```

## Auto-Start Options

### Option 1: Systemd Service (Linux)
```bash
# Copy service file
sudo cp ncos-llm.service /etc/systemd/system/

# Edit to add your API key and paths
sudo systemctl edit ncos-llm.service

# Enable and start
sudo systemctl enable ncos-llm.service
sudo systemctl start ncos-llm.service
```

### Option 2: Docker Compose
```bash
# Set API key in .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Start all services
docker-compose up -d
```

### Option 3: Cron Job
```bash
# Add to crontab
crontab -e

# Add this line:
@reboot cd /path/to/ncos_journal && ./start_llm_assistant.sh --with-journal
```

## Integration with Dashboard

Add to your `app.py`:
```python
from llm_dashboard_integration import add_llm_chat_to_dashboard

# In your main dashboard code:
add_llm_chat_to_dashboard()
```

## API Endpoints

- Chat: `POST http://localhost:8002/chat`
- WebSocket: `ws://localhost:8002/ws`
- Suggestions: `GET http://localhost:8002/suggestions`
- Clear History: `POST http://localhost:8002/clear-history`

## Features

1. **Contextual Assistance**: LLM understands your journal context
2. **Trade Logging Help**: Guides you through comprehensive logging
3. **Pattern Recognition**: Identifies trading patterns in your data
4. **Performance Analysis**: Provides insights on your trading
5. **Real-time Chat**: WebSocket support for instant responses

## Troubleshooting

- **No API Key**: System works in fallback mode with basic responses
- **Port Conflict**: Change LLM_PORT in start script
- **Connection Issues**: Check if journal API is running on port 8000
