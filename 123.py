# Create the master fix script
fix_script = '''#!/usr/bin/env python3
"""
ncOS v21.7 Comprehensive Fix Script
Addresses all issues identified in the analysis report
Created: {timestamp}
"""

import os
import shutil
import yaml
import json
from pathlib import Path
from datetime import datetime
import tarfile
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
    
    def fix_predictive_engine_config(self):
        """Fix 1: Complete the predictive engine configuration"""
        print("\\nFixing predictive engine configuration...")
        
        config_path = self.ncos_path / "config/predictive_engine_config.yaml"
        
        complete_config = {
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
        
        with open(config_path, 'w') as f:
            yaml.dump(complete_config, f, default_flow_style=False, sort_keys=False)
        
        self.fixes_applied.append("predictive_engine_config")
        print("  ✅ Predictive engine config completed with all sections")
    
    def enhance_pydantic_schemas(self):
        """Fix 2: Enhance Pydantic schemas with validation"""
        print("\\nEnhancing Pydantic schemas...")
        
        schema_path = self.ncos_path / "ncOS/ncos_predictive_schemas.py"
        
        enhanced_schema = """\"\"\"
Enhanced Predictive Engine Schemas with comprehensive validation
\"\"\"
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime


class FactorWeights(BaseModel):
    \"\"\"Factor weights with validation to ensure they sum to 1.0\"\"\"
    htf_bias_alignment: float = Field(0.20, ge=0, le=1)
    idm_detected_clarity: float = Field(0.10, ge=0, le=1)
    sweep_validation_strength: float = Field(0.15, ge=0, le=1)
    choch_confirmation_score: float = Field(0.15, ge=0, le=1)
    poi_validation_score: float = Field(0.20, ge=0, le=1)
    tick_density_score: float = Field(0.10, ge=0, le=1)
    spread_stability_score: float = Field(0.10, ge=0, le=1)
    
    @root_validator
    def validate_weights_sum(cls, values):
        \"\"\"Ensure all weights sum to 1.0 (with small tolerance for floating point)\"\"\"
        total = sum(values.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Factor weights must sum to 1.0, got {total}")
        return values


class GradeThresholds(BaseModel):
    \"\"\"Grade thresholds with validation\"\"\"
    A: float = Field(0.85, ge=0, le=1)
    B: float = Field(0.70, ge=0, le=1)
    C: float = Field(0.55, ge=0, le=1)
    D: float = Field(0.0, ge=0, le=1)
    
    @root_validator
    def validate_descending_order(cls, values):
        \"\"\"Ensure thresholds are in descending order\"\"\"
        if not (values['A'] > values['B'] > values['C'] >= values['D']):
            raise ValueError("Grade thresholds must be in descending order: A > B > C >= D")
        return values


class ConflictDetectionSettings(BaseModel):
    \"\"\"Conflict detection configuration\"\"\"
    enabled: bool = True
    max_conflicting_signals: int = Field(2, ge=0, le=10)
    conflict_penalty: float = Field(0.15, ge=0, le=0.5)


class JournalingConfig(BaseModel):
    \"\"\"Journaling configuration with validation\"\"\"
    enabled: bool = True
    auto_log_evaluations: bool = True
    log_path: str = Field("logs/predictive_journal.json")
    include_failed_setups: bool = True
    retention_days: int = Field(30, ge=1, le=365)
    
    @validator('log_path')
    def validate_log_path(cls, v):
        \"\"\"Ensure log path has proper extension\"\"\"
        if not v.endswith(('.json', '.jsonl')):
            raise ValueError("Log path must end with .json or .jsonl")
        return v


class DataEnrichmentConfig(BaseModel):
    \"\"\"Data enrichment configuration\"\"\"
    enabled: bool = True
    enrichers: List[str] = Field(default_factory=list)
    cache_ttl_seconds: int = Field(300, ge=0, le=3600)
    
    @validator('enrichers')
    def validate_enrichers(cls, v):
        \"\"\"Validate enricher names\"\"\"
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
    \"\"\"Feature extraction configuration\"\"\"
    enabled: bool = True
    extractors: List[str] = Field(default_factory=list)
    feature_window_sizes: Dict[str, int] = Field(default_factory=dict)
    
    @validator('feature_window_sizes')
    def validate_window_sizes(cls, v):
        \"\"\"Ensure window sizes are positive\"\"\"
        for window, size in v.items():
            if size <= 0:
                raise ValueError(f"Window size for {window} must be positive")
        return v


class RiskIntegrationConfig(BaseModel):
    \"\"\"Risk integration configuration\"\"\"
    min_grade_to_trade: str = Field("B", regex="^[A-D]$")
    grade_risk_multipliers: Dict[str, float] = Field(default_factory=dict)
    max_concurrent_trades_by_grade: Dict[str, int] = Field(default_factory=dict)
    
    @validator('grade_risk_multipliers')
    def validate_risk_multipliers(cls, v):
        \"\"\"Validate risk multipliers are non-negative\"\"\"
        for grade, multiplier in v.items():
            if multiplier < 0:
                raise ValueError(f"Risk multiplier for grade {grade} cannot be negative")
        return v


class BacktestingConfig(BaseModel):
    \"\"\"Backtesting configuration\"\"\"
    enabled: bool = True
    lookback_days: int = Field(90, ge=1, le=365)
    min_samples_per_grade: int = Field(50, ge=10, le=1000)
    performance_metrics: List[str] = Field(default_factory=list)


class PredictiveScorerConfig(BaseModel):
    \"\"\"Main predictive scorer configuration\"\"\"
    enabled: bool = True
    factor_weights: FactorWeights = Field(default_factory=FactorWeights)
    grade_thresholds: GradeThresholds = Field(default_factory=GradeThresholds)
    min_score_to_emit_potential_entry: float = Field(0.55, ge=0, le=1)
    conflict_detection_settings: ConflictDetectionSettings = Field(
        default_factory=ConflictDetectionSettings
    )


class PredictiveEngineConfig(BaseModel):
    \"\"\"Complete predictive engine configuration\"\"\"
    predictive_scorer: PredictiveScorerConfig
    journaling: JournalingConfig = Field(default_factory=JournalingConfig)
    data_enrichment: DataEnrichmentConfig = Field(default_factory=DataEnrichmentConfig)
    feature_extraction: FeatureExtractionConfig = Field(default_factory=FeatureExtractionConfig)
    risk_integration: RiskIntegrationConfig = Field(default_factory=RiskIntegrationConfig)
    backtesting: BacktestingConfig = Field(default_factory=BacktestingConfig)
    
    class Config:
        \"\"\"Pydantic configuration\"\"\"
        validate_assignment = True
        extra = "forbid"


# Export for backward compatibility
__all__ = [
    'PredictiveEngineConfig',
    'PredictiveScorerConfig',
    'FactorWeights',
    'GradeThresholds',
    'ConflictDetectionSettings',
    'JournalingConfig',
    'DataEnrichmentConfig',
    'FeatureExtractionConfig',
    'RiskIntegrationConfig',
    'BacktestingConfig'
]
"""
        
        with open(schema_path, 'w') as f:
            f.write(enhanced_schema)
        
        self.fixes_applied.append("pydantic_schemas")
        print("  ✅ Enhanced Pydantic schemas with comprehensive validation")
    
    def create_error_handling_framework(self):
        """Fix 3: Create standardized error handling framework"""
        print("\\nCreating error handling framework...")
        
        error_handling_path = self.ncos_path / "utils/error_handling.py"
        error_handling_path.parent.mkdir(exist_ok=True)
        
        with open(error_handling_path, 'w') as f:
            f.write(ERROR_HANDLING_CODE)
        
        self.fixes_applied.append("error_handling")
        print("  ✅ Created standardized error handling framework")
    
    def enhance_predictive_engine(self):
        """Fix 4: Enhance predictive engine with full A/B/C/D grading"""
        print("\\nEnhancing predictive engine...")
        
        engine_path = self.ncos_path / "ncOS/ncos_predictive_engine.py"
        
        # Read the current engine
        if engine_path.exists():
            with open(engine_path, 'r') as f:
                engine_content = f.read()
            
            # Check if D grade is properly implemented
            if 'grade_risk_multipliers' not in engine_content:
                # Add risk multiplier support
                risk_integration = """
    def apply_risk_multipliers(self, grade: str, base_risk: float) -> float:
        \"\"\"Apply grade-based risk multipliers\"\"\"
        if hasattr(self.config, 'risk_integration'):
            multipliers = self.config.risk_integration.grade_risk_multipliers
            return base_risk * multipliers.get(grade, 1.0)
        return base_risk
    
    def should_trade(self, grade: str) -> bool:
        \"\"\"Check if grade meets minimum trading threshold\"\"\"
        if hasattr(self.config, 'risk_integration'):
            min_grade = self.config.risk_integration.min_grade_to_trade
            grade_order = ['A', 'B', 'C', 'D']
            return grade_order.index(grade) <= grade_order.index(min_grade)
        return grade != 'D'
"""
                # Insert before the last class method
                engine_content = engine_content.replace(
                    "def _calculate_grade(self, maturity_score: float) -> str:",
                    risk_integration + "\\n    def _calculate_grade(self, maturity_score: float) -> str:"
                )
            
            with open(engine_path, 'w') as f:
                f.write(engine_content)
        
        self.fixes_applied.append("predictive_engine")
        print("  ✅ Enhanced predictive engine with full grading system")
    
    def complete_vector_engine(self):
        """Fix 5: Complete the enhanced vector engine implementation"""
        print("\\nCompleting vector engine implementation...")
        
        vector_path = self.ncos_path / "engines/enhanced_vector_engine.py"
        
        with open(vector_path, 'w') as f:
            f.write(VECTOR_ENGINE_CODE)
        
        self.fixes_applied.append("vector_engine")
        print("  ✅ Completed enhanced vector engine with pattern matching")
    
    def standardize_logging(self):
        """Fix 6: Standardize logging across all agents"""
        print("\\nStandardizing logging...")
        
        # Update logging configuration
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]"
                },
                "json": {
                    "class": "utils.error_handling.JsonFormatter"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "json",
                    "filename": "logs/ncos.json",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "level": "INFO",
                    "handlers": ["console", "file"]
                }
            }
        }
        
        config_path = self.ncos_path / "config/logging_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(log_config, f, default_flow_style=False)
        
        self.fixes_applied.append("logging")
        print("  ✅ Standardized logging configuration")
    
    def create_strategy_loader(self):
        """Fix 7: Create dynamic strategy loader"""
        print("\\nCreating strategy loader...")
        
        strategy_loader = """\"\"\"
Dynamic Strategy Loader for ncOS
\"\"\"
import importlib
import inspect
from typing import Dict, List, Any, Type
from pathlib import Path
import yaml

from utils.error_handling import get_logger, ConfigurationError


logger = get_logger(__name__)


class StrategyLoader:
    \"\"\"Dynamic strategy loader for ncOS\"\"\"
    
    def __init__(self, strategies_dir: Path = Path("strategies")):
        self.strategies_dir = strategies_dir
        self.loaded_strategies: Dict[str, Any] = {}
        self.strategy_configs: Dict[str, Dict] = {}
        
    def load_strategy(self, strategy_name: str) -> Any:
        \"\"\"Load a strategy by name\"\"\"
        if strategy_name in self.loaded_strategies:
            return self.loaded_strategies[strategy_name]
        
        # Load strategy configuration
        config_path = self.strategies_dir / f"{strategy_name}_config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.strategy_configs[strategy_name] = yaml.safe_load(f)
        
        # Load strategy module
        module_path = self.strategies_dir / f"{strategy_name}.py"
        if not module_path.exists():
            raise ConfigurationError(f"Strategy module not found: {strategy_name}")
        
        # Dynamic import
        spec = importlib.util.spec_from_file_location(strategy_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find strategy class
        strategy_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith('Strategy'):
                strategy_class = obj
                break
        
        if not strategy_class:
            raise ConfigurationError(f"No strategy class found in {strategy_name}")
        
        # Instantiate strategy
        config = self.strategy_configs.get(strategy_name, {})
        strategy_instance = strategy_class(config)
        
        self.loaded_strategies[strategy_name] = strategy_instance
        logger.info(f"Loaded strategy: {strategy_name}")
        
        return strategy_instance
    
    def load_all_strategies(self) -> Dict[str, Any]:
        \"\"\"Load all available strategies\"\"\"
        strategy_files = list(self.strategies_dir.glob("*.py"))
        
        for strategy_file in strategy_files:
            if strategy_file.stem.startswith('_'):
                continue
            
            try:
                self.load_strategy(strategy_file.stem)
            except Exception as e:
                logger.error(f"Failed to load strategy {strategy_file.stem}: {e}")
        
        return self.loaded_strategies
    
    def reload_strategy(self, strategy_name: str) -> Any:
        \"\"\"Reload a strategy (useful for development)\"\"\"
        if strategy_name in self.loaded_strategies:
            del self.loaded_strategies[strategy_name]
        
        return self.load_strategy(strategy_name)
"""
        
        loader_path = self.ncos_path / "utils/strategy_loader.py"
        with open(loader_path, 'w') as f:
            f.write(strategy_loader)
        
        self.fixes_applied.append("strategy_loader")
        print("  ✅ Created dynamic strategy loader")
    
    def update_master_orchestrator(self):
        """Fix 8: Update master orchestrator with strategy loading"""
        print("\\nUpdating master orchestrator...")
        
        orchestrator_path = self.ncos_path / "agents/master_orchestrator.py"
        
        if orchestrator_path.exists():
            with open(orchestrator_path, 'r') as f:
                content = f.read()
            
            # Add strategy loader import if not present
            if 'StrategyLoader' not in content:
                import_line = "from utils.strategy_loader import StrategyLoader\\n"
                content = content.replace(
                    "import asyncio",
                    "import asyncio\\n" + import_line
                )
                
                # Add strategy loader initialization
                init_addition = """
        # Initialize strategy loader
        self.strategy_loader = StrategyLoader()
        self.active_strategies = {}
"""
                content = content.replace(
                    "self.agents = {}",
                    "self.agents = {}" + init_addition
                )
            
            with open(orchestrator_path, 'w') as f:
                f.write(content)
        
        self.fixes_applied.append("master_orchestrator")
        print("  ✅ Updated master orchestrator with strategy loading")
    
    def create_integration_tests(self):
        """Fix 9: Create comprehensive integration tests"""
        print("\\nCreating integration tests...")
        
        test_path = self.ncos_path / "tests/test_complete_integration.py"
        test_path.parent.mkdir(exist_ok=True)
        
        with open(test_path, 'w') as f:
            f.write(INTEGRATION_TEST_CODE)
        
        self.fixes_applied.append("integration_tests")
        print("  ✅ Created comprehensive integration tests")
    
    def update_documentation(self):
        """Fix 10: Update documentation"""
        print("\\nUpdating documentation...")
        
        # Create comprehensive setup guide
        setup_guide = """# ncOS v21.7 Complete Setup Guide

## Prerequisites
- Python 3.8+
- Required packages: See requirements.txt

## Configuration

### 1. Predictive Engine Configuration
The predictive engine configuration is now complete with all sections:
- Journaling configuration for trade evaluation logging
- Data enrichment with market regime and volatility enrichers
- Feature extraction with configurable window sizes
- Risk integration with grade-based multipliers
- Backtesting configuration

### 2. Strategy Management
Strategies can now be dynamically loaded from the strategies/ directory.
Each strategy should have:
- A Python file (e.g., `my_strategy.py`)
- A configuration file (e.g., `my_strategy_config.yaml`)
- A class ending with 'Strategy'

### 3. Error Handling
Standardized error handling is now available:
- Use `@with_error_handling` decorator for automatic retries
- Use `CircuitBreaker` for fault tolerance
- All errors are logged in structured JSON format

### 4. Vector Engine
The enhanced vector engine now supports:
- FAISS-based similarity search
- Pattern detection and clustering
- Persistent storage
- PCA dimensionality reduction

## Running Tests
```bash
# Run all tests
pytest tests/

# Run configuration validation
pytest tests/test_config_validation.py

# Run integration tests
pytest tests/test_complete_integration.py
'''