#!/usr/bin/env python3
"""
ncOS Journal LLM Assistant
Auto-starting AI assistant for trade journaling and analysis
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel

from production.production_config import load_production_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
config = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))


@dataclass
class LLMConfig:
    """LLM Assistant Configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt_file: str = "llm_system_prompt.txt"
    journal_api_url: str = config.api.journal

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
