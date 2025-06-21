# Required Environment Variables

The NCOS system relies on several environment variables to configure runtime behavior.
If a variable is not provided, the default value from `production/production_config.py` will be used.

| Variable                       | Default                 | Description                                |
|--------------------------------|-------------------------|--------------------------------------------|
| `FINNHUB_API_KEY`              | *(none)*                | API key for market data integration        |
| `TWELVE_DATA_API_KEY`          | *(none)*                | API key for alternative market data        |
| `NCOS_ENVIRONMENT`             | `production`            | Deployment environment name                |
| `NCOS_LOG_LEVEL`               | `INFO`                  | Logging verbosity                          |
| `NCOS_LOG_DIR`                 | `/var/log/ncos`         | Directory for application logs             |
| `NCOS_MONITORING_PORT`         | `9090`                  | Port for the monitoring service            |
| `NCOS_CIRCUIT_BREAKER_ENABLED` | `true`                  | Enable circuit breaker logic               |
| `NCOS_JOURNAL_API_URL`         | `http://localhost:8000` | Journal API endpoint                       |
| `NCOS_DASHBOARD_API_URL`       | `http://localhost:8001` | Dashboard API endpoint                     |
| `NCOS_LLM_API_URL`             | `http://localhost:8002` | LLM assistant endpoint                     |
| `NCOS_CONFIG_PATH`             | *(none)*                | Optional path to a YAML configuration file |

All of these variables can also be provided in a YAML file loaded via
`load_production_config`. Environment variables take precedence over values
in the configuration file.
