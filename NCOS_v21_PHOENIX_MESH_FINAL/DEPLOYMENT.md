# NCOS v21 Deployment Guide

## Production Deployment

### 1. System Requirements
- Python 3.9+
- 8GB RAM minimum (16GB recommended)
- 10GB disk space
- Ubuntu 20.04+ or similar

### 2. Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV NCOS_CONFIG=/app/config/production.yaml

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ncos-v21
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ncos
  template:
    metadata:
      labels:
        app: ncos
    spec:
      containers:
      - name: ncos
        image: ncos:v21
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

### 4. Environment Variables
```bash
export NCOS_ENV=production
export NCOS_CONFIG=/path/to/config.yaml
export NCOS_LOG_LEVEL=INFO
export NCOS_API_KEY=your-api-key
export NCOS_DB_URL=postgresql://user:pass@host/db
```

### 5. Monitoring Setup
- Prometheus endpoint: `/metrics`
- Health check: `/health`
- Ready check: `/ready`

### 6. Backup Strategy
- L3 persistent memory: Daily backups
- Configuration: Version controlled
- Logs: Rotate daily, keep 30 days
