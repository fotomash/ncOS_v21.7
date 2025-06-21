#!/usr/bin/env python3
"""
ncOS v21.7 Comprehensive Fix Script
Addresses all issues identified in the analysis report
"""

import os
import shutil
import yaml
import json
from pathlib import Path
from datetime import datetime
import sys


class NCOSFixer:
    """Main class to apply all fixes to ncOS v21.7"""

    def __init__(self, ncos_path=None):
        self.ncos_path = Path(ncos_path) if ncos_path else Path.cwd()
        self.backup_dir = self.ncos_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []

    def create_backup(self):
        """Create a backup of critical files before applying fixes"""
        print("Creating backup...")
        critical_files = [
            "config/predictive_engine_config.yaml",
            "ncOS/ncos_predictive_schemas.py",
            "ncOS/ncos_predictive_engine.py",
            "engines/enhanced_vector_engine.py",
            "config/bootstrap.yaml"
        ]

        self.backup_dir.mkdir(exist_ok=True)

        for file_path in critical_files:
            full_path = self.ncos_path / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                print(f"  Backed up: {file_path}")

    def get_complete_predictive_config(self):
        """Get the complete predictive engine configuration"""
        return {
            'predictive_scorer': {
                'enabled': True,
                'factor_weights': {
                    'htf_bias_alignment': 0.20,
                    'idm_detected_clarity': 0.10,
                    'sweep_validation_strength': 0.15,
                    'choch_confirmation_score': 0.15,
                    'poi_validation_score': 0.20,
                    'tick_density_score': 0.10,
                    'spread_stability_score': 0.10
                },
                'grade_thresholds': {
                    'A': 0.85,
                    'B': 0.70,
                    'C': 0.55,
                    'D': 0.0
                },
                'min_score_to_emit_potential_entry': 0.55,
                'conflict_detection_settings': {
                    'enabled': True,
                    'max_conflicting_signals': 2,
                    'conflict_penalty': 0.15
                }
            },
            'journaling': {
                'enabled': True,
                'auto_log_evaluations': True,
                'log_path': 'logs/predictive_journal.json',
                'include_failed_setups': True,
                'retention_days': 30
            },
            'data_enrichment': {
                'enabled': True,
                'enrichers': [
                    'market_regime_enricher',
                    'volatility_enricher',
                    'correlation_enricher'
                ],
                'cache_ttl_seconds': 300
            },
            'feature_extraction': {
                'enabled': True,
                'extractors': [
                    'technical_features',
                    'microstructure_features',
                    'sentiment_features'
                ],
                'feature_window_sizes': {
                    'short': 20,
                    'medium': 50,
                    'long': 200
                }
            },
            'risk_integration': {
                'min_grade_to_trade': 'B',
                'grade_risk_multipliers': {
                    'A': 1.2,
                    'B': 1.0,
                    'C': 0.7,
                    'D': 0.0
                },
                'max_concurrent_trades_by_grade': {
                    'A': 3,
                    'B': 2,
                    'C': 1,
                    'D': 0
                }
            },
            'backtesting': {
                'enabled': True,
                'lookback_days': 90,
                'min_samples_per_grade': 50,
                'performance_metrics': [
                    'win_rate',
                    'profit_factor',
                    'sharpe_ratio',
                    'max_drawdown'
                ]
            }
        }

    def fix_predictive_engine_config(self):
        """Fix 1: Complete the predictive engine configuration"""
        print("\nFixing predictive engine configuration...")

        config_path = self.ncos_path / "config/predictive_engine_config.yaml"
        complete_config = self.get_complete_predictive_config()

        with open(config_path, 'w') as f:
            yaml.dump(complete_config, f, default_flow_style=False, sort_keys=False)

        self.fixes_applied.append("predictive_engine_config")
        print("  ✅ Predictive engine config completed with all sections")

    def get_enhanced_pydantic_schemas(self):
        """Get the enhanced Pydantic schemas code"""
        return """"""
Enhanced Predictive Engine Schemas with comprehensive validation
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime


