"""
ncOS Journal Dashboard - Phoenix Edition
"""

import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

# Configuration
API_URL = "http://localhost:8001"

# Page config
st.set_page_config(
    page_title="ncOS Journal - Phoenix Edition",
    page_icon="📊",
    layout="wide"
)

# Helper functions
def fetch_data(endpoint: str, params: dict = None) -> dict:
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params)
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return {}

def post_data(endpoint: str, data: dict) -> dict:
    """Post data to API"""
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data)
        return response.json()
    except Exception as e:
        st.error(f"Failed to post data: {e}")
        return {}

# Sidebar
with st.sidebar:
    st.title("🔥 ncOS Journal")
    st.markdown("### Phoenix Edition v21.7")
    
    page = st.selectbox(
        "Navigation",
        ["Dashboard", "Trade Entry", "Journal", "Analysis", "Statistics"]
    )
    
    st.markdown("---")
    
    # Quick stats
    stats = fetch_data("stats")
    if stats:
        st.metric("Total Trades", stats.get("trades", {}).get("total", 0))
        st.metric("Win Rate", f"{stats.get('trades', {}).get('win_rate', 0):.1f}%")
        st.metric("Journal Entries", stats.get("journal_entries", 0))

# Main content
if page == "Dashboard":
    st.title("📊 Trading Dashboard")
    
    # Fetch recent data
    trades_data = fetch_data("trades")
    trades = trades_data.get("trades", [])
    
    if trades:
        # Convert to DataFrame
        df = pd.DataFrame(trades)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(trades))
        
        with col2:
            winning_trades = sum(1 for t in trades if t.get("exit_price", 0) > t.get("entry_price", 0))
            st.metric("Winning Trades", winning_trades)
        
        with col3:
            symbols = list(set(t.get("symbol", "") for t in trades))
            st.metric("Symbols Traded", len(symbols))
        
        with col4:
            today_trades = sum(1 for t in trades if t.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d")))
            st.metric("Today's Trades", today_trades)
        
        # Recent trades table
        st.subheader("Recent Trades")
        recent_trades = df.tail(10)[["timestamp", "symbol", "side", "entry_price", "exit_price", "notes"]]
        st.dataframe(recent_trades)
        
        # Pattern analysis
        if any(t.get("patterns") for t in trades):
            st.subheader("Pattern Performance")
            pattern_data = {}
            for trade in trades:
                for pattern in trade.get("patterns", []):
                    if pattern not in pattern_data:
                        pattern_data[pattern] = {"total": 0, "wins": 0}
                    pattern_data[pattern]["total"] += 1
                    if trade.get("exit_price", 0) > trade.get("entry_price", 0):
                        pattern_data[pattern]["wins"] += 1
            
            pattern_df = pd.DataFrame([
                {
                    "Pattern": p,
                    "Total": d["total"],
                    "Wins": d["wins"],
                    "Win Rate": (d["wins"] / d["total"] * 100) if d["total"] > 0 else 0
                }
                for p, d in pattern_data.items()
            ])
            
            fig = px.bar(pattern_df, x="Pattern", y="Win Rate", title="Pattern Win Rates")
            st.plotly_chart(fig)
    else:
        st.info("No trades recorded yet. Start by entering a trade!")

elif page == "Trade Entry":
    st.title("📝 Trade Entry")
    
    with st.form("trade_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", value="XAUUSD")
            side = st.selectbox("Side", ["long", "short"])
            entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
            exit_price = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)
        
        with col2:
            quantity = st.number_input("Quantity", min_value=0.01, step=0.01, value=0.01)
            stop_loss = st.number_input("Stop Loss", min_value=0.0, step=0.01)
            take_profit = st.number_input("Take Profit", min_value=0.0, step=0.01)
            session_id = st.text_input("Session ID", value=f"session_{datetime.now().strftime('%Y%m%d')}")
        
        patterns = st.multiselect(
            "Patterns",
            ["Wyckoff Spring", "Order Block", "FVG", "Liquidity Sweep", "Break of Structure"]
        )
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Submit Trade")
        
        if submitted:
            trade_data = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "exit_price": exit_price if exit_price > 0 else None,
                "quantity": quantity,
                "stop_loss": stop_loss if stop_loss > 0 else None,
                "take_profit": take_profit if take_profit > 0 else None,
                "patterns": patterns,
                "notes": notes,
                "session_id": session_id
            }
            
            result = post_data("trades", trade_data)
            if result.get("id"):
                st.success(f"Trade recorded! ID: {result['id']}")
            else:
                st.error("Failed to record trade")

elif page == "Journal":
    st.title("📔 Trading Journal")
    
    tab1, tab2 = st.tabs(["View Entries", "New Entry"])
    
    with tab1:
        entries_data = fetch_data("journal")
        entries = entries_data.get("entries", [])
        
        if entries:
            for entry in entries:
                with st.expander(f"{entry.get('title')} - {entry.get('timestamp', '')[:10]}"):
                    st.markdown(entry.get("content", ""))
                    if entry.get("tags"):
                        st.write("Tags:", ", ".join(entry["tags"]))
        else:
            st.info("No journal entries yet.")
    
    with tab2:
        with st.form("journal_form"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=300)
            category = st.selectbox(
                "Category",
                ["general", "trade_review", "market_analysis", "psychology", "strategy"]
            )
            tags = st.text_input("Tags (comma-separated)")
            
            submitted = st.form_submit_button("Save Entry")
            
            if submitted and title and content:
                journal_data = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()]
                }
                
                result = post_data("journal", journal_data)
                if result.get("id"):
                    st.success("Journal entry saved!")
                    st.experimental_rerun()

elif page == "Analysis":
    st.title("🔍 Market Analysis")
    
    analyses_data = fetch_data("analysis")
    analyses = analyses_data.get("analyses", [])
    
    if analyses:
        # Group by symbol
        symbols = list(set(a.get("symbol", "") for a in analyses))
        selected_symbol = st.selectbox("Select Symbol", symbols)
        
        symbol_analyses = [a for a in analyses if a.get("symbol") == selected_symbol]
        
        for analysis in symbol_analyses:
            with st.expander(f"{analysis.get('analysis_type')} - {analysis.get('timestamp', '')[:16]}"):
                st.json(analysis.get("content", {}))
    else:
        st.info("No analyses recorded yet.")

elif page == "Statistics":
    st.title("📈 Trading Statistics")
    
    stats = fetch_data("stats")
    
    if stats:
        # Overall metrics
        st.subheader("Overall Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Trades", stats.get("trades", {}).get("total", 0))
        with col2:
            st.metric("Win Rate", f"{stats.get('trades', {}).get('win_rate', 0):.1f}%")
        with col3:
            st.metric("Total Analyses", stats.get("analyses", 0))
        
        # Pattern statistics
        if stats.get("patterns"):
            st.subheader("Pattern Usage")
            pattern_df = pd.DataFrame([
                {"Pattern": p, "Count": c}
                for p, c in stats["patterns"].items()
            ])
            
            fig = px.pie(pattern_df, values="Count", names="Pattern", title="Pattern Distribution")
            st.plotly_chart(fig)
        
        # Symbol distribution
        if stats.get("symbols"):
            st.subheader("Symbols Traded")
            st.write(", ".join(stats["symbols"]))

# Footer
st.markdown("---")
st.markdown("🔥 ncOS Journal - Phoenix Edition v21.7")
