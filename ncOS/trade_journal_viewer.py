import streamlit as st
import pandas as pd
import json
import os
import requests

st.set_page_config(layout="wide", page_title="ZBAR Trade Journal")

LOG_FILE = "/mnt/data/logs/trade_journal.jsonl"


def load_entries():
    """Load journal entries from the JSONL log file."""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()
    with open(LOG_FILE, "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    return pd.DataFrame(records)


st.title("\ud83d\udcda ZBAR Trade Journal Viewer")

df = load_entries()
if df.empty:
    st.warning("No journal entries found yet.")
    st.stop()

# Parse timestamp and sort
if "logged_at" in df:
    df["logged_at"] = pd.to_datetime(df["logged_at"])
    df = df.sort_values("logged_at", ascending=False)

# Sidebar filters
st.sidebar.header("Filters")
session_ids = sorted(df["session_id"].dropna().unique().tolist()) if "session_id" in df else []
session = st.sidebar.selectbox("Session ID", options=["All"] + session_ids)
symbol = st.sidebar.selectbox("Symbol", options=["All"] + sorted(df["symbol"].dropna().unique().tolist()))
trace_id = st.sidebar.text_input("Trace ID contains")

# Apply filters
filtered_df = df.copy()
if session != "All":
    filtered_df = filtered_df[filtered_df["session_id"] == session]
if symbol != "All":
    filtered_df = filtered_df[filtered_df["symbol"] == symbol]
if trace_id:
    filtered_df = filtered_df[filtered_df["trace_id"].str.contains(trace_id, na=False)]

# Session recap information
if session != "All":
    st.markdown(f"### \ud83e\udd14 Session Recap: {session}")
    trades = filtered_df.shape[0]
    pairs = sorted(filtered_df["symbol"].dropna().unique())
    avg_maturity = filtered_df["maturity_score"].mean() if "maturity_score" in filtered_df else None
    recap_text = f"**{trades}** trades logged for this session\n\nPairs: {', '.join(pairs)}"
    recap_text += "\n\n" + (
        f"Average maturity score: {avg_maturity:.2f}" if avg_maturity else "No maturity scores recorded"
    )
    st.info(recap_text)

st.markdown(f"### Showing {len(filtered_df)} filtered entries")

# Display each entry with option to re-run strategy
for i, row in filtered_df.iterrows():
    with st.expander(f"{row['logged_at']} | {row.get('symbol')} | {row.get('trace_id')}"):
        st.json(row.to_dict())
        if st.button(f"\ud83d\udd01 Re-run Strategy [{row.get('trace_id')}]", key=f"rerun_{i}"):
            context = {
                "trace_id": row.get("trace_id"),
                "initial_htf_bias": row.get("bias"),
                "session_id": row.get("session_id"),
            }
            try:
                res = requests.post(
                    "http://localhost:8000/strategy/zbar/execute_multi",
                    json={
                        "strategy": "ISPTS_v14",
                        "asset": row.get("symbol"),
                        "blocks": [],
                        "context": context,
                    },
                )
                st.success("Strategy Re-run Completed")
                st.json(res.json())
            except Exception as e:
                st.error(f"Error running strategy: {e}")
