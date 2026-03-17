#!/usr/bin/env python3
"""
AICode Token Analysis - RUTHLESS FACT-CHECKING
Compares AICode vs Python token counts using tiktoken (GPT-4 tokenizer)
"""

import tiktoken

# Initialize tokenizer (cl100k_base is used by GPT-4)
enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    """Count tokens using GPT-4 tokenizer"""
    return len(enc.encode(text))


def analyze_file(name, aicode, python):
    """Compare AICode vs Python token counts"""
    aicode_tokens = count_tokens(aicode)
    python_tokens = count_tokens(python)

    diff = python_tokens - aicode_tokens
    pct_saved = (diff / python_tokens * 100) if python_tokens > 0 else 0

    print(f"\n{'=' * 60}")
    print(f"{name}")
    print(f"{'=' * 60}")
    print(f"AICode:  {aicode_tokens:3d} tokens")
    print(f"Python:  {python_tokens:3d} tokens")
    print(f"Diff:    {diff:+3d} tokens ({pct_saved:+.1f}%)")

    if pct_saved > 0:
        print(f"✓ AICode saves {pct_saved:.1f}%")
    else:
        print(f"✗ Python is {-pct_saved:.1f}% MORE efficient")

    return aicode_tokens, python_tokens


# Test 1: FizzBuzz
print("\n" + "=" * 60)
print("TEST 1: FIZZBUZZ")
print("=" * 60)

fizzbuzz_aic = """fn fizzbuzz(n: int) -> str
  if n % 3 == 0 and n % 5 == 0
    return "FizzBuzz"
  else if n % 3 == 0
    return "Fizz"
  else if n % 5 == 0
    return "Buzz"
  else
    return n

for i in range(1, 100)
  println(fizzbuzz(i))"""

fizzbuzz_py = """def fizzbuzz(n: int) -> str:
    if n % 3 == 0 and n % 5 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)

for i in range(1, 100):
    print(fizzbuzz(i))"""

t1_aic, t1_py = analyze_file("FizzBuzz", fizzbuzz_aic, fizzbuzz_py)

# Test 2: Data Processing (from README claim)
print("\n" + "=" * 60)
print("TEST 2: DATA PROCESSING (README CLAIM)")
print("=" * 60)

data_aic_readme = """fn process_users(users)
  users
    |> filter(.active)
    |> map(.name.upper)
    |> sort
    |> take(10)"""

data_py_readme = """def process_users(users):
    active = [u.name.upper() for u in users if u.active]
    return sorted(active)[:10]"""

t2_aic, t2_py = analyze_file("README Claim", data_aic_readme, data_py_readme)

# Check README's math
readme_claim_aic = 67
readme_claim_py = 127
readme_claim_pct = 47
actual_pct_saved = (t2_py - t2_aic) / t2_py * 100

print(f"\nREADME CLAIMS:")
print(f"  Python: {readme_claim_py} tokens")
print(f"  AICode: {readme_claim_aic} tokens ({readme_claim_pct}% less)")
print(f"\nACTUAL MEASUREMENT:")
print(f"  Python: {t2_py} tokens")
print(f"  AICode: {t2_aic} tokens ({actual_pct_saved:.1f}% less)")
if abs(actual_pct_saved - readme_claim_pct) > 5:
    print(f"  ⚠️  SIGNIFICANT DISCREPANCY!")
    print(
        f"  README is off by {abs(actual_pct_saved - readme_claim_pct):.1f} percentage points"
    )

# Test 3: Real data processing (from examples)
print("\n" + "=" * 60)
print("TEST 3: ACTUAL DATA PROCESSING (from examples/)")
print("=" * 60)

data_aic_real = """# Data processing with pipes

let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Double all numbers, filter evens, sum them
let evens = filter(numbers, fn(x): x % 2 == 0)
let doubled = map(evens, fn(x): x * 2)
let total = reduce(doubled, fn(acc, x): acc + x, 0)

println("Sum of doubled evens: ")
println(total)"""

data_py_real = """# Data processing

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Double all numbers, filter evens, sum them
evens = list(filter(lambda x: x % 2 == 0, numbers))
doubled = list(map(lambda x: x * 2, evens))
total = sum(doubled)

print("Sum of doubled evens: ")
print(total)"""

t3_aic, t3_py = analyze_file("Data Processing (Real)", data_aic_real, data_py_real)

