# NCOS Market Bias System Integration Guide

## Quick Start
1. Copy `ncos_market_bias_system_v21.7.1.yaml` to your NCOS config directory
2. Run `python market_bias_launcher.py` to initialize
3. Configure environment variables for alerts

## Environment Variables Required
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export WEBHOOK_URL="your-webhook-url"
export WEBHOOK_TOKEN="your-webhook-token"
```

## Integration Points
- **Enhanced Core Orchestrator**: Auto-registers all bias agents
- **SMC Analysis Engine**: Feeds pattern data to bias monitor
- **Liquidity Analysis Engine**: Provides flow data for bias calculation
- **Vector Engine**: Manages bias memory across sessions

## Usage Examples
```python
# Get current bias
bias = await bias_monitor.get_current_bias("XAUUSD")

# Render chart with bias overlay
chart = await chart_renderer.render_with_bias("XAUUSD", bias)

# Query historical bias
history = await vector_engine.query_bias_history("XAUUSD", days=7)
```

## Next Steps
1. Configure your data sources in the market data ingestor
2. Set up alert channels (Telegram/Webhook)
3. Customize bias calculation parameters
4. Enable session export for review
