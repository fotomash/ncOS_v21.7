
import requests
import json

# Example: Execute ZBAR strategy with multi-timeframe data
def test_zbar_execution():
    url = "http://localhost:8001/strategy/zbar/execute_multi"

    # Sample multi-timeframe data
    payload = {
        "strategy": "ISPTS_v14",
        "asset": "XAUUSD",
        "blocks": [
            {
                "id": "XAUUSD_M1",
                "timeframe": "M1",
                "columns": ["timestamp", "open", "high", "low", "close", "volume"],
                "data": [
                    ["2025-06-20T08:30:00Z", 2358.5, 2360.2, 2358.1, 2359.8, 1250],
                    ["2025-06-20T08:31:00Z", 2359.8, 2361.5, 2359.5, 2360.1, 1180]
                ]
            },
            {
                "id": "XAUUSD_H1",
                "timeframe": "H1",
                "columns": ["timestamp", "open", "high", "low", "close", "volume"],
                "data": [
                    ["2025-06-20T08:00:00Z", 2355.0, 2361.5, 2354.5, 2360.1, 15000]
                ]
            }
        ],
        "context": {
            "initial_htf_bias": "bullish",
            "trace_id": "zbar_test_003",
            "session_id": "london_2025_06_20"
        }
    }

    response = requests.post(url, json=payload)
    print("ZBAR Execution Response:")
    print(json.dumps(response.json(), indent=2))

    # Query the journal
    journal_url = "http://localhost:8001/journal/query"
    params = {"symbol": "XAUUSD", "limit": 5}
    journal_response = requests.get(journal_url, params=params)
    print("\nJournal Entries:")
    print(json.dumps(journal_response.json(), indent=2))

if __name__ == "__main__":
    test_zbar_execution()
