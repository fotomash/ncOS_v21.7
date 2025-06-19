"""
Production Configuration for NCOS v21
Environment-specific settings with validation
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import yaml
import json

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    directory: str = Field(default="/var/log/ncos")
    max_size_mb: int = Field(default=100, ge=1, le=1000)
    backup_count: int = Field(default=10, ge=1, le=50)
    structured: bool = Field(default=True)

class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    failure_threshold: int = Field(default=5, ge=1, le=20)
    success_threshold: int = Field(default=2, ge=1, le=10)
    timeout_seconds: int = Field(default=60, ge=10, le=300)
    half_open_attempts: int = Field(default=3, ge=1, le=10)

class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    enabled: bool = Field(default=True)
    port: int = Field(default=9090, ge=1024, le=65535)
    retention_minutes: int = Field(default=60, ge=10, le=1440)
    collection_interval: int = Field(default=10, ge=1, le=60)

class AgentConfig(BaseModel):
    """Agent-specific configuration"""
    timeout_seconds: int = Field(default=30, ge=5, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    memory_limit_mb: Optional[int] = Field(default=None, ge=100, le=10000)

class ProductionConfig(BaseModel):
    """Main production configuration"""
    environment: str = Field(default="production", pattern="^(development|staging|production)$")
    version: str = Field(default="v21.0.0")

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)

    # Feature flags
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "parquet_processing": False,  # Disabled by default
        "vector_persistence": False,  # Disabled by default
        "zbar_integration": False,    # Disabled by default
        "async_workflows": True,
        "circuit_breakers": True,
        "structured_logging": True
    })

    @validator('environment')
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

def load_production_config(config_path: Optional[str] = None) -> ProductionConfig:
    """Load production configuration with environment variable overrides"""

    # Default configuration
    config_dict = {}

    # Load from file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

    # Environment variable overrides
    env_mappings = {
        "NCOS_ENVIRONMENT": "environment",
        "NCOS_LOG_LEVEL": "logging.level",
        "NCOS_LOG_DIR": "logging.directory",
        "NCOS_MONITORING_PORT": "monitoring.port",
        "NCOS_CIRCUIT_BREAKER_ENABLED": "features.circuit_breakers"
    }

    for env_var, config_path in env_mappings.items():
        if env_var in os.environ:
            # Navigate nested path
            parts = config_path.split('.')
            current = config_dict

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the value with type conversion
            value = os.environ[env_var]
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)

            current[parts[-1]] = value

    return ProductionConfig(**config_dict)

# Production configuration file template
PRODUCTION_CONFIG_YAML = """
# NCOS v21 Production Configuration
environment: production
version: v21.0.0

logging:
  level: INFO
  directory: /var/log/ncos
  max_size_mb: 100
  backup_count: 10
  structured: true

circuit_breaker:
  failure_threshold: 5
  success_threshold: 2
  timeout_seconds: 60
  half_open_attempts: 3

monitoring:
  enabled: true
  port: 9090
  retention_minutes: 60
  collection_interval: 10

# Agent-specific configurations
agents:
  MasterOrchestrator:
    timeout_seconds: 60
    max_retries: 3

  SMCRouter:
    timeout_seconds: 30
    max_retries: 5

  ParquetIngestor:
    timeout_seconds: 120
    max_retries: 2
    memory_limit_mb: 2048

# Feature flags
features:
  parquet_processing: false  # Enable only when needed
  vector_persistence: false  # Enable only when needed
  zbar_integration: false    # Enable only when needed
  async_workflows: true
  circuit_breakers: true
  structured_logging: true
"""

# Save the production config template
with open('production_config.yaml', 'w') as f:
    f.write(PRODUCTION_CONFIG_YAML)
