# scripts/test_api_endpoints.py

"""
Test ZanLink API endpoints for operational status and data structure.
Run this manually or hook into CI/test suite.
"""

import requests

BASE = "http://localhost:8000"

def check_status():
    res = requests.get(f"{BASE}/status")
    assert res.status_code == 200
    print("[✓] /status OK")

def check_events():
    res = requests.get(f"{BASE}/events/30T")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    print(f"[✓] /events/30T returned {len(res.json())} signals")

def check_macro():
    res = requests.get(f"{BASE}/macro/latest")
    assert res.status_code == 200
    macro = res.json()
    assert "bias" in macro and "headline" in macro
    print(f"[✓] /macro/latest: {macro['bias'].upper()} – {macro['headline']}")

if __name__ == "__main__":
    check_status()
    check_events()
    check_macro()
