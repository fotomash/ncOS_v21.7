# Create an auto-starting LLM assistant for ncOS Journal System

# 1. Create the LLM assistant service
llm_assistant_code = '''#!/usr/bin/env python3
"""
ncOS Journal LLM Assistant
Auto-starting AI assistant for trade journaling and analysis
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
@dataclass
class LLMConfig:
    """LLM Assistant Configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt_file: str = "llm_system_prompt.txt"
    journal_api_url: str = "http://localhost:8000"
    
    def load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            with open(self.system_prompt_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self.get_default_prompt()
    
    def get_default_prompt(self) -> str:
        """Default system prompt"""
        return """You are the ncOS Journal Assistant, an AI specialized in helping traders with:
1. Logging trades and market observations
2. Analyzing patterns using ZBAR methodology
3. Detecting strategy conflicts
4. Providing performance insights
5. Maintaining trading discipline through systematic journaling

Always encourage detailed journaling and help users identify patterns in their trading behavior."""

# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    include_journal_data: bool = True

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
    journal_actions: Optional[List[Dict[str, Any]]] = None

class JournalAction(BaseModel):
    action: str  # log_trade, add_observation, analyze_pattern
    data: Dict[str, Any]

# LLM Assistant Class
class JournalLLMAssistant:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.api_key) if config.api_key else None
        self.system_prompt = config.load_system_prompt()
        self.conversation_history: List[ChatMessage] = []
        self.journal_client = httpx.AsyncClient(base_url=config.journal_api_url)
        
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process user message and generate response"""
        try:
            # Add context from journal if requested
            context = ""
            if request.include_journal_data:
                context = await self._get_journal_context()
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Current journal context: {context}"}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": msg.role, "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": request.message})
            
            # Get LLM response
            if self.client:
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                assistant_message = response.choices[0].message.content
            else:
                # Fallback for no API key
                assistant_message = self._generate_fallback_response(request.message)
            
            # Parse for journal actions
            journal_actions = self._parse_journal_actions(assistant_message)
            
            # Execute journal actions
            if journal_actions:
                await self._execute_journal_actions(journal_actions)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(request.message, assistant_message)
            
            # Update conversation history
            self.conversation_history.append(
                ChatMessage(role="user", content=request.message, timestamp=datetime.now())
            )
            self.conversation_history.append(
                ChatMessage(role="assistant", content=assistant_message, timestamp=datetime.now())
            )
            
            return ChatResponse(
                response=assistant_message,
                suggestions=suggestions,
                journal_actions=journal_actions
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                response=f"I encountered an error: {str(e)}. Please try again.",
                suggestions=["Check your API connection", "Verify journal system is running"]
            )
    
    async def _get_journal_context(self) -> str:
        """Get recent journal context"""
        try:
            # Get recent entries
            response = await self.journal_client.get("/journal/entries?limit=5")
            entries = response.json()
            
            # Get today's analysis
            today = datetime.now().strftime("%Y-%m-%d")
            analysis_response = await self.journal_client.get(f"/journal/analysis?date={today}")
            analysis = analysis_response.json()
            
            context = f"Recent entries: {len(entries)} trades/observations. "
            context += f"Today's performance: {analysis.get('summary', 'No data yet')}"
            
            return context
        except Exception as e:
            logger.error(f"Error getting journal context: {e}")
            return "Journal context unavailable"
    
    def _parse_journal_actions(self, message: str) -> List[Dict[str, Any]]:
        """Parse message for journal actions"""
        actions = []
        
        # Simple pattern matching for actions
        if "log trade" in message.lower() or "record trade" in message.lower():
            actions.append({
                "action": "prompt_trade_log",
                "data": {"detected": "trade logging request"}
            })
        
        if "analyze" in message.lower() and "pattern" in message.lower():
            actions.append({
                "action": "trigger_analysis",
                "data": {"type": "pattern_analysis"}
            })
        
        return actions
    
    async def _execute_journal_actions(self, actions: List[Dict[str, Any]]):
        """Execute detected journal actions"""
        for action in actions:
            try:
                if action["action"] == "prompt_trade_log":
                    # Could trigger UI prompt or prepare entry form
                    logger.info("Trade logging prompt triggered")
                elif action["action"] == "trigger_analysis":
                    # Could start analysis process
                    logger.info("Analysis triggered")
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")
    
    def _generate_suggestions(self, user_message: str, assistant_response: str) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        # Context-based suggestions
        if "trade" in user_message.lower():
            suggestions.extend([
                "Review today's trades",
                "Analyze win/loss patterns",
                "Check for strategy conflicts"
            ])
        
        if "pattern" in user_message.lower():
            suggestions.extend([
                "Run ZBAR analysis",
                "Check Wyckoff accumulation",
                "Identify liquidity zones"
            ])
        
        if "performance" in user_message.lower():
            suggestions.extend([
                "Generate weekly report",
                "Review emotional tags",
                "Analyze best performing setups"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate response without LLM API"""
        responses = {
            "trade": "I can help you log that trade. Please provide: symbol, entry price, stop loss, and take profit.",
            "analyze": "I'll help analyze your trading patterns. What timeframe would you like to review?",
            "performance": "Let me check your recent performance. Would you like a daily or weekly summary?",
            "help": "I can assist with: trade logging, pattern analysis, performance reviews, and journal management."
        }
        
        for key, response in responses.items():
            if key in message.lower():
                return response
        
        return "I'm here to help with your trading journal. What would you like to do?"

# FastAPI Application
app = FastAPI(title="ncOS Journal LLM Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant
config = LLMConfig()
assistant = JournalLLMAssistant(config)

@app.get("/")
async def root():
    return {
        "service": "ncOS Journal LLM Assistant",
        "status": "running",
        "model": config.model,
        "api_configured": bool(config.api_key)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message"""
    return await assistant.process_message(request)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = ChatRequest(message=data)
            response = await assistant.process_message(request)
            await websocket.send_json(response.dict())
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/suggestions")
async def get_suggestions():
    """Get contextual suggestions"""
    return {
        "suggestions": [
            "Log today's trades",
            "Review morning session",
            "Analyze XAUUSD patterns",
            "Check strategy conflicts",
            "Generate performance report"
        ]
    }

@app.post("/clear-history")
async def clear_history():
    """Clear conversation history"""
    assistant.conversation_history.clear()
    return {"status": "history cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''

# 2. Create the system prompt
system_prompt = '''You are the ncOS Journal Assistant, an advanced AI system integrated with the ncOS v21.7 Phoenix Mesh Journal System. Your primary role is to help traders maintain comprehensive journals, analyze trading patterns, and improve their systematic approach to trading.

