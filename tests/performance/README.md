# AICode Performance Benchmarks

This directory contains performance benchmarks and optimizations for the AICode language.

## Structure

- `benchmarks.py` - Main benchmark suite with 20+ performance tests
- `test_performance.py` - Unit tests for benchmarks and optimizations
- `baseline.json` - Saved baseline measurements (generated after first run)

## Running Benchmarks

### Run All Benchmarks

```bash
python3 tests/performance/benchmarks.py
```

### Run Specific Tests

```bash
# Run only Fibonacci tests
python3 -m pytest tests/performance/test_performance.py::TestPerformanceThresholds::test_fibonacci_performance -v

# Run only bytecode optimizer tests
python3 -m pytest tests/performance/test_performance.py::TestBytecodeOptimizer -v
```

## Benchmark Categories

### 1. Recursion Performance
- **fibonacci_recursive_n10** - Fibonacci(10) with O(2^n) complexity
- **fibonacci_recursive_n15** - Fibonacci(15) 
- **fibonacci_recursive_n20** - Fibonacci(20)
- **fibonacci_iterative_n1000** - Fibonacci(1000) with O(n) complexity

### 2. List Operations
- **list_map_size100** - Map operation on 100 elements
- **list_map_size1000** - Map operation on 1000 elements
- **list_filter_size1000** - Filter operation on 1000 elements
- **list_reduce_size1000** - Reduce operation on 1000 elements

### 3. Compilation Speed
- **compilation_100_lines** - Compile 100 lines of code
- **compilation_500_lines** - Compile 500 lines of code
- **compilation_1000_lines** - Compile 1000 lines of code

### 4. Full Execution Pipeline
- **full_execution_small** - Simple arithmetic
- **full_execution_medium** - Factorial calculation
- **full_execution_large** - List summation

### 5. Function Call Performance
- **function_calls_depth100** - 100 nested calls
- **function_calls_depth500** - 500 nested calls

### 6. Loop Performance
- **while_loop_1000_iterations** - 1000 while loop iterations
- **while_loop_10000_iterations** - 10000 while loop iterations
- **for_loop_100_iterations** - 100 for loop iterations
- **for_loop_1000_iterations** - 1000 for loop iterations

## Current Performance Baseline

Based on initial measurements:

| Benchmark | Time | Memory | Status |
|-----------|------|--------|--------|
| fibonacci_recursive_n10 | ~5ms | ~30KB | ✓ OK |
| fibonacci_recursive_n15 | ~48ms | ~32KB | ✓ OK |
| fibonacci_recursive_n20 | ~530ms | ~32KB | ✓ OK |
| fibonacci_iterative_n1000 | ~32ms | ~29KB | ✓ OK |
| list_map_size1000 | ~10ms | ~82KB | ✓ OK |
| compilation_1000_lines | ~57ms | ~1.2MB | ✓ OK |
| while_loop_10000_iterations | ~240ms | ~15KB | ✓ OK |
| for_loop_1000_iterations | ~16ms | ~44KB | ✓ OK |

## Bytecode Optimizations

The `src/optimizer.py` module implements several optimizations:

### 1. Constant Folding
Evaluates constant expressions at compile time:
```
# Before:
PUSH_CONST 2
PUSH_CONST 3
ADD

# After:
PUSH_CONST 5  # Computed at compile time
```

### 2. Peephole Optimizations
- Removes redundant `DUP; POP` sequences
- Removes `LOAD_LOCAL; STORE_LOCAL` pairs
- Removes unused `PUSH_CONST; POP` sequences

### 3. Dead Code Elimination
Removes unreachable code after `RETURN` statements.

### 4. Bytecode Caching
Caches compiled bytecode to avoid recompilation:
```python
from src.optimizer import BytecodeCache, optimize_and_cache

cache = BytecodeCache(max_size=100)
optimized_module = optimize_and_cache(module, cache, source_hash)
```

## Using Optimizations

To use optimizations in your code:

```python
from src.parser import parse
from src.compiler import BytecodeCompiler
from src.optimizer import BytecodeOptimizer

# Compile
ast = parse(source_code)
compiler = BytecodeCompiler()
module = compiler.compile_program(ast)

# Optimize
optimizer = BytecodeOptimizer()
optimizer.constant_folding_enabled = True
optimizer.peephole_enabled = True
optimized = optimizer.optimize_module(module)

# Get stats
stats = optimizer.get_stats()
print(f"Applied {stats['optimizations_applied']} optimizations")
```

## Adding New Benchmarks

To add a new benchmark:

```python
def benchmark_my_feature(self, param: int = 100) -> BenchmarkResult:
    """Benchmark my new feature"""
    code = f"""
fn my_func(n)
  # Implementation
  return result

my_func({param})
"""
    
    def run():
        return self._run_code(code)
    
    duration_ms, _ = self._measure_time(run, iterations=10)
    memory_kb, _ = self._measure_memory(run)
    
    result = BenchmarkResult(
        name=f"my_feature_{param}",
        duration_ms=duration_ms,
        memory_kb=memory_kb,
        iterations=10,
        details={"param": param}
    )
    self.results.append(result)
    return result
```

Then add it to `run_all_benchmarks()`.

## Comparing with Baseline

To save a baseline:

```python
benchmarks = PerformanceBenchmarks()
benchmarks.run_all_benchmarks()
benchmarks.save_baseline("baseline.json")
```

To compare with baseline:

```python
benchmarks = PerformanceBenchmarks()
benchmarks.run_all_benchmarks()
benchmarks.load_baseline("baseline.json")
benchmarks.compare_with_baseline()
```

## Performance Goals

- **Fibonacci(10)**: < 100ms ✓
- **Fibonacci(20)**: < 1000ms ✓
- **List operations (1000 elements)**: < 100ms ✓
- **Compilation (1000 lines)**: < 100ms ✓
- **While loop (10000 iterations)**: < 500ms ✓
- **For loop (1000 iterations)**: < 100ms ✓

## Known Issues

1. Recursive Fibonacci(n=20) is ~530ms - acceptable but could be optimized
2. While loop performance is slower than for loop (expected due to manual index management)
3. Compilation scales linearly with code size

## Future Optimizations

Potential areas for improvement:

1. **Tail Call Optimization** - Reuse stack frames for tail-recursive calls
2. **Inline Caching** - Cache method lookups for repeated calls
3. **Loop Unrolling** - Reduce loop overhead
4. **Better Constant Propagation** - Track constants through assignments
5. **JIT Compilation** - Compile hot paths to native code
