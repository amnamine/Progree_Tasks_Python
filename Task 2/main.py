"""Root entry point for the Fibonacci Algorithmic Suite (CLI & Modern Tkinter GUI)."""

import argparse
import sys
from fibonacci import (
    compare_algorithms,
    fibonacci_nth,
    fibonacci_sequence,
    generate_benchmark_report,
    sanitize_integer,
)


def run_cli_demo() -> None:
    """Executes a command-line demonstration and timeit runtime benchmarks."""
    print("=" * 80)
    print("  FIBONACCI CORE ALGORITHMIC ENGINE - CLI BENCHMARK & DEMO")
    print("=" * 80)

    # 1. Sequence Generation
    print("\n[1] Generating Fibonacci Sequence for N=15 (0 to 15):")
    seq_15 = fibonacci_sequence(15)
    print(f"    Result ({len(seq_15)} terms): {seq_15}")

    # 2. Bounded range
    print("\n[2] Generating Bounded Range [F(10) ... F(20)]:")
    seq_range = fibonacci_sequence(20, start_bound=10)
    print(f"    Result ({len(seq_range)} terms): {seq_range}")

    # 3. Exact Big Int Calculation
    print("\n[3] Calculating Exact F(500) using Fast Doubling O(log n):")
    f_500 = fibonacci_nth(500, method="fast_doubling")
    print(f"    F(500) = {f_500}")
    print(f"    Exact Digits: {len(str(f_500))}")

    # 4. timeit Benchmarks
    print("\n[4] Running timeit Performance Benchmarks (N=100, 1,000 iterations per batch, 5 repeats):")
    metrics = compare_algorithms(n=100, number=1000, repeat=5)
    report = generate_benchmark_report(metrics)
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fibonacci Algorithmic Suite & timeit Benchmarking")
    parser.add_argument("--cli", action="store_true", help="Run in CLI demonstration and benchmark mode")
    parser.add_argument("--seq", type=int, help="Generate sequence up to index N")
    parser.add_argument("--nth", type=int, help="Calculate exact nth Fibonacci number")
    parser.add_argument("--benchmark", type=int, help="Run timeit benchmark for index N")

    args = parser.parse_args()

    if args.seq is not None:
        seq = fibonacci_sequence(args.seq)
        print(f"Fibonacci Sequence [0..{args.seq}]: {seq}")
        return

    if args.nth is not None:
        val = fibonacci_nth(args.nth)
        print(f"F({args.nth}) = {val}")
        return

    if args.benchmark is not None:
        metrics = compare_algorithms(args.benchmark, number=1000, repeat=5)
        print(generate_benchmark_report(metrics))
        return

    if args.cli:
        run_cli_demo()
        return

    # Default to GUI desktop app
    try:
        from gui.app import launch_app
        launch_app()
    except Exception as exc:
        print(f"Failed to launch GUI ({exc}). Falling back to CLI demo:")
        run_cli_demo()


if __name__ == "__main__":
    main()