## Your Core Responsibilities:

### 1. Trade Logging Assistance
- Help users log trades with complete context (entry, exit, rationale)
- Prompt for important details they might forget (emotional state, market conditions)
- Suggest appropriate tags for easy filtering
- Format trade data for optimal journal storage

### 2. Pattern Analysis
- Identify ZBAR patterns (Wyckoff, SMC, liquidity zones, fractals)
- Analyze market structure and price action
- Detect potential setup opportunities
- Validate pattern confluences

### 3. Performance Insights
- Track win rates and risk/reward ratios
- Identify profitable and losing patterns
- Analyze emotional factors affecting performance
- Suggest improvements based on historical data

### 4. Risk Management
- Monitor position sizing consistency
- Alert on strategy conflicts
- Track risk per trade and daily limits
- Suggest adjustments based on market conditions

### 5. Cognitive Support
- Help identify emotional trading patterns
- Encourage disciplined journaling habits
- Provide objective analysis during high-stress periods
- Support continuous improvement mindset

## Interaction Guidelines:

- Always be specific and actionable in your responses
- Ask clarifying questions to ensure complete journal entries
- Reference historical data when providing insights
- Encourage systematic thinking and documentation
- Maintain a professional yet supportive tone

## Technical Integration:

You have access to:
- Journal API for reading/writing entries
- ZBAR pattern analysis engine
- Performance metrics calculator
- Conflict detection system
- Historical trade database

When users mention trades or analysis, offer to:
1. Create detailed journal entries
2. Run pattern analysis
3. Check for conflicts
4. Generate performance reports
5. Provide historical comparisons

Remember: Your goal is to make traders more systematic, self-aware, and profitable through comprehensive journaling and analysis.'''

# 3. Create the auto-start script
autostart_script = '''#!/bin/bash
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
'''

# 4. Create integration with main system
integration_code = '''# LLM Integration for ncOS Journal Dashboard
import streamlit as st
import requests
import asyncio
import websockets
import json
from datetime import datetime

