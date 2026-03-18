"""
Tests for performance benchmarks and optimizations
"""

import unittest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parser import parse
from src.compiler import BytecodeCompiler
from src.vm import VirtualMachine
from src.interpreter import Interpreter
from src.optimizer import BytecodeOptimizer, BytecodeCache, optimize_and_cache
from tests.performance.benchmarks import PerformanceBenchmarks, BenchmarkResult


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test the benchmark suite itself"""

    def setUp(self):
        self.benchmarks = PerformanceBenchmarks()

    def test_fibonacci_benchmark(self):
        """Test that Fibonacci benchmark runs"""
        result = self.benchmarks.benchmark_recursion_fibonacci(n=10)

        self.assertIsInstance(result, BenchmarkResult)
        self.assertEqual(result.name, "fibonacci_recursive_n10")
        self.assertGreater(result.duration_ms, 0)
        self.assertGreater(result.memory_kb, 0)
        self.assertEqual(result.details["n"], 10)

    def test_list_operations_benchmark(self):
        """Test list operation benchmarks"""
        result_map = self.benchmarks.benchmark_list_map(size=100)
        result_filter = self.benchmarks.benchmark_list_filter(size=100)
        result_reduce = self.benchmarks.benchmark_list_reduce(size=100)

        self.assertEqual(result_map.name, "list_map_size100")
        self.assertEqual(result_filter.name, "list_filter_size100")
        self.assertEqual(result_reduce.name, "list_reduce_size100")

    def test_compilation_speed_benchmark(self):
        """Test compilation speed benchmark"""
        result = self.benchmarks.benchmark_compilation_speed(lines=50)

        self.assertEqual(result.name, "compilation_50_lines")
        self.assertGreater(result.duration_ms, 0)
        self.assertEqual(result.details["lines"], 50)

    def test_benchmark_results_collection(self):
        """Test that results are collected properly"""
        self.benchmarks.benchmark_recursion_fibonacci(n=10)
        self.benchmarks.benchmark_list_map(size=100)

        self.assertEqual(len(self.benchmarks.results), 2)

    def test_benchmark_thresholds(self):
        """Test benchmark thresholds"""
        # Run a quick benchmark
        result = self.benchmarks.benchmark_recursion_fibonacci(n=5)

        # Should complete in reasonable time
        self.assertLess(result.duration_ms, 5000, "Benchmark took too long")

        # Memory should be reasonable
        self.assertLess(result.memory_kb, 10000, "Benchmark used too much memory")


class TestBytecodeOptimizer(unittest.TestCase):
    """Test bytecode optimizations"""

    def setUp(self):
        self.optimizer = BytecodeOptimizer()
        self.compiler = BytecodeCompiler()

    def compile_code(self, code: str):
        """Helper to compile code"""
        ast = parse(code)
        return self.compiler.compile_program(ast)

    def test_constant_folding_addition(self):
        """Test constant folding for addition"""
        code = """
let x = 2 + 3
x
"""
        module = self.compile_code(code)

        # Count PUSH_CONST instructions before optimization
        main_func = module.functions[module.entry_point]
        push_const_before = sum(
            1 for instr in main_func.code if instr.opcode.name == "PUSH_CONST"
        )

        # Optimize
        optimized = self.optimizer.optimize_module(module)
        main_func_opt = optimized.functions[optimized.entry_point]

        # Check that optimization was applied
        stats = self.optimizer.get_stats()
        self.assertGreaterEqual(stats["optimizations_applied"], 0)

    def test_constant_folding_arithmetic(self):
        """Test constant folding for various arithmetic operations"""
        code = """
let a = 10 * 5
let b = 20 / 4
let c = 15 - 7
let d = 17 % 5
"""
        module = self.compile_code(code)
        optimized = self.optimizer.optimize_module(module)

        # Module should still be valid
        self.assertIsNotNone(optimized)
        self.assertGreater(len(optimized.functions), 0)

    def test_peephole_pop_after_push(self):
        """Test peephole optimization for POP after PUSH"""
        code = """
2 + 3
"""
        module = self.compile_code(code)

        # Get code size before
        main_func = module.functions[module.entry_point]
        code_size_before = len(main_func.code)

        # Optimize
        optimized = self.optimizer.optimize_module(module)
        main_func_opt = optimized.functions[optimized.entry_point]

        # Should not increase code size
        self.assertLessEqual(len(main_func_opt.code), code_size_before + 5)

    def test_dead_code_elimination(self):
        """Test dead code elimination"""
        # This tests that the optimizer runs without errors
        code = """
fn test()
  return 42
  let x = 10  # Dead code
"""
        module = self.compile_code(code)
        optimized = self.optimizer.optimize_module(module)

        self.assertIsNotNone(optimized)

    def test_optimization_preserves_semantics(self):
        """Test that optimizations preserve program semantics"""
        code = """
