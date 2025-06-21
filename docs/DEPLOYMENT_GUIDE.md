# NCOS v21.7.1 Deployment Guide

## Prerequisites

- Python 3.10+
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- Environment variables `FINNHUB_API_KEY` and `TWELVE_DATA_API_KEY` for market data access

## Deployment Steps

1. **Extract Package**
   ```bash
   tar -xzf ncos_v21_production_candidate.tar.gz
   cd ncOS_v21.7
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure System**
   Edit config/bootstrap.yaml as needed

4. **Start System**
   ```bash
   python start_ncos.py
   ```

5. **Monitor System**
   ```bash
   tail -f logs/ncos.log
   ```

## Production Considerations

- Set appropriate resource limits
- Configure logging rotation
- Enable monitoring/alerting
- Regular backup of state directory