# Test 4: Functions
print("\n" + "=" * 60)
print("TEST 4: SIMPLE FUNCTIONS")
print("=" * 60)

func_aic = """# Functions test
fn add(a: int, b: int) -> int
  return a + b

let x = add(3, 4)
println(x)"""

func_py = """# Functions test
def add(a: int, b: int) -> int:
    return a + b

x = add(3, 4)
print(x)"""

t4_aic, t4_py = analyze_file("Simple Functions", func_aic, func_py)

# Test 5: Full Demo
print("\n" + "=" * 60)
print("TEST 5: FULL DEMO PROGRAM")
print("=" * 60)

demo_aic = """# AICode Demo

# Variables
let x = 10
let y = 20
let sum = x + y
println("Sum: ")
println(sum)

# Functions
fn square(n: int) -> int
  return n * n

let sq = square(5)
println("Square of 5: ")
println(sq)

# Lists and higher-order functions
let nums = [1, 2, 3, 4, 5]
let doubled = map(nums, fn(x): x * 2)
println("Doubled: ")
println(doubled)

# Filtering
let evens = filter(nums, fn(x): x % 2 == 0)
println("Evens: ")
println(evens)

# Match
let value = 3
let name = match value
  1 -> "one"
  2 -> "two"
  3 -> "three"
  _ -> "other"

println("Match result: ")
println(name)

# Loops
println("Counting to 5:")
for i in range(1, 6)
  println(i)"""

demo_py = """# Python Demo

# Variables
x = 10
y = 20
sum_val = x + y
print("Sum: ")
print(sum_val)

# Functions
def square(n: int) -> int:
    return n * n

sq = square(5)
print("Square of 5: ")
print(sq)

# Lists and higher-order functions
nums = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, nums))
print("Doubled: ")
print(doubled)

# Filtering
evens = list(filter(lambda x: x % 2 == 0, nums))
print("Evens: ")
print(evens)

# Match equivalent
value = 3
if value == 1:
    name = "one"
elif value == 2:
    name = "two"
elif value == 3:
    name = "three"
else:
    name = "other"

print("Match result: ")
print(name)

# Loops
print("Counting to 5:")
for i in range(1, 6):
    print(i)"""

t5_aic, t5_py = analyze_file("Full Demo", demo_aic, demo_py)

# Summary
print("\n" + "=" * 60)
print("SUMMARY - ALL TESTS")
print("=" * 60)
print(f"{'Test':<25} {'AICode':>8} {'Python':>8} {'Saved %':>10}")
print("-" * 60)
total_aic = t1_aic + t2_aic + t3_aic + t4_aic + t5_aic
total_py = t1_py + t2_py + t3_py + t4_py + t5_py
total_pct = (total_py - total_aic) / total_py * 100

print(
    f"{'FizzBuzz':<25} {t1_aic:>8} {t1_py:>8} {(t1_py - t1_aic) / t1_py * 100:>9.1f}%"
)
print(
    f"{'README Claim':<25} {t2_aic:>8} {t2_py:>8} {(t2_py - t2_aic) / t2_py * 100:>9.1f}%"
)
print(
    f"{'Data Processing':<25} {t3_aic:>8} {t3_py:>8} {(t3_py - t3_aic) / t3_py * 100:>9.1f}%"
)
print(
    f"{'Simple Functions':<25} {t4_aic:>8} {t4_py:>8} {(t4_py - t4_aic) / t4_py * 100:>9.1f}%"
)
print(
    f"{'Full Demo':<25} {t5_aic:>8} {t5_py:>8} {(t5_py - t5_aic) / t5_py * 100:>9.1f}%"
)
print("-" * 60)
print(f"{'TOTAL':<25} {total_aic:>8} {total_py:>8} {total_pct:>9.1f}%")

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)
if total_pct >= 40:
    print(f"✓ Claim VERIFIED: AICode saves {total_pct:.1f}% tokens")
elif total_pct >= 20:
    print(f"⚠️  Claim PARTIALLY TRUE: AICode saves {total_pct:.1f}% (claimed 40-60%)")
elif total_pct > 0:
    print(f"✗ Claim FALSE: Only {total_pct:.1f}% saved (claimed 40-60%)")
else:
    print(f"✗✗✗ CATASTROPHIC: Python is {-total_pct:.1f}% MORE efficient!")
