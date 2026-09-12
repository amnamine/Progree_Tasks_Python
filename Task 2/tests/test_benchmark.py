"""Unit tests for timeit benchmarking framework and statistical reporting."""

import unittest
from fibonacci import (
    benchmark_function,
    compare_algorithms,
    generate_benchmark_report,
    fibonacci_nth,
    BenchmarkMetric,
)


class TestBenchmarkFramework(unittest.TestCase):
    """Tests for benchmarking execution and statistics."""

    def test_benchmark_function_execution(self):
        """Test timeit benchmark execution returns valid metrics."""
        metric = benchmark_function(fibonacci_nth, 50, method="fast_doubling", number=50, repeat=3)
        self.assertIsInstance(metric, BenchmarkMetric)
        self.assertEqual(metric.input_n, 50)
        self.assertGreater(metric.mean_seconds, 0.0)
        self.assertGreater(metric.min_seconds, 0.0)
        self.assertGreater(metric.max_seconds, 0.0)
        self.assertGreaterEqual(metric.max_seconds, metric.min_seconds)
        self.assertGreater(metric.ops_per_second, 0.0)
        
        # Test string formatting
        summary = metric.format_summary()
        self.assertIn("fast_doubling", summary)
        self.assertIn("Ops/sec", summary)

    def test_compare_algorithms(self):
        """Test comparative benchmark runs across multiple algorithms."""
        metrics = compare_algorithms(n=25, number=20, repeat=3)
        self.assertGreaterEqual(len(metrics), 3)
        
        # Verify all metrics have valid positive runtimes
        for m in metrics:
            self.assertGreater(m.mean_seconds, 0.0)
            self.assertGreater(m.ops_per_second, 0.0)

    def test_benchmark_report_generation(self):
        """Test report generation returns readable ASCII text with header."""
        metrics = compare_algorithms(n=20, number=10, repeat=2)
        report = generate_benchmark_report(metrics)
        self.assertIn("FIBONACCI ALGORITHMIC EXECUTION RUNTIME BENCHMARK", report)
        self.assertIn("Ops/sec", report)


if __name__ == "__main__":
    unittest.main()
