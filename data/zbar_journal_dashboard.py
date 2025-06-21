
import requests
import streamlit as st

st.set_page_config(page_title="ZBAR Voice Command Dashboard", layout="wide")

# API configuration
API_BASE = "http://localhost:8001"

st.title("🎤 ZBAR Voice Command Interface")

# Voice input section
col1, col2 = st.columns([3, 1])

with col1:
    voice_input = st.text_input(
        "Voice Command:", 
        placeholder="e.g., 'Mark gold bullish on H4 with high maturity'"
    )

with col2:
    if st.button("🎙️ Record Audio"):
        st.info("Audio recording not implemented in demo")

# Process command
if voice_input and st.button("Execute Command"):
    with st.spinner("Processing voice command..."):
        response = requests.post(
            f"{API_BASE}/voice/command",
            json={"text": voice_input}
        )

        if response.status_code == 200:
            result = response.json()

            # Display parsed information
            st.subheader("📊 Parsed Information")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Symbol", result["parsed_tag"].get("symbol", "N/A"))
                st.metric("Timeframe", result["parsed_tag"].get("timeframe", "N/A"))

            with col2:
                st.metric("Bias", result["parsed_tag"].get("bias", "N/A"))
                st.metric("Session", result["parsed_tag"].get("session", "N/A"))

            with col3:
                confidence = result["parsed_tag"].get("confidence", 0)
                st.metric("Confidence", f"{confidence:.0%}")
                if result["parsed_tag"].get("maturity_score"):
                    st.metric("Maturity", f"{result['parsed_tag']['maturity_score']:.2f}")

            # Display action result
            if result["status"] == "executed":
                st.success(f"✅ Command executed: {result['action']['action']}")
                if result.get("result"):
                    st.json(result["result"])

            elif result["status"] == "confirm_needed":
                st.warning(result["message"])
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirm"):
                        st.info("Confirmation action would execute here")
                with col2:
                    if st.button("❌ Cancel"):
                        st.info("Cancelled")

            elif result["status"] == "clarification_needed":
                st.error(result["message"])
                st.subheader("Did you mean:")
                for suggestion in result.get("suggestions", []):
                    if st.button(suggestion["command"]):
                        st.info(f"Would execute: {suggestion['action']}")

# Voice command history
st.divider()
st.subheader("📜 Recent Voice Commands")

history_response = requests.get(f"{API_BASE}/voice/history")
if history_response.status_code == 200:
    history = history_response.json()

    for cmd in history["commands"]:
        with st.expander(f"{cmd['raw_text']} - {cmd['timestamp'][:19]}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Symbol:** {cmd.get('symbol', 'N/A')}")
                st.write(f"**Timeframe:** {cmd.get('timeframe', 'N/A')}")
                st.write(f"**Bias:** {cmd.get('bias', 'N/A')}")
            with col2:
                st.write(f"**Action:** {cmd.get('action', 'N/A')}")
                st.write(f"**Session:** {cmd.get('session', 'N/A')}")
                st.write(f"**Confidence:** {cmd.get('confidence', 0):.0%}")

# Examples section
with st.sidebar:
    st.header("📚 Voice Command Examples")

    examples_response = requests.get(f"{API_BASE}/voice/examples")
    if examples_response.status_code == 200:
        examples = examples_response.json()

        st.subheader("Try these commands:")
        for example in examples["examples"]:
            st.code(example)

        st.subheader("Command Patterns:")
        for pattern_type, pattern in examples["patterns"].items():
            st.write(f"**{pattern_type.title()}:** `{pattern}`")
