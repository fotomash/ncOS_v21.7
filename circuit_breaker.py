from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable, Optional


class CircuitOpenError(Exception):
    """Raised when an operation is attempted on an open circuit."""


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: timedelta = timedelta(seconds=60)


class CircuitBreaker:
    """Simple asynchronous circuit breaker implementation."""

    def __init__(self, name: str, config: CircuitBreakerConfig) -> None:
        self.name = name
        self.config = config
        self.state: CircuitState = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._opened_at: Optional[datetime] = None

    async def call(self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Call ``func`` under circuit breaker protection."""
        now = datetime.now()

        if self.state is CircuitState.OPEN:
            if self._opened_at and now - self._opened_at >= self.config.timeout:
                # Move to half-open state
                self.state = CircuitState.HALF_OPEN
                self._failures = 0
                self._successes = 0
            else:
                raise CircuitOpenError(f"Circuit {self.name} is open")

        try:
            result = await func(*args, **kwargs)
        except Exception:
            await self._record_failure()
            raise
        else:
            await self._record_success()
            return result

    async def _record_failure(self) -> None:
        self._failures += 1
        self._successes = 0
        if self.state is CircuitState.HALF_OPEN or self._failures >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self._opened_at = datetime.now()

    async def _record_success(self) -> None:
        if self.state is CircuitState.HALF_OPEN:
            self._successes += 1
            if self._successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self._failures = 0
                self._successes = 0
        else:
            # In closed state just reset failure count
            self._failures = 0
