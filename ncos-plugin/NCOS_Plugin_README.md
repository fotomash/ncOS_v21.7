
# NCOS Plugin Setup

To run the plugin server:
1. Install dependencies:
   pip install fastapi uvicorn yfinance

2. Start the server:
   python plugin_api_backend.py

3. Access:
   - http://localhost:8000/stock/quote?ticker=AAPL
   - http://localhost:8000/crypto/quote?symbol=BTC-USD
   - http://localhost:8000/forex/quote?pair=EURUSD=X
