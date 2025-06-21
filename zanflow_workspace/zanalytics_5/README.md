# ZDX: Zanalytics-DXtrade Execution Bridge

## Overview

ZDX is the neural bridge between your AI trading system (ZANALYTICS) and the DXtrade institutional trading platform. It enables:
- Order execution via REST API
- Live metrics intake via AWS SQS
- Risk and journal event routing

## Files

- `zdx_core.py`: Send limit orders to DXtrade with HMAC auth
- `listen_to_metrics.py`: SQS consumer for real-time equity/margin monitoring
- `.env`: Secure credential storage

## Requirements

- Python 3.8+
- DXtrade demo or production credentials
- AWS credentials + configured SQS queues
- Libraries: `requests`, `boto3`, `python-dotenv`

## How to Run

1. Place your credentials in `.env`
2. Run:

```bash
python core/zdx_core.py       # Send a limit order
python consumers/listen_to_metrics.py  # Start metrics listener
```

## Architecture

```text
ZANALYTICS
    |
    | → entry.json
    | → trade_log.csv
    |
  [ZDX]
    |        ↘ DX REST API (/orders)
    |         ↘ SQS (metrics, events, fills)
    |
DXtrade System
```

---

Ready for full automation, learning, and institutional-grade execution.
