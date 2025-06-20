# NCOS ZBAR API Deployment Guide

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements_zbar.txt
```

2. Run the API server:
```bash
python ncos_zbar_api.py
```

3. Test with the client:
```bash
python test_zbar_client.py
```

## API Endpoints

### 1. Execute ZBAR Strategy
**POST** `/strategy/zbar/execute_multi`

Executes ZBAR analysis on multi-timeframe data blocks.

### 2. Query Journal
**GET** `/journal/query`

Query parameters:
- `symbol`: Filter by trading symbol
- `strategy`: Filter by strategy name
- `session_id`: Filter by session
- `trace_id`: Get specific execution
- `limit`: Max results (default: 100)

### 3. Journal Statistics
**GET** `/journal/stats`

Returns:
- Total trades
- Pass/fail rates
- Average maturity scores
- Symbol distribution

## Integration with NCOS

To integrate with your existing NCOS system:

1. Replace the `ZBARAgent.process_multi_timeframe()` method with calls to your actual `zbar_agent.py`
2. Update the journal path to match your system configuration
3. Add authentication if needed
4. Deploy behind your NCOS API gateway

## Production Considerations

- Add proper error handling and validation
- Implement rate limiting
- Set up monitoring and alerting
- Use a proper database instead of JSONL for scale
- Add WebSocket support for real-time updates
