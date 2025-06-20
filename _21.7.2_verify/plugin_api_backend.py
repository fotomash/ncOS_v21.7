
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime
import json

app = FastAPI(
    title="NCOS Live Market Data API",
    description="Provides live market data for stocks, crypto, and forex, powered by the NCOS system.",
    version="21.7.2"
)

# Allow CORS for development and for the LLM platform to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the LLM's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Agent Logic (Integrated directly for simplicity) ---
# In a full NCOS system, this would be a separate agent class.

def get_stock_data(ticker: str):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid ticker or no data available")
        return {
            "symbol": info.get("symbol", ticker.upper()),
            "price": info.get("regularMarketPrice"),
            "change_percent": info.get("regularMarketChangePercent", 0) * 100,
            "timestamp": datetime.fromtimestamp(info.get("regularMarketTime")).isoformat() if info.get("regularMarketTime") else datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch data for stock ticker {ticker}: {e}")

def get_crypto_data(symbol: str):
    try:
        data = yf.Ticker(symbol)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid symbol or no data available")
        return {
            "symbol": info.get("symbol", symbol.upper()),
            "price": info.get("regularMarketPrice"),
            "change_percent": info.get("regularMarketChangePercent", 0) * 100,
            "market_cap": info.get("marketCap")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch data for crypto symbol {symbol}: {e}")

def get_forex_data(pair: str):
    try:
        data = yf.Ticker(pair)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid pair or no data available")
        return {
            "pair": info.get("shortName", pair.upper()),
            "rate": info.get("regularMarketPrice"),
            "timestamp": datetime.fromtimestamp(info.get("regularMarketTime")).isoformat() if info.get("regularMarketTime") else datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch data for forex pair {pair}: {e}")

# --- API Endpoints ---

@app.get("/stock/quote", summary="Get a real-time stock quote")
def stock_quote_endpoint(ticker: str = Query(..., description="The stock ticker symbol (e.g., 'AAPL').")):
    return get_stock_data(ticker)

@app.get("/crypto/quote", summary="Get a real-time cryptocurrency price")
def crypto_quote_endpoint(symbol: str = Query(..., description="The crypto symbol (e.g., 'BTC-USD').")):
    return get_crypto_data(symbol)

@app.get("/forex/quote", summary="Get a real-time forex exchange rate")
def forex_quote_endpoint(pair: str = Query(..., description="The currency pair (e.g., 'EURUSD=X').")):
    return get_forex_data(pair)

# --- Plugin Configuration Endpoints ---

@app.get("/openapi.json", include_in_schema=False)
def get_openapi_spec():
    with open('ncos_openapi.json') as f:
        return JSONResponse(content=json.load(f))

@app.get("/ai-plugin.json", include_in_schema=False)
def get_ai_plugin_manifest():
    with open('ncos_ai_plugin.json') as f:
        return JSONResponse(content=json.load(f))

@app.get("/logo.png", include_in_schema=False)
def get_logo():
    # Return a placeholder logo
    return FileResponse('logo.png')

if __name__ == "__main__":
    import uvicorn
    print("NCOS Live Market Data API starting on http://localhost:8000")
    print("Access OpenAPI spec at http://localhost:8000/openapi.json")
    print("Access AI Plugin manifest at http://localhost:8000/ai-plugin.json")
    uvicorn.run(app, host="0.0.0.0", port=8000)
