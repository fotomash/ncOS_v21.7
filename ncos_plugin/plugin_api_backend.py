from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ncOS.voice_api_routes import router as voice_router
import yfinance as yf
from datetime import datetime
from pathlib import Path
import json
import os
import requests
from fastapi import Query

# Import your custom Finnhub client
from ncos_plugin.finnhub_data_fetcher import finnhub_client

app = FastAPI(title="NCOS Live Market Data API", version="21.7.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount voice command API routes
app.include_router(voice_router)

BASE_DIR = Path(__file__).parent

# Twelve Data API key should be provided via environment variable
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

def get_twelvedata_price(symbol: str):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "price" in data:
        return {
            "symbol": symbol,
            "price": float(data["price"])
        }
    else:
        raise HTTPException(status_code=500, detail=f"Twelve Data error: {data.get('message', 'Unknown error')}")
# ---- YFinance Endpoints ----
def get_stock_data(ticker: str):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid ticker or no data")
        return {
            "symbol": info.get("symbol", ticker.upper()),
            "price": info.get("regularMarketPrice"),
            "change_percent": info.get("regularMarketChangePercent", 0) * 100,
            "timestamp": datetime.fromtimestamp(info.get("regularMarketTime")).isoformat() if info.get("regularMarketTime") else datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

def get_crypto_data(symbol: str):
    try:
        data = yf.Ticker(symbol)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid symbol or no data")
        return {
            "symbol": info.get("symbol", symbol.upper()),
            "price": info.get("regularMarketPrice"),
            "change_percent": info.get("regularMarketChangePercent", 0) * 100,
            "market_cap": info.get("marketCap")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

def get_forex_data(pair: str):
    try:
        data = yf.Ticker(pair)
        info = data.info
        if not info.get('regularMarketPrice'):
            raise ValueError("Invalid pair or no data")
        return {
            "pair": info.get("shortName", pair.upper()),
            "rate": info.get("regularMarketPrice"),
            "timestamp": datetime.fromtimestamp(info.get("regularMarketTime")).isoformat() if info.get("regularMarketTime") else datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---- Endpoints ----
@app.get("/stock/quote")
def stock_quote(ticker: str = Query(...)):
    return get_stock_data(ticker)

@app.get("/crypto/quote")
def crypto_quote(symbol: str = Query(...)):
    return get_crypto_data(symbol)

@app.get("/forex/quote")
def forex_quote(pair: str = Query(...)):
    return get_forex_data(pair)

@app.get("/finnhub/quote")
def finnhub_quote(symbol: str = Query(...)):
    try:
        quote = finnhub_client.quote(symbol)
        return {
            "symbol": symbol,
            "current_price": quote["c"],
            "high": quote["h"],
            "low": quote["l"],
            "open": quote["o"],
            "prev_close": quote["pc"],
            "timestamp": quote["t"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/openapi.json")
def openapi():
    with open(BASE_DIR / "ncos_openapi.json") as f:
        return JSONResponse(content=json.load(f))

@app.get("/ai-plugin.json")
def plugin_manifest():
    with open(BASE_DIR / "ncos_ai_plugin.json") as f:
        return JSONResponse(content=json.load(f))

@app.get("/logo.png")
def logo():
    return FileResponse(BASE_DIR / "logo.png")

@app.get("/twelvedata/quote")
def twelvedata_quote(symbol: str = Query(..., description="Symbol, e.g. 'EUR/USD', 'XAU/USD', 'BTC/USD'")):
    return get_twelvedata_price(symbol)