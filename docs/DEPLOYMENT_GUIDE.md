# NCOS v21 Deployment Guide

## Prerequisites
- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- 10GB disk space

## Deployment Steps

1. **Extract Package**
   ```bash
   tar -xzf ncos_v21_production_candidate.tar.gz
   cd ncos_v21_deployment
   ```

2. **Run Deployment Script**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Configure System**
   Edit configs/bootstrap.yaml as needed

4. **Start System**
   ```bash
   ./start_ncos.sh
   ```

5. **Monitor System**
   ```bash
   ./status_ncos.sh
   tail -f logs/ncos.log
   ```

## Production Considerations
- Set appropriate resource limits
- Configure logging rotation
- Enable monitoring/alerting
- Regular backup of state directory
