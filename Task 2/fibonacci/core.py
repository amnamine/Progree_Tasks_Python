"""Core algorithmic Fibonacci sequence generation module.

Provides multiple high-performance mathematical implementations:
- Fast Doubling (O(log n))
- Matrix Exponentiation (O(log n))
- Linear Iterative (O(n))
- Memoized Dynamic Programming
- Generator Streaming (O(1) memory)
"""

from dataclasses import dataclass
import functools
import time
from typing import Any, Generator, List, Literal, Tuple

from .exceptions import AlgorithmNotSupportedError
from .validator import sanitize_integer, validate_range_bounds


@dataclass(frozen=True)
class FibonacciResult:
    """Structured container for Fibonacci sequence calculation results.

    Attributes
    ----------
    sequence : List[int]
        List of generated Fibonacci numbers.
    start_index : int
        Starting index of the sequence (0-indexed).
    end_index : int
        Ending index of the sequence (inclusive).
    count : int
        Total number of elements generated.
    algorithm : str
        Algorithm name used for calculation.
    execution_time_seconds : float
        Wall-clock time taken to compute sequence in seconds.
    """
    sequence: List[int]
    start_index: int
    end_index: int
    count: int
    algorithm: str
    execution_time_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Convert result to a serializable dictionary."""
        return {
            "sequence": self.sequence,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "count": self.count,
            "algorithm": self.algorithm,
            "execution_time_seconds": self.execution_time_seconds,
        }


# =====================================================================
# Core Mathematical Algorithms for Nth Fibonacci Number (0-indexed: F0=0, F1=1)
# =====================================================================

def _fib_fast_doubling(n: int) -> Tuple[int, int]:
    """Computes (F(n), F(n+1)) using the Fast Doubling identities in O(log n).

    Identities:
        F(2k)   = F(k) * [2*F(k+1) - F(k)]
        F(2k+1) = F(k)^2 + F(k+1)^2
    """
    if n == 0:
        return (0, 1)
    a, b = _fib_fast_doubling(n >> 1)
    c = a * ((b << 1) - a)
    d = a * a + b * b
    if n & 1:
        return (d, c + d)
    return (c, d)


def fibonacci_fast_doubling(n: int) -> int:
    """Calculates F(n) using Fast Doubling in O(log n) time.

    Parameters
    ----------
    n : int
        The sequence index (non-negative integer).

    Returns
    -------
    int
        The exact nth Fibonacci number.
    """
    n = sanitize_integer(n, param_name="n", allow_negative=False)
    return _fib_fast_doubling(n)[0]


def _matrix_multiply_2x2(
    a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]
) -> Tuple[int, int, int, int]:
    """Multiplies two 2x2 integer matrices represented as 4-tuples."""
    a00, a01, a10, a11 = a
    b00, b01, b10, b11 = b
    return (
        a00 * b00 + a01 * b10,
        a00 * b01 + a01 * b11,
        a10 * b00 + a11 * b10,
        a10 * b01 + a11 * b11,
    )


def _matrix_power_2x2(
    matrix: Tuple[int, int, int, int], power: int
) -> Tuple[int, int, int, int]:
    """Computes matrix^power using binary exponentiation in O(log power)."""
    result = (1, 0, 0, 1)  # Identity matrix
    base = matrix
    while power > 0:
        if power & 1:
            result = _matrix_multiply_2x2(result, base)
        base = _matrix_multiply_2x2(base, base)
        power >>= 1
    return result


def fibonacci_matrix(n: int) -> int:
    """Calculates F(n) using 2x2 matrix exponentiation [[1, 1], [1, 0]]^n.

    Parameters
    ----------
    n : int
        The sequence index (non-negative integer).

    Returns
    -------
    int
        The exact nth Fibonacci number.
    """
    n = sanitize_integer(n, param_name="n", allow_negative=False)
    if n == 0:
        return 0
    q = (1, 1, 1, 0)
    res = _matrix_power_2x2(q, n - 1)
    return res[0]


def fibonacci_iterative(n: int) -> int:
    """Calculates F(n) using linear iterative accumulation in O(n) time.

    Parameters
    ----------
    n : int
        The sequence index (non-negative integer).

    Returns
    -------
    int
        The exact nth Fibonacci number.
    """
    n = sanitize_integer(n, param_name="n", allow_negative=False)
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


@functools.lru_cache(maxsize=10000)
def _fib_memoized_helper(n: int) -> int:
    """Internal recursive memoized helper."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    return _fib_memoized_helper(n - 1) + _fib_memoized_helper(n - 2)


def fibonacci_memoized(n: int) -> int:
    """Calculates F(n) using memoized recursion.

    Parameters
    ----------
    n : int
        The sequence index (non-negative integer, n <= 1000 to avoid recursion depth limit).

    Returns
    -------
    int
        The exact nth Fibonacci number.
    """
    n = sanitize_integer(n, param_name="n", allow_negative=False, max_value=2000)
    # Recursively fill cache iteratively to avoid Python RecursionError on large n
    for i in range(n + 1):
        _fib_memoized_helper(i)
    return _fib_memoized_helper(n)


