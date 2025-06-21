import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ncOS Journal Dashboard",
    page_icon="📊",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Title
st.title("📊 ncOS Journal Dashboard v2.0")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Overview", "Trades", "Journal", "Analysis", "New Entry"])

# Helper functions
def fetch_trades():
    try:
        response = requests.get(f"{API_URL}/trades")
        return response.json()
    except:
        return []

def fetch_journal():
    try:
        response = requests.get(f"{API_URL}/journal")
        return response.json()
    except:
        return []

def fetch_stats():
    try:
        response = requests.get(f"{API_URL}/stats")
        return response.json()
    except:
        return {}

# Main content
if page == "Overview":
    st.header("Trading Overview")
    
    # Stats
    stats = fetch_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", stats.get("total_trades", 0))
    
    with col2:
        st.metric("Win Rate", f"{stats.get('win_rate', 0)*100:.1f}%")
    
    with col3:
        st.metric("Total P&L", f"${stats.get('total_pnl', 0):,.2f}")
    
    with col4:
        st.metric("Avg P&L", f"${stats.get('average_pnl', 0):,.2f}")
    
    # Recent trades chart
    trades = fetch_trades()
    if trades:
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # P&L over time
        st.subheader("P&L Over Time")
        if 'pnl' in df.columns:
            df_sorted = df.sort_values('timestamp')
            df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_sorted['timestamp'],
                y=df_sorted['cumulative_pnl'],
                mode='lines+markers',
                name='Cumulative P&L'
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Trades":
    st.header("Trade History")
    
    trades = fetch_trades()
    if trades:
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            symbol_filter = st.selectbox(
                "Filter by Symbol",
                ["All"] + list(df['symbol'].unique())
            )
        
        with col2:
            side_filter = st.selectbox(
                "Filter by Side",
                ["All", "buy", "sell"]
            )
        
        # Apply filters
        if symbol_filter != "All":
            df = df[df['symbol'] == symbol_filter]
        if side_filter != "All":
            df = df[df['side'] == side_filter]
        
        # Display table
        st.dataframe(
            df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No trades found")

elif page == "Journal":
    st.header("Journal Entries")
    
    entries = fetch_journal()
    if entries:
        for entry in entries[:20]:  # Show last 20 entries
            with st.expander(f"{entry['title']} - {entry['timestamp']}"):
                st.write(entry['content'])
                if entry.get('tags'):
                    st.write(f"Tags: {', '.join(entry['tags'])}")
    else:
        st.info("No journal entries found")

elif page == "Analysis":
    st.header("Market Analysis")
    
    # Placeholder for analysis display
    st.info("Analysis visualization coming soon...")

elif page == "New Entry":
    st.header("Create New Entry")
    
    entry_type = st.radio("Entry Type", ["Trade", "Journal", "Analysis"])
    
    if entry_type == "Trade":
        with st.form("trade_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Symbol", "XAUUSD")
                side = st.selectbox("Side", ["buy", "sell"])
                entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
                quantity = st.number_input("Quantity", min_value=0.01, step=0.01)
            
            with col2:
                exit_price = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)
                pnl = st.number_input("P&L (optional)", step=0.01)
                patterns = st.text_input("Patterns (comma-separated)")
            
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Log Trade"):
                trade_data = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat(),
                    "notes": notes
                }
                
                if exit_price > 0:
                    trade_data["exit_price"] = exit_price
                if pnl != 0:
                    trade_data["pnl"] = pnl
                if patterns:
                    trade_data["patterns"] = [p.strip() for p in patterns.split(",")]
                
                try:
                    response = requests.post(f"{API_URL}/trades", json=trade_data)
                    if response.status_code == 200:
                        st.success("Trade logged successfully!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif entry_type == "Journal":
        with st.form("journal_form"):
            title = st.text_input("Title")
            category = st.selectbox("Category", ["general", "strategy", "psychology", "review"])
            content = st.text_area("Content", height=200)
            tags = st.text_input("Tags (comma-separated)")
            
            if st.form_submit_button("Create Entry"):
                entry_data = {
                    "title": title,
                    "content": content,
                    "category": category
                }
                
                if tags:
                    entry_data["tags"] = [t.strip() for t in tags.split(",")]
                
                try:
                    response = requests.post(f"{API_URL}/journal", json=entry_data)
                    if response.status_code == 200:
                        st.success("Journal entry created!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("ncOS Journal v2.0")
st.sidebar.markdown("Focus on journaling, not voice")
