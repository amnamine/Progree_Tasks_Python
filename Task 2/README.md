# Fibonacci Core Algorithmic Engine & Benchmarking Suite

An enterprise-grade Python module for calculating exact Fibonacci sequence values under arbitrary parameter limits, complete with input sanitization handlers, `timeit` execution runtime benchmarks, unit test suites, and a modern Tkinter desktop application.

---

## 🌟 Key Features

1. **High-Performance Core Algorithms**:
   - **Fast Doubling ($O(\log n)$)**: Arbitrarily large exact integer computation via matrix reduction identities.
   - **Matrix Exponentiation ($O(\log n)$)**: $2 \times 2$ logarithmic matrix power generation $\begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}^n$.
   - **Linear Iterative ($O(n)$)**: Optimal cache-friendly forward sequence generator.
   - **Memoized Dynamic Programming**: Cached recursion for analytical workflows.
   - **Infinite Generator Stream ($O(1)$ memory)**: Lazy evaluation for unbounded pipelines.

2. **Input Sanitization & Parameter Validation**:
   - Explicit negative bound verification raising `NegativeBoundError`.
   - Strict type sanitization handling whitespace, commas, and strings while rejecting floats, `None`, and booleans via `InvalidInputError`.
   - Range consistency verification ($start \le end$) via `RangeBoundError`.

3. **`timeit` Performance Benchmarking Framework**:
   - Statistical evaluation including **Mean**, **Min (best)**, **Max**, **Standard Deviation**, and **Operations/sec (Throughput)**.
   - Comparative multi-algorithm benchmarking and ASCII report formatting.

4. **Modern Tkinter Desktop Application**:
   - Dark glassmorphism color palette with emerald/cyan/indigo glowing accents.
   - Multi-tab navigation (Sequence Generator, Nth Big-Int Calculator, Benchmark Lab, Spiral Visualizer).
   - Live Canvas rendering of the Fibonacci Golden Spiral and Golden Ratio convergence ($\lim_{n \to \infty} \frac{F_n}{F_{n-1}} = \varphi \approx 1.6180339887$).
   - Interactive data tables, one-click clipboard copying, and JSON/CSV/TXT export.

---

## 🚀 Quickstart & Usage

### 1. Python API

```python
from fibonacci import (
    fibonacci_sequence,
    fibonacci_nth,
    fibonacci_range,
    compare_algorithms,
    generate_benchmark_report,
)

# 1. Generate structured sequence list for bounds
seq = fibonacci_sequence(count_or_end=15, start_bound=0)
print("Sequence F(0)..F(15):", seq)

# 2. Compute exact nth Fibonacci number in O(log n)
f_1000 = fibonacci_nth(1000, method="fast_doubling")
print("F(1000) digits count:", len(str(f_1000)))

# 3. Run timeit benchmarking suite
metrics = compare_algorithms(n=200, number=1000, repeat=5)
print(generate_benchmark_report(metrics))
```

### 2. Command Line Interface (CLI)

```bash
# Run CLI demo & benchmarks
python main.py --cli

# Generate sequence up to N=20
python main.py --seq 20

# Calculate exact F(500)
python main.py --nth 500

# Benchmark algorithms for N=250
python main.py --benchmark 250
```

### 3. Launch Desktop GUI Application

```bash
python main.py
```

---

## 🧪 Running the Test Suite

Run the full automated test suite with verbose output:

```bash
python -m unittest discover tests -v
```

---

## 📐 Complexity Analysis

| Algorithm | Time Complexity | Auxiliary Space | Best Suited For |
|---|---|---|---|
| **Fast Doubling** | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ recursion stack | Large $N > 1,000$, exact BigInt calculations |
| **Matrix Exponentiation** | $\mathcal{O}(\log n)$ | $\mathcal{O}(1)$ | Single nth term computations |
| **Iterative Sequence** | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ space ($\mathcal{O}(n)$ output list) | Generating full ranges/lists $[0 \dots N]$ |
| **Memoized DP** | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ memoization cache | Small $N \le 500$ exploratory checks |
