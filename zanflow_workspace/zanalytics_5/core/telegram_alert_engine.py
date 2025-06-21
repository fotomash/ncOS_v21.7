# telegram_alert_engine.py

import requests
import json

def send_telegram_alert(entry_data, config_path="config/webhook_settings.json"):
    """
    Sends a formatted message to a Telegram bot based on entry confirmation.
    Expects a config file with token and chat_id.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        if not config.get("webhook_enabled", False):
            print("[TELEGRAM] Webhook disabled in config.")
            return

        token = config["bot_token"]
        chat_id = config["chat_id"]
        endpoint = f"https://api.telegram.org/bot{token}/sendMessage"

        message = format_trade_message(entry_data)
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

        response = requests.post(endpoint, data=payload)
        if response.status_code != 200:
            print(f"[TELEGRAM ERROR] {response.status_code}: {response.text}")
        else:
            print("[TELEGRAM] Alert sent.")
    except Exception as e:
        print(f"[TELEGRAM EXCEPTION] {e}")


def send_simple_summary_alert(summary_text, config_path="config/webhook_settings.json"):
    """
    Send a plain summary line to Telegram — e.g., from AI agents or journaling.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        if not config.get("webhook_enabled", False):
            print("[TELEGRAM] Webhook disabled in config.")
            return

        token = config["bot_token"]
        chat_id = config["chat_id"]
        endpoint = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {"chat_id": chat_id, "text": summary_text, "parse_mode": "HTML"}

        response = requests.post(endpoint, data=payload)
        if response.status_code != 200:
            print(f"[TELEGRAM ERROR] {response.status_code}: {response.text}")
        else:
            print("[TELEGRAM] Summary alert sent.")
    except Exception as e:
        print(f"[TELEGRAM EXCEPTION] {e}")


def format_trade_message(entry_data):
    """
    Format a detailed message for any trade entry (scalp or macro).
    """
    trade_type = entry_data.get("entry_type", "TRADE")
    trade_label = "SCALP" if "scalp" in trade_type.lower() else "MACRO"
    return f"""
📡 <b>ZANALYTICS {trade_label} ENTRY</b>

🟢 <b>Symbol:</b> {entry_data.get('symbol')}
🕒 <b>Time:</b> {entry_data.get('timestamp')}
⚙️ <b>Type:</b> {trade_type}
🎯 <b>Entry:</b> {entry_data.get('entry_price')} | <b>SL:</b> {entry_data.get('sl')} | <b>TP:</b> {entry_data.get('tp')}
📊 <b>R:R:</b> {entry_data.get('r_multiple')} | <b>Risk:</b> {entry_data.get('risk_percent')}%
📎 <b>Comment:</b> {entry_data.get('comment', 'zan_entry')}
""".strip()
