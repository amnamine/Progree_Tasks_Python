"""Fibonacci sequence generation, input sanitization, and benchmarking package."""

from .benchmark import (
    BenchmarkMetric,
    benchmark_function,
    compare_algorithms,
    generate_benchmark_report,
)
from .core import (
    FibonacciResult,
    fibonacci_by_max_value,
    fibonacci_fast_doubling,
    fibonacci_iterative,
    fibonacci_matrix,
    fibonacci_memoized,
    fibonacci_nth,
    fibonacci_range,
    fibonacci_sequence,
    fibonacci_stream,
)
from .exceptions import (
    AlgorithmNotSupportedError,
    FibonacciError,
    InvalidInputError,
    NegativeBoundError,
    RangeBoundError,
)
from .validator import sanitize_integer, validate_range_bounds

__all__ = [
    # Core Functions
    "fibonacci_sequence",
    "fibonacci_nth",
    "fibonacci_range",
    "fibonacci_by_max_value",
    "fibonacci_stream",
    "fibonacci_fast_doubling",
    "fibonacci_matrix",
    "fibonacci_iterative",
    "fibonacci_memoized",
    "FibonacciResult",
    # Validation & Exceptions
    "sanitize_integer",
    "validate_range_bounds",
    "FibonacciError",
    "InvalidInputError",
    "NegativeBoundError",
    "RangeBoundError",
    "AlgorithmNotSupportedError",
    # Benchmarking
    "benchmark_function",
    "compare_algorithms",
    "generate_benchmark_report",
    "BenchmarkMetric",
]

__version__ = "2.0.0"
