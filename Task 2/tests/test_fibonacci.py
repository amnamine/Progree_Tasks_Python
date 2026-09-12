"""Unit and integration tests for core Fibonacci algorithms, sanitization, and edge cases."""

import unittest
from fibonacci import (
    fibonacci_sequence,
    fibonacci_nth,
    fibonacci_range,
    fibonacci_by_max_value,
    fibonacci_stream,
    fibonacci_fast_doubling,
    fibonacci_matrix,
    fibonacci_iterative,
    fibonacci_memoized,
    sanitize_integer,
    validate_range_bounds,
    InvalidInputError,
    NegativeBoundError,
    RangeBoundError,
    AlgorithmNotSupportedError,
)


class TestFibonacciCore(unittest.TestCase):
    """Tests for algorithmic correctness and sequence outputs."""

    # Known first 15 Fibonacci numbers (F0 to F14)
    KNOWN_FIB_15 = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

    def test_fibonacci_sequence_standard(self):
        """Test sequence generation for standard bound limits."""
        res = fibonacci_sequence(14)
        self.assertEqual(res, self.KNOWN_FIB_15)
        self.assertEqual(len(res), 15)

    def test_fibonacci_sequence_zero(self):
        """Test sequence with count/bound = 0."""
        self.assertEqual(fibonacci_sequence(0), [0])

    def test_fibonacci_sequence_one(self):
        """Test sequence with count/bound = 1."""
        self.assertEqual(fibonacci_sequence(1), [0, 1])

    def test_fibonacci_sequence_custom_start_bound(self):
        """Test sequence generation with non-zero start bound."""
        res = fibonacci_sequence(count_or_end=7, start_bound=3)
        # indices 3, 4, 5, 6, 7 => 2, 3, 5, 8, 13
        self.assertEqual(res, [2, 3, 5, 8, 13])

    def test_fibonacci_range(self):
        """Test fibonacci_range dataclass structured output."""
        res = fibonacci_range(start=4, end=8)
        self.assertEqual(res.sequence, [3, 5, 8, 13, 21])
        self.assertEqual(res.start_index, 4)
        self.assertEqual(res.end_index, 8)
        self.assertEqual(res.count, 5)
        self.assertGreaterEqual(res.execution_time_seconds, 0.0)

    def test_fibonacci_by_max_value(self):
        """Test bounded generation by maximum numerical value."""
        res = fibonacci_by_max_value(55)
        self.assertEqual(res, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
        
        res_small = fibonacci_by_max_value(0)
        self.assertEqual(res_small, [0])

    def test_fibonacci_stream(self):
        """Test infinite generator output."""
        gen = fibonacci_stream()
        stream_out = [next(gen) for _ in range(10)]
        self.assertEqual(stream_out, self.KNOWN_FIB_15[:10])

    def test_nth_algorithmic_parity(self):
        """Ensure all nth calculation algorithms produce identical exact values."""
        test_indices = [0, 1, 2, 3, 7, 14, 25, 50, 100]
        for idx in test_indices:
            fast_val = fibonacci_fast_doubling(idx)
            matrix_val = fibonacci_matrix(idx)
            iter_val = fibonacci_iterative(idx)
            memo_val = fibonacci_memoized(idx)

            self.assertEqual(fast_val, iter_val, f"Mismatch at n={idx}")
            self.assertEqual(matrix_val, iter_val, f"Mismatch at n={idx}")
            self.assertEqual(memo_val, iter_val, f"Mismatch at n={idx}")

    def test_large_nth_computation(self):
        """Test big integer computation with Fast Doubling for n=1000."""
        val = fibonacci_nth(1000, method="fast_doubling")
        self.assertIsInstance(val, int)
        # F(1000) has 209 digits
        self.assertEqual(len(str(val)), 209)


class TestInputSanitizationAndExceptions(unittest.TestCase):
    """Tests for input sanitization, negative bounds, and exception handlers."""

    def test_negative_bound_rejection(self):
        """Negative bounds must raise NegativeBoundError."""
        with self.assertRaises(NegativeBoundError):
            fibonacci_sequence(-5)

        with self.assertRaises(NegativeBoundError):
            fibonacci_nth(-1)

        with self.assertRaises(NegativeBoundError):
            fibonacci_range(start=-2, end=10)

        with self.assertRaises(NegativeBoundError):
            fibonacci_by_max_value(-10)

    def test_invalid_type_rejection(self):
        """Invalid types (float, None, bool, non-numeric strings) must raise InvalidInputError."""
        with self.assertRaises(InvalidInputError):
            fibonacci_sequence(3.14)

        with self.assertRaises(InvalidInputError):
            fibonacci_sequence(None)

        with self.assertRaises(InvalidInputError):
            fibonacci_sequence(True)  # Booleans rejected

        with self.assertRaises(InvalidInputError):
            fibonacci_sequence("invalid_string")

    def test_valid_string_sanitization(self):
        """Formatted string inputs (e.g. '10', ' 100 ', '1,000') should be safely sanitized."""
        self.assertEqual(sanitize_integer(" 10 "), 10)
        self.assertEqual(sanitize_integer("1_000"), 1000)
        self.assertEqual(sanitize_integer("1,000"), 1000)
        self.assertEqual(len(fibonacci_sequence("10")), 11)

    def test_range_bound_order_violation(self):
        """Range where start > end must raise RangeBoundError."""
        with self.assertRaises(RangeBoundError):
            validate_range_bounds(start=10, end=5)

        with self.assertRaises(RangeBoundError):
            fibonacci_range(start=20, end=10)

    def test_unsupported_algorithm_rejection(self):
        """Invalid method strings must raise AlgorithmNotSupportedError."""
        with self.assertRaises(AlgorithmNotSupportedError):
            fibonacci_nth(10, method="quantum_teleportation")


if __name__ == "__main__":
    unittest.main()
