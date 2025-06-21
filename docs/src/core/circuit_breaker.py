from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable, Optional


class CircuitOpenError(Exception):
    """Raised when an operation is attempted while the circuit is open."""


@dataclass
class CircuitBreakerConfig:
    """Configuration for :class:`CircuitBreaker`."""

    failure_threshold: int = 5
    success_threshold: int = 1
    timeout: timedelta = timedelta(seconds=60)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple asynchronous circuit breaker."""

    def __init__(self, name: str, config: CircuitBreakerConfig) -> None:
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: Optional[datetime] = None

    async def call(self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Execute ``func`` within the circuit breaker."""

        # Transition from OPEN to HALF_OPEN if timeout expired
        if self.state == CircuitState.OPEN:
            if self._opened_at and datetime.now() - self._opened_at >= self.config.timeout:
                self.state = CircuitState.HALF_OPEN
                self._failure_count = 0
                self._success_count = 0
            else:
                raise CircuitOpenError(f"Circuit '{self.name}' is open")

        try:
            result = await func(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise
        else:
            self._record_success()
            return result

    def _record_failure(self) -> None:
        self._failure_count += 1

        if self.state == CircuitState.HALF_OPEN or self.state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self._opened_at = datetime.now()
                self._failure_count = 0
                self._success_count = 0

    def _record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._opened_at = None
        else:
            # Reset failure count on successful call when closed
            self._failure_count = 0


__all__ = ["CircuitBreakerConfig", "CircuitBreaker", "CircuitOpenError"]
