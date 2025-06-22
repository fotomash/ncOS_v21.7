"""
Token Budget Management for NCOS v11.5 Phoenix-Mesh

This module provides functionality for managing the token budget
in the single-session LLM runtime.
"""

import logging
from typing import Optional

from .core import TokenBudget

logger = logging.getLogger(__name__)

class TokenBudgetManager:
    """
    Manages token budget allocation and tracking.

    The token budget manager is responsible for:
    1. Tracking total, used, and available tokens
    2. Allocating tokens for actions
    3. Releasing unused tokens
    4. Providing budget status and warnings
    """

    def __init__(self, total_budget: int, reserve_percentage: float = 0.2):
        """
        Initialize the token budget manager.

        Args:
            total_budget: Total token budget for the session
            reserve_percentage: Percentage of tokens to reserve for system operations
        """
        self.total_budget = total_budget
        self.reserve_percentage = max(0.0, min(1.0, reserve_percentage))
        self.reserved_tokens = int(total_budget * reserve_percentage)
        self.used_tokens = 0
        self.allocated_tokens = 0

        logger.info(f"Token budget initialized: {total_budget} tokens ({self.reserved_tokens} reserved)")

    def get_budget(self) -> TokenBudget:
        """Get the current token budget."""
        return TokenBudget(
            total=self.total_budget,
            used=self.used_tokens,
            reserved=self.reserved_tokens
        )

    @property
    def available_tokens(self) -> int:
        """Get the number of available tokens."""
        return max(0, self.total_budget - self.used_tokens - self.reserved_tokens - self.allocated_tokens)

    @property
    def usage_percentage(self) -> float:
        """Get the token usage percentage."""
        if self.total_budget == 0:
            return 0
        return (self.used_tokens / self.total_budget) * 100

    def can_allocate(self, tokens: int) -> bool:
        """
        Check if the specified number of tokens can be allocated.

        Args:
            tokens: Number of tokens to allocate

        Returns:
            True if the tokens can be allocated, False otherwise
        """
        return tokens <= self.available_tokens

    def allocate(self, tokens: int) -> bool:
        """
        Allocate tokens for an action.

        Args:
            tokens: Number of tokens to allocate

        Returns:
            True if the tokens were allocated, False otherwise
        """
        if not self.can_allocate(tokens):
            logger.warning(f"Cannot allocate {tokens} tokens. Available: {self.available_tokens}")
            return False

        self.allocated_tokens += tokens
        logger.debug(f"Allocated {tokens} tokens. Remaining: {self.available_tokens}")
        return True

    def release(self, tokens: int) -> None:
        """
        Release previously allocated tokens.

        Args:
            tokens: Number of tokens to release
        """
        self.allocated_tokens = max(0, self.allocated_tokens - tokens)
        logger.debug(f"Released {tokens} tokens. Remaining allocated: {self.allocated_tokens}")

    def use(self, tokens: int) -> None:
        """
        Mark tokens as used.

        Args:
            tokens: Number of tokens used
        """
        self.used_tokens += tokens
        self.allocated_tokens = max(0, self.allocated_tokens - tokens)

        # Log warning if usage is high
        if self.is_budget_warning():
            logger.warning(f"Token budget warning: {self.usage_percentage:.1f}% used ({self.used_tokens}/{self.total_budget})")

        # Log critical if usage is very high
        if self.is_budget_critical():
            logger.critical(f"Token budget critical: {self.usage_percentage:.1f}% used ({self.used_tokens}/{self.total_budget})")

        logger.debug(f"Used {tokens} tokens. Total used: {self.used_tokens} ({self.usage_percentage:.1f}%)")

    def is_budget_warning(self) -> bool:
        """Check if the token budget is reaching a warning level."""
        return self.usage_percentage >= 80.0

    def is_budget_critical(self) -> bool:
        """Check if the token budget is at a critical level."""
        return self.usage_percentage >= 95.0

    def reset(self, budget: Optional[TokenBudget] = None) -> None:
        """
        Reset the token budget.

        Args:
            budget: Optional budget to reset to. If None, keeps the total budget but resets usage.
        """
        if budget:
            self.total_budget = budget.total
            self.used_tokens = budget.used
            self.reserved_tokens = budget.reserved
        else:
            self.used_tokens = 0
            self.reserved_tokens = int(self.total_budget * self.reserve_percentage)

        self.allocated_tokens = 0

        logger.info(f"Token budget reset: {self.total_budget} tokens ({self.reserved_tokens} reserved)")
