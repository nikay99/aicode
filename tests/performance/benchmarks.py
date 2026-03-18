"""
AICode Performance Benchmarks
Tests execution speed, compilation speed, and memory usage
"""

import time
import gc
import tracemalloc
from typing import Callable, List, Dict, Any, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parser import parse
from src.compiler import BytecodeCompiler
from src.vm import VirtualMachine
from src.interpreter import Interpreter


@dataclass
class BenchmarkResult:
    """Result of a benchmark run"""

    name: str
    duration_ms: float
    memory_kb: float
    iterations: int
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class PerformanceBenchmarks:
    """Performance benchmark suite for AICode"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.baseline_results: Dict[str, BenchmarkResult] = {}

    def _measure_time(self, fn: Callable, iterations: int = 1) -> Tuple[float, Any]:
        """Measure execution time of a function"""
        gc.collect()  # Clean up before measurement
        start = time.perf_counter()
        result = None
        for _ in range(iterations):
            result = fn()
        end = time.perf_counter()
        duration_ms = (end - start) * 1000 / iterations
        return duration_ms, result

    def _measure_memory(self, fn: Callable) -> Tuple[float, Any]:
        """Measure memory usage of a function"""
        gc.collect()
        tracemalloc.start()
        result = fn()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_kb = peak / 1024
        return memory_kb, result

    def _run_code(self, code: str) -> List[str]:
        """Run AICode and return output"""
        # parse() accepts source string directly
        ast = parse(code)
        interpreter = Interpreter()
        return interpreter.interpret(ast)

    def benchmark_recursion_fibonacci(self, n: int = 20) -> BenchmarkResult:
        """Benchmark recursive Fibonacci"""
        code = f"""
fn fib(n)
  if n < 2
    return n
  return fib(n-1) + fib(n-2)

fib({n})
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"fibonacci_recursive_n{n}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=1,
            details={"n": n, "complexity": "O(2^n)"},
        )
        self.results.append(result)
        return result

    def benchmark_recursion_fibonacci_iterative(self, n: int = 1000) -> BenchmarkResult:
        """Benchmark iterative Fibonacci"""
        code = f"""
fn fib_iter(n)
  if n < 2
    return n
  let a = 0
  let b = 1
  let i = 2
  while i < n + 1
    let temp = a + b
    a = b
    b = temp
    i = i + 1
  return b

fib_iter({n})
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=10)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"fibonacci_iterative_n{n}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=10,
            details={"n": n, "complexity": "O(n)"},
        )
        self.results.append(result)
        return result

    def benchmark_list_map(self, size: int = 1000) -> BenchmarkResult:
        """Benchmark map operation on list"""
        code = f"""
fn double(x)
  return x * 2

let big_list = range({size})
map(big_list, double)
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=100)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"list_map_size{size}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=100,
            details={"list_size": size, "operation": "map"},
        )
        self.results.append(result)
        return result

    def benchmark_list_filter(self, size: int = 1000) -> BenchmarkResult:
        """Benchmark filter operation on list"""
        code = f"""
fn is_even(x)
  return x % 2 == 0

let big_list = range({size})
filter(big_list, is_even)
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=100)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"list_filter_size{size}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=100,
            details={"list_size": size, "operation": "filter"},
        )
        self.results.append(result)
        return result

    def benchmark_list_reduce(self, size: int = 1000) -> BenchmarkResult:
        """Benchmark reduce operation on list"""
        code = f"""
fn add(acc, x)
  return acc + x

let big_list = range({size})
reduce(big_list, add, 0)
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=100)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"list_reduce_size{size}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=100,
            details={"list_size": size, "operation": "reduce"},
        )
        self.results.append(result)
        return result

    def benchmark_compilation_speed(self, lines: int = 100) -> BenchmarkResult:
        """Benchmark compilation speed for programs of different sizes"""
        # Generate a program with N lines
        statements = []
        for i in range(lines):
            statements.append(f"let x{i} = {i}")
        statements.append(f"x{lines - 1}")
        code = "\n".join(statements)

        def compile_only():
            ast = parse(code)
            compiler = BytecodeCompiler()
            return compiler.compile_program(ast)

        duration_ms, _ = self._measure_time(compile_only, iterations=10)
        memory_kb, _ = self._measure_memory(compile_only)

        result = BenchmarkResult(
            name=f"compilation_{lines}_lines",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=10,
            details={"lines": lines, "operation": "compile_only"},
        )
        self.results.append(result)
        return result

    def benchmark_full_execution(self, complexity: str = "medium") -> BenchmarkResult:
        """Benchmark full execution pipeline"""
        if complexity == "small":
            code = """
let x = 10
let y = 20
x + y
"""
        elif complexity == "medium":
            code = """
fn factorial(n)
  if n < 2
    return 1
  return n * factorial(n - 1)

factorial(10)
"""
        else:  # large
            code = """
fn sum_list(lst)
  let sum = 0
  for x in lst
    sum = sum + x
  return sum

let numbers = range(100)
sum_list(numbers)
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=50)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"full_execution_{complexity}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=50,
            details={"complexity": complexity},
        )
        self.results.append(result)
        return result

    def benchmark_function_calls(self, depth: int = 100) -> BenchmarkResult:
        """Benchmark deep function call chains"""
        code = f"""
fn recurse(n)
  if n < 1
    return 0
  return 1 + recurse(n - 1)

