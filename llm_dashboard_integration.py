# LLM Integration for ncOS Journal Dashboard
import streamlit as st
import requests
import asyncio
import websockets
import json
import os
from datetime import datetime
from production.production_config import load_production_config

config = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))

class LLMIntegration:
    """Integration with ncOS LLM Assistant"""

    def __init__(self, llm_url: str | None = None):
        self.llm_url = llm_url or config.api.llm
        self.ws_url = self.llm_url.replace("http", "ws") + "/ws"
        
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
