"""
AICode Performance Testing Suite

This package contains performance benchmarks and optimization tests.

Usage:
    from tests.performance.benchmarks import PerformanceBenchmarks

    benchmarks = PerformanceBenchmarks()
    benchmarks.run_all_benchmarks()
    benchmarks.print_results()
"""

from .benchmarks import (
    PerformanceBenchmarks,
    BenchmarkResult,
    run_benchmarks,
)

__all__ = [
    "PerformanceBenchmarks",
    "BenchmarkResult",
    "run_benchmarks",
]