recurse({depth})
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=100)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"function_calls_depth{depth}",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=100,
            details={"call_depth": depth},
        )
        self.results.append(result)
        return result

    def benchmark_while_loop(self, iterations: int = 10000) -> BenchmarkResult:
        """Benchmark while loop performance"""
        code = f"""
let i = 0
let sum = 0
while i < {iterations}
  sum = sum + i
  i = i + 1
sum
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=10)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"while_loop_{iterations}_iterations",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=10,
            details={"loop_iterations": iterations},
        )
        self.results.append(result)
        return result

    def benchmark_for_loop(self, size: int = 1000) -> BenchmarkResult:
        """Benchmark for loop performance"""
        code = f"""
let sum = 0
for x in range({size})
  sum = sum + x
sum
"""

        def run():
            return self._run_code(code)

        duration_ms, _ = self._measure_time(run, iterations=10)
        memory_kb, _ = self._measure_memory(run)

        result = BenchmarkResult(
            name=f"for_loop_{size}_iterations",
            duration_ms=duration_ms,
            memory_kb=memory_kb,
            iterations=10,
            details={"loop_iterations": size},
        )
        self.results.append(result)
        return result

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks"""
        print("Running AICode Performance Benchmarks...")
        print("=" * 60)

        # Recursion benchmarks
        print("\n1. Recursion Performance")
        self.benchmark_recursion_fibonacci(n=10)
        self.benchmark_recursion_fibonacci(n=15)
        self.benchmark_recursion_fibonacci(n=20)
        self.benchmark_recursion_fibonacci_iterative(n=1000)

        # List operation benchmarks
        print("2. List Operations")
        self.benchmark_list_map(size=100)
        self.benchmark_list_map(size=1000)
        self.benchmark_list_filter(size=1000)
        self.benchmark_list_reduce(size=1000)

        # Compilation speed
        print("3. Compilation Speed")
        self.benchmark_compilation_speed(lines=100)
        self.benchmark_compilation_speed(lines=500)
        self.benchmark_compilation_speed(lines=1000)

        # Full execution
        print("4. Full Execution Pipeline")
        self.benchmark_full_execution(complexity="small")
        self.benchmark_full_execution(complexity="medium")
        self.benchmark_full_execution(complexity="large")

        # Function calls
        print("5. Function Call Performance")
        self.benchmark_function_calls(depth=100)
        self.benchmark_function_calls(depth=500)

        # Loops
        print("6. Loop Performance")
        self.benchmark_while_loop(iterations=1000)
        self.benchmark_while_loop(iterations=10000)
        self.benchmark_for_loop(size=100)
        self.benchmark_for_loop(size=1000)

        return self.results

    def print_results(self):
        """Print benchmark results in a formatted table"""
        print("\n" + "=" * 100)
        print("BENCHMARK RESULTS")
        print("=" * 100)
        print(f"{'Benchmark':<40} {'Time (ms)':<15} {'Memory (KB)':<15} {'Status':<15}")
        print("-" * 100)

        for result in self.results:
            # Determine status based on thresholds
            status = "✓ OK"
            if result.duration_ms > 1000:
                status = "⚠ SLOW"
            if result.duration_ms > 5000:
                status = "✗ TOO SLOW"

            print(
                f"{result.name:<40} {result.duration_ms:>10.2f} ms  {result.memory_kb:>10.2f} KB  {status:<15}"
            )

        print("=" * 100)

    def save_baseline(self, filename: str = "baseline.json"):
        """Save current results as baseline"""
        import json

        data = {
            r.name: {
                "duration_ms": r.duration_ms,
                "memory_kb": r.memory_kb,
                "iterations": r.iterations,
                "details": r.details,
            }
            for r in self.results
        }
        filepath = Path(__file__).parent / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nBaseline saved to {filepath}")

    def load_baseline(self, filename: str = "baseline.json") -> bool:
        """Load baseline results"""
        import json

        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            return False

        with open(filepath, "r") as f:
            data = json.load(f)

        self.baseline_results = {
            name: BenchmarkResult(
                name=name,
                duration_ms=info["duration_ms"],
                memory_kb=info["memory_kb"],
                iterations=info["iterations"],
                details=info.get("details", {}),
            )
            for name, info in data.items()
        }
        return True

    def compare_with_baseline(self):
        """Compare current results with baseline"""
        if not self.baseline_results:
            print("\nNo baseline found. Run save_baseline() first.")
            return

        print("\n" + "=" * 100)
        print("PERFORMANCE COMPARISON WITH BASELINE")
        print("=" * 100)
        print(f"{'Benchmark':<40} {'Current':<12} {'Baseline':<12} {'Change':<15}")
        print("-" * 100)

        for result in self.results:
            if result.name in self.baseline_results:
                baseline = self.baseline_results[result.name]
                change_pct = (
                    (result.duration_ms - baseline.duration_ms) / baseline.duration_ms
                ) * 100

                if change_pct < -5:
                    change_str = f"↓ {abs(change_pct):.1f}% FASTER"
                elif change_pct > 5:
                    change_str = f"↑ {change_pct:.1f}% SLOWER"
                else:
                    change_str = "~ SAME"

                print(
                    f"{result.name:<40} {result.duration_ms:>10.2f}  {baseline.duration_ms:>10.2f}  {change_str:<15}"
                )
            else:
                print(
                    f"{result.name:<40} {result.duration_ms:>10.2f}  {'N/A':>10}  {'NEW':<15}"
                )

        print("=" * 100)


def run_benchmarks():
    """Main entry point for running benchmarks"""
    benchmarks = PerformanceBenchmarks()
    benchmarks.run_all_benchmarks()
    benchmarks.print_results()

    # Try to load and compare with baseline
    if benchmarks.load_baseline():
        benchmarks.compare_with_baseline()

    return benchmarks


if __name__ == "__main__":
    benchmarks = run_benchmarks()
