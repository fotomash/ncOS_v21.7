"""
Standardized Error Handling and Logging Framework for ncOS
"""

import logging
import json
import traceback
import functools
from datetime import datetime
from typing import Any, Callable, Optional, Dict, Type
from enum import Enum
import os

# Configure structured logging
class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_obj.update(record.extra_fields)
            
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        return json.dumps(log_obj)

class ErrorCategory(str, Enum):
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    RUNTIME = "runtime"
    RESOURCE = "resource"
    NETWORK = "network"
    SECURITY = "security"

class NCOSError(Exception):
    """Base exception class for ncOS"""
    def __init__(self, message: str, category: ErrorCategory, details: Optional[Dict] = None):
        super().__init__(message)
        self.category = category
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class ConfigurationError(NCOSError):
    """Raised when configuration is invalid"""
    def __init__(self, message: str, config_key: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, details)
        self.config_key = config_key

class ValidationError(NCOSError):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str, value: Any, details: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.VALIDATION, details)
        self.field = field
        self.value = value

class ResourceError(NCOSError):
    """Raised when resource limits are exceeded"""
    def __init__(self, message: str, resource_type: str, limit: Any, current: Any, details: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.RESOURCE, details)
        self.resource_type = resource_type
        self.limit = limit
        self.current = current

def setup_logging(component_name: str, log_level: str = "INFO") -> logging.Logger:
    """Set up structured logging for a component"""
    logger = logging.getLogger(component_name)
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler with structured output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = "/var/log/ncOS"
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(f"{log_dir}/{component_name}.json")
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    return logger

def with_error_handling(
    component: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    propagate: bool = True
) -> Callable:
    """Decorator for standardized error handling with retries"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logging(component)
            attempt = 0
            last_error = None
            
            while attempt < max_retries:
                try:
                    # Log function call
                    logger.info(
                        f"Calling {func.__name__}",
                        extra={'extra_fields': {
                            'attempt': attempt + 1,
                            'max_retries': max_retries,
                            'args_count': len(args),
                            'kwargs_keys': list(kwargs.keys())
                        }}
                    )
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Log successful completion
                    logger.info(
                        f"Successfully completed {func.__name__}",
                        extra={'extra_fields': {'attempt': attempt + 1}}
                    )
                    
                    return result
                    
                except NCOSError as e:
                    last_error = e
                    logger.error(
                        f"ncOS error in {func.__name__}: {str(e)}",
                        extra={'extra_fields': {
                            'error_category': e.category.value,
                            'error_details': e.details,
                            'attempt': attempt + 1
                        }},
                        exc_info=True
                    )
                    
                except Exception as e:
                    last_error = e
                    logger.error(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        extra={'extra_fields': {
                            'error_type': type(e).__name__,
                            'attempt': attempt + 1
                        }},
                        exc_info=True
                    )
                
                attempt += 1
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay * attempt)  # Exponential backoff
            
            # All retries exhausted
            logger.critical(
                f"All retries exhausted for {func.__name__}",
                extra={'extra_fields': {
                    'total_attempts': attempt,
                    'last_error': str(last_error)
                }}
            )
            
            if propagate and last_error:
                raise last_error
            
            return None
            
        return wrapper
    return decorator

def log_performance(component: str) -> Callable:
    """Decorator to log function performance metrics"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logging(component)
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(
                    f"Performance metrics for {func.__name__}",
                    extra={'extra_fields': {
                        'duration_seconds': duration,
                        'status': 'success'
                    }}
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error(
                    f"Performance metrics for {func.__name__} (failed)",
                    extra={'extra_fields': {
                        'duration_seconds': duration,
                        'status': 'failed',
                        'error': str(e)
                    }}
                )
                
                raise
                
        return wrapper
    return decorator

# Example usage functions

@with_error_handling(component="predictive_engine", max_retries=3)
@log_performance(component="predictive_engine")
def process_prediction(data: Dict) -> Dict:
    """Example function showing error handling usage"""
    if not data:
        raise ValidationError(
            "Input data cannot be empty",
            field="data",
            value=data
        )
    
    # Processing logic here
    return {"status": "processed", "data": data}

class ErrorAggregator:
    """Aggregates errors for batch operations"""
    def __init__(self, component: str):
        self.component = component
        self.errors = []
        self.logger = setup_logging(component)
        
    def add_error(self, error: Exception, context: Dict):
        """Add an error to the aggregator"""
        self.errors.append({
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(error),
            'type': type(error).__name__,
            'context': context
        })
        
    def log_summary(self):
        """Log a summary of all collected errors"""
        if self.errors:
            self.logger.error(
                f"Error summary for {self.component}",
                extra={'extra_fields': {
                    'error_count': len(self.errors),
                    'errors': self.errors
                }}
            )
            
    def raise_if_errors(self):
        """Raise an exception if any errors were collected"""
        if self.errors:
            raise NCOSError(
                f"Batch operation failed with {len(self.errors)} errors",
                ErrorCategory.RUNTIME,
                {'errors': self.errors}
            )
