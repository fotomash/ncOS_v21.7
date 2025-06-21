import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from production.production_config import load_production_config

# Page config
st.set_page_config(
    page_title="ncOS Journal Dashboard - Phoenix Edition",
    page_icon="🔥",
    layout="wide"
)

# API endpoints
CONFIG = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))
API_URL = CONFIG.api.journal
ZBAR_LOG_FILE = "/mnt/data/logs/trade_journal.jsonl"
LOCAL_LOG_FILE = "data/journals/trade_journal.jsonl"


# Helper functions
def load_zbar_entries():
    """Load ZBAR journal entries"""
    log_files = [ZBAR_LOG_FILE, LOCAL_LOG_FILE]
    records = []

    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except:
                            pass

    return pd.DataFrame(records) if records else pd.DataFrame()


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


# Title with Phoenix branding
st.title("🔥 ncOS Journal Dashboard - Phoenix Edition")
st.markdown("*Unified Trade Intelligence & ZBAR Pattern Analysis*")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Module",
    ["Overview", "Trades", "Journal", "ZBAR Analysis", "Session Replay", "New Entry", "Settings"]
)

# Main content routing
if page == "Overview":
    st.header("Trading Overview")

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Statistics", "Performance", "ZBAR Patterns"])

    with tab1:
        # Stats
        stats = fetch_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Trades", stats.get("total_trades", 0))

        with col2:
            st.metric("Win Rate", f"{stats.get('win_rate', 0) * 100:.1f}%")

        with col3:
            st.metric("Total P&L", f"${stats.get('total_pnl', 0):,.2f}")

        with col4:
            st.metric("Avg P&L", f"${stats.get('average_pnl', 0):,.2f}")

    with tab2:
        # P&L over time
        trades = fetch_trades()
        if trades:
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            st.subheader("P&L Over Time")
            if 'pnl' in df.columns:
                df_sorted = df.sort_values('timestamp')
                df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sorted['timestamp'],
                    y=df_sorted['cumulative_pnl'],
                    mode='lines+markers',
                    name='Cumulative P&L',
                    line=dict(color='#00ff00', width=2)
                ))
                fig.update_layout(
                    height=400,
                    template="plotly_dark",
                    title="Cumulative P&L Performance"
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # ZBAR pattern distribution
        zbar_df = load_zbar_entries()
        if not zbar_df.empty and 'patterns' in zbar_df.columns:
            st.subheader("ZBAR Pattern Distribution")
            pattern_counts = {}
            for patterns in zbar_df['patterns'].dropna():
                if isinstance(patterns, list):
                    for p in patterns:
                        pattern_counts[p] = pattern_counts.get(p, 0) + 1

            if pattern_counts:
                fig = px.bar(
                    x=list(pattern_counts.keys()),
                    y=list(pattern_counts.values()),
                    labels={'x': 'Pattern', 'y': 'Count'},
                    title="Most Common ZBAR Patterns"
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

elif page == "ZBAR Analysis":
    st.header("📊 ZBAR Trade Journal")

    # Load ZBAR entries
    df = load_zbar_entries()

    if df.empty:
        st.warning("No ZBAR journal entries found yet.")
        st.info("ZBAR entries will appear here once you start logging trades with pattern analysis.")
    else:
        # Process dataframe
        if "logged_at" in df.columns:
            df["logged_at"] = pd.to_datetime(df["logged_at"])
            df = df.sort_values("logged_at", ascending=False)

        # Sidebar filters
        st.sidebar.header("ZBAR Filters")

        # Session filter
        session_ids = []
        if "session_id" in df.columns:
            session_ids = sorted(df["session_id"].dropna().unique().tolist())
        session = st.sidebar.selectbox("Session ID", options=["All"] + session_ids)

        # Symbol filter
        symbols = []
        if "symbol" in df.columns:
            symbols = sorted(df["symbol"].dropna().unique().tolist())
        symbol = st.sidebar.selectbox("Symbol", options=["All"] + symbols)

        # Trace ID filter
        trace_id = st.sidebar.text_input("Trace ID contains")

        # Pattern filter
        pattern_filter = st.sidebar.multiselect(
            "Patterns",
            options=["Wyckoff", "SMC", "Order Block", "FVG", "Liquidity Sweep", "Break of Structure"]
        )

        # Apply filters
        filtered_df = df.copy()
        if session != "All":
            filtered_df = filtered_df[filtered_df["session_id"] == session]
        if symbol != "All":
            filtered_df = filtered_df[filtered_df["symbol"] == symbol]
        if trace_id:
            filtered_df = filtered_df[filtered_df["trace_id"].str.contains(trace_id, na=False)]

        # Session recap
        if session != "All":
            st.markdown(f"### 🧠 Session Recap: {session}")
            trades = filtered_df.shape[0]
            pairs = sorted(filtered_df['symbol'].dropna().unique()) if 'symbol' in filtered_df else []
            avg_maturity = filtered_df["maturity_score"].mean() if "maturity_score" in filtered_df else None

            recap_text = f"**{trades}** trades logged for this session\n\n"
            if pairs:
                recap_text += f"Pairs: {', '.join(pairs)}\n\n"
            if avg_maturity:
                recap_text += f"Average maturity score: {avg_maturity:.2f}"

            st.info(recap_text)

        st.markdown(f"### Showing {len(filtered_df)} filtered entries")

        # Display entries
        for i, row in filtered_df.iterrows():
            timestamp = row.get('logged_at', 'Unknown time')
            symbol = row.get('symbol', 'Unknown')
            trace = row.get('trace_id', 'No trace')

            with st.expander(f"{timestamp} | {symbol} | {trace}"):
                # Display entry details
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.json(row.to_dict())

                with col2:
                    st.markdown("**Actions**")

                    # Re-run strategy button
                    if st.button(f"🔁 Re-run", key=f"rerun_{i}"):
                        context = {
                            "trace_id": row.get("trace_id"),
                            "initial_htf_bias": row.get("bias"),
                            "session_id": row.get("session_id")
                        }
                        try:
                            res = requests.post(
                                "http://localhost:8000/strategy/zbar/execute_multi",
                                json={
                                    "strategy": "ISPTS_v14",
                                    "asset": row.get("symbol"),
                                    "blocks": [],
                                    "context": context
                                }
                            )
                            st.success("Strategy Re-run Completed")
                            st.json(res.json())
                        except Exception as e:
                            st.error(f"Error: {e}")

                    # Analyze button
                    if st.button(f"📈 Analyze", key=f"analyze_{i}"):
                        st.info("Deep analysis coming soon...")

elif page == "Session Replay":
    st.header("🎬 Session Replay & Analysis")

    # Session selection
    zbar_df = load_zbar_entries()
    if not zbar_df.empty and "session_id" in zbar_df.columns:
        sessions = sorted(zbar_df["session_id"].dropna().unique().tolist())

        selected_session = st.selectbox("Select Session to Replay", sessions)

        if selected_session:
            session_data = zbar_df[zbar_df["session_id"] == selected_session]

            # Session metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Trades", len(session_data))
            with col2:
                if "pnl" in session_data.columns:
                    total_pnl = session_data["pnl"].sum()
                    st.metric("Session P&L", f"${total_pnl:,.2f}")
            with col3:
                if "maturity_score" in session_data.columns:
                    avg_maturity = session_data["maturity_score"].mean()
                    st.metric("Avg Maturity", f"{avg_maturity:.2f}")

            # Timeline view
            st.subheader("Session Timeline")
            if "logged_at" in session_data.columns:
                timeline_data = session_data.sort_values("logged_at")

                # Create timeline chart
                fig = go.Figure()

                for idx, row in timeline_data.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row["logged_at"]],
                        y=[row.get("symbol", "Unknown")],
                        mode='markers+text',
                        marker=dict(
                            size=15,
                            color='green' if row.get("pnl", 0) > 0 else 'red'
                        ),
                        text=f"{row.get('trace_id', '')}",
                        textposition="top center",
                        name=row.get("trace_id", "Trade")
                    ))

                fig.update_layout(
                    height=400,
                    showlegend=False,
                    template="plotly_dark",
                    title="Trade Execution Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Detailed replay
            if st.button("🎯 Start Detailed Replay"):
                st.info("Replaying session trades...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, (i, row) in enumerate(timeline_data.iterrows()):
                    progress = (idx + 1) / len(timeline_data)
                    progress_bar.progress(progress)

                    status_text.text(
                        f"Replaying trade {idx + 1}/{len(timeline_data)}: {row.get('symbol')} at {row.get('logged_at')}")

                    # Display trade details
                    with st.container():
                        st.write(f"**Trade {idx + 1}**")
                        st.json({
                            "symbol": row.get("symbol"),
                            "bias": row.get("bias"),
                            "patterns": row.get("patterns"),
                            "entry": row.get("entry_price"),
                            "exit": row.get("exit_price"),
                            "pnl": row.get("pnl")
                        })

                    # Simulate processing time
                    import time

                    time.sleep(0.5)

                status_text.text("Replay complete!")
    else:
        st.info("No sessions found for replay")

elif page == "New Entry":
    st.header("Create New Entry")

    entry_type = st.radio("Entry Type", ["Trade", "Journal", "ZBAR Analysis"])

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
                patterns = st.multiselect(
                    "Patterns Detected",
                    ["Wyckoff Spring", "SMC MSS", "Order Block", "FVG", "Liquidity Sweep", "BOS", "CHoCH"]
                )

            # ZBAR specific fields
            st.subheader("ZBAR Context")
            col3, col4 = st.columns(2)

            with col3:
                session_id = st.text_input("Session ID", value=f"session_{datetime.now().strftime('%Y%m%d_%H%M')}")
                trace_id = st.text_input("Trace ID", value=f"trace_{datetime.now().strftime('%H%M%S')}")
                bias = st.selectbox("HTF Bias", ["bullish", "bearish", "neutral"])

            with col4:
                maturity_score = st.slider("Maturity Score", 0.0, 10.0, 5.0, 0.1)
                confluence_score = st.slider("Confluence Score", 0.0, 10.0, 5.0, 0.1)

            notes = st.text_area("Trade Notes & Rationale")

            if st.form_submit_button("Log Trade"):
                trade_data = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat(),
                    "notes": notes,
                    "patterns": patterns,
                    # ZBAR fields
                    "session_id": session_id,
                    "trace_id": trace_id,
                    "bias": bias,
                    "maturity_score": maturity_score,
                    "confluence_score": confluence_score,
                    "logged_at": datetime.now().isoformat()
                }

                if exit_price > 0:
                    trade_data["exit_price"] = exit_price
                if pnl != 0:
                    trade_data["pnl"] = pnl

                try:
                    # Log to API
                    response = requests.post(f"{API_URL}/trades", json=trade_data)

                    # Also log to ZBAR journal
                    os.makedirs("data/journals", exist_ok=True)
                    with open(LOCAL_LOG_FILE, "a") as f:
                        f.write(json.dumps(trade_data) + "\n")

                    if response.status_code == 200:
                        st.success("Trade logged successfully!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    elif entry_type == "ZBAR Analysis":
        st.subheader("Log ZBAR Pattern Analysis")

        with st.form("zbar_form"):
            symbol = st.text_input("Symbol", "XAUUSD")
            timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"])

            st.subheader("Wyckoff Analysis")
            wyckoff_phase = st.selectbox(
                "Current Phase",
                ["Accumulation A", "Accumulation B", "Accumulation C", "Accumulation D", "Accumulation E",
                 "Distribution A", "Distribution B", "Distribution C", "Distribution D", "Distribution E"]
            )

            st.subheader("Smart Money Concepts")
            smc_patterns = st.multiselect(
                "SMC Patterns Identified",
                ["Market Structure Shift", "Break of Structure", "Change of Character",
                 "Order Block", "Breaker Block", "Mitigation Block", "Fair Value Gap",
                 "Liquidity Sweep", "Inducement", "Premium/Discount"]
            )

            st.subheader("Technical Context")
            col1, col2 = st.columns(2)

            with col1:
                rsi = st.number_input("RSI", 0.0, 100.0, 50.0)
                volume_profile = st.selectbox("Volume Profile", ["Low", "Average", "High", "Climactic"])

            with col2:
                delta = st.number_input("Delta", step=0.01)
                cvd = st.number_input("CVD", step=0.01)

            analysis_notes = st.text_area("Detailed Analysis", height=200)

            if st.form_submit_button("Log Analysis"):
                analysis_data = {
                    "symbol": symbol,
                    "analysis_type": "ZBAR",
                    "content": {
                        "timeframe": timeframe,
                        "wyckoff_phase": wyckoff_phase,
                        "smc_patterns": smc_patterns,
                        "rsi": rsi,
                        "volume_profile": volume_profile,
                        "delta": delta,
                        "cvd": cvd,
                        "notes": analysis_notes
                    },
                    "timestamp": datetime.now().isoformat()
                }

                try:
                    response = requests.post(f"{API_URL}/analysis", json=analysis_data)
                    if response.status_code == 200:
                        st.success("ZBAR analysis logged!")
                except Exception as e:
                    st.error(f"Error: {e}")

elif page == "Settings":
    st.header("⚙️ Settings & Configuration")

    tab1, tab2, tab3 = st.tabs(["Data Management", "API Configuration", "Export/Import"])

    with tab1:
        st.subheader("Data Management")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear All Trades"):
                if st.checkbox("I understand this will delete all trade data"):
                    # Clear logic here
                    st.warning("Feature coming soon")

        with col2:
            if st.button("📊 Generate Report"):
                st.info("Report generation coming soon")

    with tab2:
        st.subheader("API Configuration")

        api_host = st.text_input("API Host", value="localhost")
        api_port = st.number_input("API Port", value=8000, min_value=1, max_value=65535)

        if st.button("Test Connection"):
            try:
                response = requests.get(f"http://{api_host}:{api_port}/health")
                if response.status_code == 200:
                    st.success("API connection successful!")
                    st.json(response.json())
            except:
                st.error("Failed to connect to API")

    with tab3:
        st.subheader("Export/Import Data")

        export_format = st.selectbox("Export Format", ["JSON", "CSV", "Parquet"])

        if st.button("Export All Data"):
            st.info(f"Exporting data as {export_format}...")
            # Export logic here

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔥 Phoenix Edition Features")
st.sidebar.markdown("""
- Unified trade journaling
- ZBAR pattern analysis
- Session replay capability
- Wyckoff phase tracking
- Smart Money Concepts
- Real-time performance metrics
""")
st.sidebar.markdown("---")
st.sidebar.markdown("ncOS Journal v2.0 - Phoenix")
