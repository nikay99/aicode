"""
Quick test for Unicode lexer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from lexer_ai import tokenize, TokenType

# Test 1: Simple variable
test1 = "𝕍 x ≔ 42"
print("Test 1:", test1)
tokens = tokenize(test1)
for t in tokens:
    print(f"  {t}")
print()

# Test 2: Function
test2 = "λ f(α,β) → α+β"
print("Test 2:", test2)
tokens = tokenize(test2)
for t in tokens:
    print(f"  {t}")
print()

# Test 3: If expression
test3 = "? x>0: ←x: ←0"
print("Test 3:", test3)
tokens = tokenize(test3)
for t in tokens:
    print(f"  {t}")
print()

# Test 4: With indentation
test4 = """λ f(α)
  ? α>0: ←α: ←0"""
print("Test 4:", repr(test4))
tokens = tokenize(test4)
for t in tokens:
    print(f"  {t}")
