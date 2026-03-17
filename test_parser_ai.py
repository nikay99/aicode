"""
Test parser
"""

import sys

sys.path.insert(0, "src")

from parser_ai import parse

# Test 1: Simple variable
test1 = "𝕍 x ≔ 42"
print("Test 1:", test1)
ast = parse(test1)
print(f"  AST: {ast}")
print()

# Test 2: Function
test2 = "λ f(α,β) → α+β"
print("Test 2:", test2)
ast = parse(test2)
print(f"  AST: {ast}")
print()

# Test 3: If expression
test3 = "? x>0: x: 0"
print("Test 3:", test3)
ast = parse(test3)
print(f"  AST: {ast}")
print()

# Test 4: Function with body
test4 = """λ add(α,β)
  ← α+β"""
print("Test 4:", repr(test4))
ast = parse(test4)
print(f"  AST: {ast}")
print()

# Test 5: List
test5 = "𝕍 lst ≔ [1,2,3]"
print("Test 5:", test5)
ast = parse(test5)
print(f"  AST: {ast}")
print()

print("✅ Parser tests complete!")