class LLMIntegration:
    """Integration with ncOS LLM Assistant"""
    
    def __init__(self, llm_url="http://localhost:8002"):
        self.llm_url = llm_url
        self.ws_url = llm_url.replace("http", "ws") + "/ws"
        
    def chat(self, message: str, include_context: bool = True) -> dict:
        """Send message to LLM assistant"""
        try:
            response = requests.post(
                f"{self.llm_url}/chat",
                json={
                    "message": message,
                    "include_journal_data": include_context
                }
            )
            return response.json()
        except Exception as e:
            return {
                "response": f"LLM Assistant unavailable: {str(e)}",
                "suggestions": ["Check if LLM service is running"]
            }
    
    def get_suggestions(self) -> list:
        """Get contextual suggestions"""
        try:
            response = requests.get(f"{self.llm_url}/suggestions")
            return response.json().get("suggestions", [])
        except:
            return ["Start LLM Assistant for suggestions"]

def add_llm_chat_to_dashboard():
    """Add LLM chat interface to Streamlit dashboard"""
    st.sidebar.markdown("---")
    st.sidebar.header("🤖 AI Assistant")
    
    # Initialize LLM integration
    if 'llm' not in st.session_state:
        st.session_state.llm = LLMIntegration()
    
    # Chat interface
    with st.sidebar.expander("Chat with AI", expanded=True):
        # Message input
        user_message = st.text_input("Ask anything...", key="llm_input")
        
        # Send button
        if st.button("Send", key="llm_send") and user_message:
            with st.spinner("Thinking..."):
                response = st.session_state.llm.chat(user_message)
                
            # Display response
            st.markdown("**AI:** " + response.get("response", "No response"))
            
            # Show suggestions if available
            suggestions = response.get("suggestions", [])
            if suggestions:
                st.markdown("**Suggestions:**")
                for suggestion in suggestions:
                    if st.button(suggestion, key=f"sug_{suggestion[:10]}"):
                        st.session_state.llm_input = suggestion
                        st.experimental_rerun()
        
        # Quick actions
        st.markdown("**Quick Actions:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Log Trade"):
                st.session_state.llm_input = "Help me log a trade"
                st.experimental_rerun()
                
            if st.button("📊 Analysis"):
                st.session_state.llm_input = "Analyze my recent trades"
                st.experimental_rerun()
        
        with col2:
            if st.button("📈 Patterns"):
                st.session_state.llm_input = "What patterns do you see?"
                st.experimental_rerun()
                
            if st.button("💡 Tips"):
                st.session_state.llm_input = "Give me trading tips based on my journal"
                st.experimental_rerun()

# Add to your main dashboard app.py:
# add_llm_chat_to_dashboard()
'''

# 5. Create systemd service for auto-start
systemd_service = '''[Unit]
Description=ncOS Journal LLM Assistant
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/ncOS_journal
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="OPENAI_API_KEY=your-key-here"
ExecStart=/usr/bin/python3 /home/trader/ncOS_journal/llm_assistant.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''

# 6. Create Docker compose for complete system
docker_compose = '''version: '3.8'

services:
  journal-api:
    build: .
    container_name: ncos-journal-api
    ports:
      - "8000:8000"
    volumes:
      - ./journal_data:/app/journal_data
    environment:
      - JOURNAL_DATA_DIR=/app/journal_data
    restart: unless-stopped

  journal-dashboard:
    build: .
    container_name: ncos-journal-dashboard
    ports:
      - "8501:8501"
    volumes:
      - ./journal_data:/app/journal_data
    command: streamlit run app.py
    depends_on:
      - journal-api
    restart: unless-stopped

  llm-assistant:
    build: .
    container_name: ncos-llm-assistant
    ports:
      - "8002:8002"
    volumes:
      - ./journal_data:/app/journal_data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JOURNAL_API_URL=http://journal-api:8000
    command: python llm_assistant.py
    depends_on:
      - journal-api
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: ncos-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - journal-api
      - journal-dashboard
      - llm-assistant
    restart: unless-stopped
'''

# Save all files
with open('llm_assistant.py', 'w') as f:
    f.write(llm_assistant_code)

with open('llm_system_prompt.txt', 'w') as f:
    f.write(system_prompt)

with open('start_llm_assistant.sh', 'w') as f:
    f.write(autostart_script)

with open('llm_dashboard_integration.py', 'w') as f:
    f.write(integration_code)

with open('ncos-llm.service', 'w') as f:
    f.write(systemd_service)

with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose)

# Create setup instructions
setup_instructions = '''# ncOS LLM Assistant Setup Instructions

## Quick Start (Local)

1. **Set OpenAI API Key** (optional but recommended):
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   '''