def fibonacci_nth(
    n: Any,
    method: Literal["fast_doubling", "matrix", "iterative", "memoized"] = "fast_doubling",
) -> int:
    """Universal dispatcher for calculating the nth Fibonacci number.

    Parameters
    ----------
    n : Any
        The target sequence index (0-indexed).
    method : str
        Algorithm to use: 'fast_doubling', 'matrix', 'iterative', or 'memoized'.

    Returns
    -------
    int
        Exact nth Fibonacci number.
    """
    sanitized_n = sanitize_integer(n, param_name="n", allow_negative=False)
    method_normalized = method.lower().strip()

    if method_normalized == "fast_doubling":
        return fibonacci_fast_doubling(sanitized_n)
    elif method_normalized == "matrix":
        return fibonacci_matrix(sanitized_n)
    elif method_normalized == "iterative":
        return fibonacci_iterative(sanitized_n)
    elif method_normalized == "memoized":
        return fibonacci_memoized(sanitized_n)
    else:
        raise AlgorithmNotSupportedError(
            f"Unsupported algorithm '{method}'. Available: 'fast_doubling', 'matrix', 'iterative', 'memoized'.",
            details={"requested_method": method},
        )


# =====================================================================
# Sequence Generation Processing Integer Bounds
# =====================================================================

def fibonacci_stream() -> Generator[int, None, None]:
    """Generates an infinite stream of Fibonacci numbers: F(0), F(1), F(2), ...

    Yields
    ------
    int
        Next Fibonacci number in sequence.
    """
    a, b = 0, 1
    yield a
    yield b
    while True:
        a, b = b, a + b
        yield b


def fibonacci_sequence(
    count_or_end: Any,
    start_bound: Any = 0,
    method: str = "iterative",
) -> List[int]:
    """Generates a structured list array of Fibonacci numbers within specified bounds.

    Parameters
    ----------
    count_or_end : Any
        Upper index limit (inclusive if start_bound is provided as range start, or total count - 1).
    start_bound : Any, optional
        Starting sequence index (0-indexed, defaults to 0).
    method : str, optional
        Method identifier ('iterative', 'fast_doubling', etc.). Defaults to 'iterative'.

    Returns
    -------
    list of int
        Structured list array containing exact sequence values [F(start), ..., F(end)].

    Raises
    ------
    InvalidInputError
        If bounds cannot be parsed as integers.
    NegativeBoundError
        If any bound is negative.
    RangeBoundError
        If start_bound > count_or_end.
    """
    start, end = validate_range_bounds(start_bound, count_or_end)

    # Optimized generation for range
    results: List[int] = []

    if end == 0:
        return [0]

    # If small start, linear generation is fastest and most memory efficient
    a, b = 0, 1
    idx = 0

    if start == 0:
        results.append(0)

    if end >= 1:
        if start <= 1:
            results.append(1)
        
        idx = 1
        while idx < end:
            a, b = b, a + b
            idx += 1
            if idx >= start:
                results.append(b)

    return results


def fibonacci_range(
    start: Any,
    end: Any,
    method: str = "iterative",
) -> FibonacciResult:
    """Calculates Fibonacci numbers within an inclusive index range with full metadata.

    Parameters
    ----------
    start : Any
        Starting index (0-indexed, non-negative).
    end : Any
        Ending index (inclusive, non-negative, >= start).
    method : str
        Algorithm name used for calculation.

    Returns
    -------
    FibonacciResult
        Structured dataclass containing sequence array and benchmark/index metadata.
    """
    start_clean, end_clean = validate_range_bounds(start, end)
    start_time = time.perf_counter()
    seq = fibonacci_sequence(end_clean, start_bound=start_clean, method=method)
    duration = time.perf_counter() - start_time

    return FibonacciResult(
        sequence=seq,
        start_index=start_clean,
        end_index=end_clean,
        count=len(seq),
        algorithm=method,
        execution_time_seconds=duration,
    )


def fibonacci_by_max_value(max_value: Any) -> List[int]:
    """Generates all Fibonacci numbers less than or equal to a maximum value limit.

    Parameters
    ----------
    max_value : Any
        Maximum ceiling value for numbers in the sequence.

    Returns
    -------
    list of int
        Structured list array of Fibonacci numbers <= max_value.
    """
    ceiling = sanitize_integer(max_value, param_name="max_value", allow_negative=False)
    if ceiling == 0:
        return [0]
    
    seq = [0, 1]
    a, b = 0, 1
    while True:
        c = a + b
        if c > ceiling:
            break
        seq.append(c)
        a, b = b, c
        
    return seq