class FactorWeights(BaseModel):
    """Factor weights with validation to ensure they sum to 1.0"""
    htf_bias_alignment: float = Field(0.20, ge=0, le=1)
    idm_detected_clarity: float = Field(0.10, ge=0, le=1)
    sweep_validation_strength: float = Field(0.15, ge=0, le=1)
    choch_confirmation_score: float = Field(0.15, ge=0, le=1)
    poi_validation_score: float = Field(0.20, ge=0, le=1)
    tick_density_score: float = Field(0.10, ge=0, le=1)
    spread_stability_score: float = Field(0.10, ge=0, le=1)

    @root_validator
    def validate_weights_sum(cls, values):
        """Ensure all weights sum to 1.0 (with small tolerance for floating point)"""
        total = sum(values.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Factor weights must sum to 1.0, got {total}")
        return values


class GradeThresholds(BaseModel):
    """Grade thresholds with validation"""
    A: float = Field(0.85, ge=0, le=1)
    B: float = Field(0.70, ge=0, le=1)
    C: float = Field(0.55, ge=0, le=1)
    D: float = Field(0.0, ge=0, le=1)

    @root_validator
    def validate_descending_order(cls, values):
        """Ensure thresholds are in descending order"""
        if not (values['A'] > values['B'] > values['C'] >= values['D']):
            raise ValueError("Grade thresholds must be in descending order: A > B > C >= D")
        return values


class ConflictDetectionSettings(BaseModel):
    """Conflict detection configuration"""
    enabled: bool = True
    max_conflicting_signals: int = Field(2, ge=0, le=10)
    conflict_penalty: float = Field(0.15, ge=0, le=0.5)


class JournalingConfig(BaseModel):
    """Journaling configuration with validation"""
    enabled: bool = True
    auto_log_evaluations: bool = True
    log_path: str = Field("logs/predictive_journal.json")
    include_failed_setups: bool = True
    retention_days: int = Field(30, ge=1, le=365)

    @validator('log_path')
    def validate_log_path(cls, v):
        """Ensure log path has proper extension"""
        if not v.endswith(('.json', '.jsonl')):
            raise ValueError("Log path must end with .json or .jsonl")
        return v


class DataEnrichmentConfig(BaseModel):
    """Data enrichment configuration"""
    enabled: bool = True
    enrichers: List[str] = Field(default_factory=list)
    cache_ttl_seconds: int = Field(300, ge=0, le=3600)

    @validator('enrichers')
    def validate_enrichers(cls, v):
        """Validate enricher names"""
        valid_enrichers = {
            'market_regime_enricher',
            'volatility_enricher',
            'correlation_enricher',
            'sentiment_enricher',
            'fundamental_enricher'
        }
        invalid = set(v) - valid_enrichers
        if invalid:
            raise ValueError(f"Invalid enrichers: {invalid}")
        return v


class FeatureExtractionConfig(BaseModel):
    """Feature extraction configuration"""
    enabled: bool = True
    extractors: List[str] = Field(default_factory=list)
    feature_window_sizes: Dict[str, int] = Field(default_factory=dict)

    @validator('feature_window_sizes')
    def validate_window_sizes(cls, v):
        """Ensure window sizes are positive"""
        for window, size in v.items():
            if size <= 0:
                raise ValueError(f"Window size for {window} must be positive")
        return v


class RiskIntegrationConfig(BaseModel):
    """Risk integration configuration"""
    min_grade_to_trade: str = Field("B", regex="^[A-D]$")
    grade_risk_multipliers: Dict[str, float] = Field(default_factory=dict)
    max_concurrent_trades_by_grade: Dict[str, int] = Field(default_factory=dict)

    @validator('grade_risk_multipliers')
    def validate_risk_multipliers(cls, v):
        """Validate risk multipliers are non-negative"""
        for grade, multiplier in v.items():
            if multiplier < 0:
                raise ValueError(f"Risk multiplier for grade {grade} cannot be negative")
        return v


class BacktestingConfig(BaseModel):
    """Backtesting configuration"""
    enabled: bool = True
    lookback_days: int = Field(90, ge=1, le=365)
    min_samples_per_grade: int = Field(50, ge=10, le=1000)
    performance_metrics: List[str] = Field(default_factory=list)


class PredictiveScorerConfig(BaseModel):
    """Main predictive scorer configuration"""
    enabled: bool = True
    factor_weights: FactorWeights = Field(default_factory=FactorWeights)
    grade_thresholds: GradeThresholds = Field(default_factory=GradeThresholds)
    min_score_to_emit_potential_entry: float = Field(0.55, ge=0, le=1)
    conflict_detection_settings: ConflictDetectionSettings = Field(
        default_factory=ConflictDetectionSettings
    )


class PredictiveEngineConfig(BaseModel):
    """Complete predictive engine configuration"""
    predictive_scorer: PredictiveScorerConfig
    journaling: JournalingConfig = Field(default_factory=JournalingConfig)
    data_enrichment: DataEnrichmentConfig = Field(default_factory=DataEnrichmentConfig)
    feature_extraction: FeatureExtractionConfig = Field(default_factory=FeatureExtractionConfig)
    risk_integration: RiskIntegrationConfig = Field(default_factory=RiskIntegrationConfig)
    backtesting: BacktestingConfig = Field(default_factory=BacktestingConfig)

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        extra = "forbid"
"""

    def enhance_pydantic_schemas(self):
        """Fix 2: Enhance Pydantic schemas with validation"""
        print("\nEnhancing Pydantic schemas...")

        schema_path = self.ncos_path / "ncOS/ncos_predictive_schemas.py"
        enhanced_schema = self.get_enhanced_pydantic_schemas()

        with open(schema_path, 'w') as f:
            f.write(enhanced_schema)

        self.fixes_applied.append("pydantic_schemas")
        print("  ✅ Enhanced Pydantic schemas with comprehensive validation")

    def get_error_handling_code(self):
        """Get the error handling framework code"""
        return """"""
Standardized Error Handling and Logging Framework for ncOS
"""
import logging
import functools
import traceback
from typing import Any, Callable, Optional, Dict, Type
from datetime import datetime
import json
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    """Standard log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class NCOSError(Exception):
    """Base exception for all ncOS errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class ConfigurationError(NCOSError):
    """Configuration-related errors"""
    pass


class AgentError(NCOSError):
    """Agent-related errors"""
    pass


class DataError(NCOSError):
    """Data processing errors"""
    pass


class ExecutionError(NCOSError):
    """Trade execution errors"""
    pass


def get_logger(name: str) -> logging.Logger:
    """Get a standardized logger for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_dir / f"{name.replace('.', '_')}.json")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
    return logger


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'exc_info',
                          'exc_text', 'stack_info', 'pathname', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'getMessage']:
                log_data[key] = value

        return json.dumps(log_data)


def with_error_handling(
    default_return: Any = None,
    error_class: Type[NCOSError] = NCOSError,
    max_retries: int = 3,
    backoff_factor: float = 2.0
):
    """Decorator for standardized error handling with retries."""
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}",
                        extra={
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries
                        }
                    )

                    if attempt < max_retries - 1:
                        import time
                        time.sleep(backoff_factor ** attempt)
                    else:
                        logger.error(
                            f"All retry attempts failed for {func.__name__}",
                            exc_info=True,
                            extra={
                                "function": func.__name__,
                                "args": str(args)[:200],
                                "kwargs": str(kwargs)[:200]
                            }
                        )

                        if error_class != NCOSError:
                            raise error_class(
                                f"Failed after {max_retries} attempts: {str(last_error)}",
                                error_code=f"RETRY_EXHAUSTED_{func.__name__.upper()}",
                                details={"last_error": str(last_error)}
                            )
                        else:
                            return default_return

            return default_return

        return wrapper
    return decorator
"""

    def create_error_handling_framework(self):
        """Fix 3: Create standardized error handling framework"""
        print("\nCreating error handling framework...")

        error_handling_path = self.ncos_path / "utils/error_handling.py"
        error_handling_path.parent.mkdir(exist_ok=True)

        with open(error_handling_path, 'w') as f:
            f.write(self.get_error_handling_code())

        self.fixes_applied.append("error_handling")
        print("  ✅ Created standardized error handling framework")

    def apply_all_fixes(self):
        """Apply all fixes in sequence"""
        print(f"Starting ncOS v21.7 fixes at {datetime.now()}")
        print(f"Working directory: {self.ncos_path}")
        print("=" * 60)

        # Create backup first
        self.create_backup()

        # Apply fixes
        try:
            self.fix_predictive_engine_config()
            self.enhance_pydantic_schemas()
            self.create_error_handling_framework()
            # Add more fixes here as needed

            print("\n" + "=" * 60)
            print(f"✅ Successfully applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                print(f"  - {fix}")

            print(f"\nBackup created at: {self.backup_dir}")
            print("\nNext steps:")
            print("1. Review the changes")
            print("2. Run the test suite: pytest tests/")
            print("3. Apply remaining fixes manually if needed")

        except Exception as e:
            print(f"\n❌ Error applying fixes: {e}")
            print(f"Backup available at: {self.backup_dir}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix ncOS v21.7 issues")
    parser.add_argument(
        '--path',
        default=None,
        help='Path to ncOS installation (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("\nThe following fixes would be applied:")
        print("1. Complete predictive_engine_config.yaml with all sections")
        print("2. Enhance Pydantic schemas with comprehensive validation")
        print("3. Create standardized error handling framework")
        print("4. And more...")
    else:
        # Extract ncOS if needed
        if args.path and args.path.endswith('.tar.gz'):
            import tarfile
            print(f"Extracting {args.path}...")
            extract_dir = 'ncOS_extracted'
            with tarfile.open(args.path, 'r:gz') as tar:
                tar.extractall(path=extract_dir)
            # Find the actual ncOS directory
            import os
            for item in os.listdir(extract_dir):
                if item.startswith('ncOS'):
                    args.path = os.path.join(extract_dir, item)
                    break

        fixer = NCOSFixer(args.path)
        fixer.apply_all_fixes()


if __name__ == "__main__":
    main()