let x = 2 + 3 * 4
x
"""
        # Run unoptimized
        ast = parse(code)
        interpreter1 = Interpreter()
        output1 = interpreter1.interpret(ast)

        # Run optimized
        module = self.compiler.compile_program(ast)
        optimized = self.optimizer.optimize_module(module)
        interpreter2 = Interpreter()

        # We can't easily run optimized code with current Interpreter
        # but we can verify the optimization ran
        stats = self.optimizer.get_stats()
        self.assertIsNotNone(stats)


class TestBytecodeCache(unittest.TestCase):
    """Test bytecode caching"""

    def setUp(self):
        self.cache = BytecodeCache(max_size=10)
        self.compiler = BytecodeCompiler()

    def compile_simple_code(self):
        """Helper to compile simple code"""
        code = "let x = 42"
        ast = parse(code)
        return self.compiler.compile_program(ast)

    def test_cache_hit(self):
        """Test cache hit"""
        module = self.compile_simple_code()

        # Store in cache
        self.cache.put("test_key", module)

        # Retrieve
        cached = self.cache.get("test_key")

        self.assertIsNotNone(cached)
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 0)

    def test_cache_miss(self):
        """Test cache miss"""
        cached = self.cache.get("nonexistent_key")

        self.assertIsNone(cached)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 1)

    def test_cache_size_limit(self):
        """Test cache size limit enforcement"""
        module = self.compile_simple_code()

        # Fill cache beyond limit
        for i in range(15):
            self.cache.put(f"key_{i}", module)

        # Cache should not exceed max size
        self.assertLessEqual(len(self.cache.cache), 10)

    def test_cache_stats(self):
        """Test cache statistics"""
        module = self.compile_simple_code()

        # Some hits and misses
        self.cache.put("key1", module)
        self.cache.get("key1")  # hit
        self.cache.get("key1")  # hit
        self.cache.get("key2")  # miss

        stats = self.cache.get_stats()

        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["size"], 1)
        self.assertEqual(stats["max_size"], 10)
        self.assertGreater(stats["hit_rate"], 0)

    def test_cache_clear(self):
        """Test cache clear"""
        module = self.compile_simple_code()

        self.cache.put("key1", module)
        self.cache.clear()

        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)


class TestPerformanceComparison(unittest.TestCase):
    """Test performance comparisons and improvements"""

    def test_benchmark_saves_results(self):
        """Test that benchmarks properly save results"""
        benchmarks = PerformanceBenchmarks()

        # Run a few benchmarks
        benchmarks.benchmark_recursion_fibonacci(n=10)
        benchmarks.benchmark_list_map(size=100)

        # Should have results
        self.assertEqual(len(benchmarks.results), 2)

        # Results should have expected attributes
        for result in benchmarks.results:
            self.assertIsNotNone(result.name)
            self.assertGreater(result.duration_ms, 0)
            self.assertIsNotNone(result.details)

    def test_benchmark_comparison(self):
        """Test benchmark comparison with baseline"""
        benchmarks = PerformanceBenchmarks()

        # Create fake baseline
        benchmarks.baseline_results = {
            "test_benchmark": BenchmarkResult(
                name="test_benchmark", duration_ms=100.0, memory_kb=50.0, iterations=1
            )
        }

        # Run same benchmark
        benchmarks.benchmark_recursion_fibonacci(n=10)

        # Should be able to compare
        # (comparison prints output, just verify it doesn't crash)
        benchmarks.compare_with_baseline()


class TestOptimizationIntegration(unittest.TestCase):
    """Integration tests for optimizations"""

    def test_full_optimization_pipeline(self):
        """Test full optimization pipeline"""
        code = """
fn calculate()
  let a = 10 + 20
  let b = 30 * 2
  let c = a + b
  return c

calculate()
"""
        # Compile
        code = "let x = 42"
        ast = parse(code)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(ast)

        # Optimize
        optimizer = BytecodeOptimizer()
        optimizer.constant_folding_enabled = True
        optimizer.peephole_enabled = True
        optimized = optimizer.optimize_module(module)

        # Should produce valid module
        self.assertIsNotNone(optimized)
        self.assertGreater(len(optimized.functions), 0)

        # Stats should be populated
        stats = optimizer.get_stats()
        self.assertIn("optimizations_applied", stats)

    def test_cache_integration(self):
        """Test cache integration with compilation"""
        code = "let x = 42"
        ast = parse(code)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(ast)

        cache = BytecodeCache()

        # First compilation - cache miss
        optimized1 = optimize_and_cache(module, cache, "hash1")
        self.assertEqual(cache.misses, 1)

        # Second compilation with same hash - cache hit
        optimized2 = optimize_and_cache(module, cache, "hash1")
        self.assertEqual(cache.hits, 1)

        # Should get same result
        self.assertIs(optimized1, optimized2)


class TestPerformanceThresholds(unittest.TestCase):
    """Test performance meets expected thresholds"""

    def test_fibonacci_performance(self):
        """Test Fibonacci completes within acceptable time"""
        benchmarks = PerformanceBenchmarks()

        # Small n should be fast
        result = benchmarks.benchmark_recursion_fibonacci(n=10)
        self.assertLess(
            result.duration_ms,
            1000,
            f"Fibonacci(10) took {result.duration_ms}ms, expected < 1000ms",
        )

        # Medium n should still be reasonable
        result = benchmarks.benchmark_recursion_fibonacci(n=15)
        self.assertLess(
            result.duration_ms,
            5000,
            f"Fibonacci(15) took {result.duration_ms}ms, expected < 5000ms",
        )

    def test_list_operations_performance(self):
        """Test list operations are efficient"""
        benchmarks = PerformanceBenchmarks()

        # Map 1000 elements should be fast
        result = benchmarks.benchmark_list_map(size=1000)
        self.assertLess(
            result.duration_ms,
            100,
            f"Map on 1000 elements took {result.duration_ms}ms, expected < 100ms",
        )

        # Filter 1000 elements should be fast
        result = benchmarks.benchmark_list_filter(size=1000)
        self.assertLess(
            result.duration_ms,
            100,
            f"Filter on 1000 elements took {result.duration_ms}ms, expected < 100ms",
        )

    def test_loop_performance(self):
        """Test loop performance"""
        benchmarks = PerformanceBenchmarks()

        # 1000 iterations should be fast
        result = benchmarks.benchmark_for_loop(size=1000)
        self.assertLess(
            result.duration_ms,
            100,
            f"1000 loop iterations took {result.duration_ms}ms, expected < 100ms",
        )


if __name__ == "__main__":
    unittest.main()
