"""Custom exceptions for the Fibonacci generation and benchmark module."""

from typing import Any, Optional


class FibonacciError(Exception):
    """Base exception class for all Fibonacci module errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class InvalidInputError(FibonacciError, TypeError):
    """Raised when an input value has an invalid data type or cannot be converted to an integer."""
    pass


class NegativeBoundError(FibonacciError, ValueError):
    """Raised when an input sequence bound or index is negative."""
    pass


class RangeBoundError(FibonacciError, ValueError):
    """Raised when range bounds are logically invalid (e.g. start > end)."""
    pass


class AlgorithmNotSupportedError(FibonacciError, ValueError):
    """Raised when an unknown algorithm identifier is specified."""
    pass
