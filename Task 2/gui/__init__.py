"""GUI package for modern Fibonacci visualizer and benchmarking desktop application."""

from .app import FibonacciApp, launch_app
from .theme import PALETTE, FONTS
from .visualizer import FibonacciVisualizer

__all__ = ["FibonacciApp", "launch_app", "PALETTE", "FONTS", "FibonacciVisualizer"]
