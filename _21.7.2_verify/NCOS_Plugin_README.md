
# NCOS Live Market Data Plugin - Implementation Guide

This package contains all the necessary components to deploy a live market data API, fully integrated with the NCOS architecture and ready to be used as a plugin for Large Language Models (LLMs) like OpenAI's GPTs.

## Components

1.  **`plugin_api_backend.py`**: A FastAPI server that acts as the API gateway. It fetches live data using `yfinance` and exposes it via REST endpoints.
2.  **`ncos_openapi.json`**: The OpenAPI 3.0 specification that defines the API's capabilities. This is the "instruction manual" for the LLM.
3.  **`ncos_ai_plugin.json`**: The manifest file required by OpenAI to register the API as a Custom GPT Action (Plugin).
4.  **`logo.png`**: A placeholder logo for the plugin.

## How It Works

1.  An LLM (like a Custom GPT) receives a user prompt, e.g., "What is the price of Bitcoin?".
2.  The LLM consults its available tools and, based on the description in `ncos_ai_plugin.json`, decides to use the `ncos_market_data_fetcher`.
3.  It uses `ncos_openapi.json` to understand how to call the correct endpoint, in this case, `/crypto/quote` with the parameter `symbol=BTC-USD`.
4.  A GET request is sent to your deployed `plugin_api_backend.py`.
5.  The FastAPI backend fetches the data from Yahoo Finance and returns a JSON response.
6.  The LLM receives the data and presents it to the user in a natural language format.

## Deployment Steps

### Step 1: Install Dependencies

Create a `requirements.txt` file with the following content:

```
fastapi
uvicorn[standard]
yfinance
python-multipart
```

Then install them:
```bash
pip install -r requirements.txt
```

### Set API Keys

Provide the required API keys as environment variables before launching the server:

```bash
export FINNHUB_API_KEY="your-finnhub-key"
export TWELVE_DATA_API_KEY="your-twelvedata-key"
```

### Step 2: Run Locally (for Testing)

You can run the API server on your local machine to test its functionality.

```bash
python plugin_api_backend.py
```

The API will be available at `http://localhost:8000`. You can test the endpoints in your browser:
-   `http://localhost:8000/stock/quote?ticker=MSFT`
-   `http://localhost:8000/crypto/quote?symbol=ETH-USD`

### Step 3: Deploy to a Public Server

For an LLM to use your plugin, the API must be accessible on the public internet (HTTPS).

1.  **Choose a Hosting Provider**: Services like [Render](https://render.com/), [Railway](https://railway.app/), or [Vercel](https://vercel.com/) are excellent for deploying Python applications.
2.  **Deploy the Application**: Follow your provider's instructions to deploy the `plugin_api_backend.py` application.
3.  **Get Your Public URL**: Once deployed, you will get a public URL, for example: `https://ncos-market-data.onrender.com`.

### Step 4: Update the Manifest File

Open `ncos_ai_plugin.json` and replace the placeholder URLs with your public URL.

```json
{
  ...
  "api": {
    "type": "openapi",
    "url": "https://YOUR_PUBLIC_URL/openapi.json",
    "is_user_authenticated": false
  },
  "logo_url": "https://YOUR_PUBLIC_URL/logo.png",
  ...
}
```
You will need to re-host this updated manifest file or ensure your backend serves the dynamically updated version.

### Step 5: Register with the LLM

1.  Go to the platform where you are building your LLM application (e.g., the OpenAI Custom GPT builder).
2.  Find the section for adding "Actions" or "Tools".
3.  Provide the URL to your hosted `ncos_ai_plugin.json` manifest file.
4.  The platform will validate the manifest and register the tool.

Your NCOS-powered market data assistant is now ready!
