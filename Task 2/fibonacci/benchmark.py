"""Runtime benchmarking framework for Fibonacci algorithms using Python's timeit."""

from dataclasses import dataclass
import statistics
import timeit
from typing import Any, Callable, Dict, List, Optional

from .core import fibonacci_nth, fibonacci_sequence
from .validator import sanitize_integer


@dataclass(frozen=True)
class BenchmarkMetric:
    """Statistical measurement container for an individual algorithm benchmark.

    Attributes
    ----------
    algorithm_name : str
        Name of the evaluated algorithm.
    input_n : int
        Input bound or sequence index evaluated.
    iterations : int
        Number of loops executed per sample batch.
    repeats : int
        Number of repeat trials.
    mean_seconds : float
        Average execution time per call in seconds.
    min_seconds : float
        Fastest recorded execution time per call in seconds.
    max_seconds : float
        Slowest recorded execution time per call in seconds.
    stdev_seconds : float
        Standard deviation across trials in seconds.
    ops_per_second : float
        Calculated operations (calls) executed per second.
    """
    algorithm_name: str
    input_n: int
    iterations: int
    repeats: int
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    stdev_seconds: float
    ops_per_second: float

    def format_summary(self) -> str:
        """Formatted human-readable benchmark summary."""
        return (
            f"[{self.algorithm_name:^18}] n={self.input_n:<6} | "
            f"Mean: {self._format_time(self.mean_seconds):>10} | "
            f"Min: {self._format_time(self.min_seconds):>10} | "
            f"Ops/sec: {self.ops_per_second:>12,.1f}"
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        if seconds < 1e-6:
            return f"{seconds * 1e9:.2f} ns"
        elif seconds < 1e-3:
            return f"{seconds * 1e6:.2f} us"
        elif seconds < 1.0:
            return f"{seconds * 1e3:.2f} ms"
        else:
            return f"{seconds:.4f} s"

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm_name,
            "input_n": self.input_n,
            "iterations": self.iterations,
            "repeats": self.repeats,
            "mean_seconds": self.mean_seconds,
            "min_seconds": self.min_seconds,
            "max_seconds": self.max_seconds,
            "stdev_seconds": self.stdev_seconds,
            "ops_per_second": self.ops_per_second,
            "formatted_mean": self._format_time(self.mean_seconds),
        }


def benchmark_function(
    func: Callable[..., Any],
    *args: Any,
    number: int = 1000,
    repeat: int = 5,
    name: Optional[str] = None,
    **kwargs: Any,
) -> BenchmarkMetric:
    """Benchmarks any callable using Python's standard timeit framework.

    Parameters
    ----------
    func : Callable
        Function to benchmark.
    number : int
        Number of times to run the callable per batch.
    repeat : int
        Number of repeat trials.
    name : str, optional
        Display name for algorithm.

    Returns
    -------
    BenchmarkMetric
        Structured statistical results.
    """
    if name:
        algo_name = name
    elif "method" in kwargs:
        algo_name = f"{getattr(func, '__name__', 'func')}_{kwargs['method']}"
    else:
        algo_name = getattr(func, "__name__", "anonymous_func")
    timer = timeit.Timer(lambda: func(*args, **kwargs))
    
    # Run timeit repeat
    raw_times = timer.repeat(repeat=repeat, number=number)
    # Convert batch times to per-call times
    per_call_times = [t / number for t in raw_times]

    mean_t = statistics.mean(per_call_times)
    min_t = min(per_call_times)
    max_t = max(per_call_times)
    stdev_t = statistics.stdev(per_call_times) if len(per_call_times) > 1 else 0.0
    ops_sec = 1.0 / mean_t if mean_t > 0 else float("inf")

    # Retrieve input n representation if first arg is int
    input_n = args[0] if args and isinstance(args[0], int) else 0

    return BenchmarkMetric(
        algorithm_name=algo_name,
        input_n=input_n,
        iterations=number,
        repeats=repeat,
        mean_seconds=mean_t,
        min_seconds=min_t,
        max_seconds=max_t,
        stdev_seconds=stdev_t,
        ops_per_second=ops_sec,
    )


def compare_algorithms(
    n: int,
    methods: Optional[List[str]] = None,
    number: int = 1000,
    repeat: int = 5,
) -> List[BenchmarkMetric]:
    """Runs comparative benchmarks across Fibonacci calculation methods using timeit.

    Parameters
    ----------
    n : int
        Sequence index bound to test.
    methods : list of str, optional
        Algorithms to include. Default is ['fast_doubling', 'matrix', 'iterative'].
        ('memoized' is supported for n <= 500).
    number : int
        timeit iteration count per batch.
    repeat : int
        timeit repeat count.

    Returns
    -------
    list of BenchmarkMetric
        List of benchmark metric results sorted from fastest to slowest.
    """
    n_clean = sanitize_integer(n, param_name="n", allow_negative=False)

    if methods is None:
        methods = ["fast_doubling", "matrix", "iterative"]
        if n_clean <= 500:
            methods.append("memoized")

    results: List[BenchmarkMetric] = []

    for method in methods:
        try:
            metric = benchmark_function(
                fibonacci_nth,
                n_clean,
                method=method,
                number=number,
                repeat=repeat,
                name=f"Nth-{method}",
            )
            results.append(metric)
        except Exception as err:
            # Handle methods that exceed recursion/range limits gracefully
            pass

    # Also benchmark full sequence generation up to n
    seq_metric = benchmark_function(
        fibonacci_sequence,
        n_clean,
        number=max(10, number // 10),
        repeat=repeat,
        name="Sequence-Bounded",
    )
    results.append(seq_metric)

    # Sort results by mean execution time (fastest first)
    results.sort(key=lambda m: m.mean_seconds)
    return results


def generate_benchmark_report(metrics: List[BenchmarkMetric]) -> str:
    """Produces a formatted ASCII text report summarizing timeit benchmark results."""
    header = "=" * 80 + "\n" + " FIBONACCI ALGORITHMIC EXECUTION RUNTIME BENCHMARK (timeit framework)\n" + "=" * 80
    lines = [header]
    for idx, m in enumerate(metrics, start=1):
        lines.append(f"{idx:>2}. {m.format_summary()}")
    lines.append("=" * 80)
    return "\n".join(lines)
