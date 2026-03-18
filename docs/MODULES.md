# AICode Module System

## Overview

AICode now supports a module system for organizing and reusing code across files.

## Import Syntax

### Import all exports from a module

```
import math

println(math.PI)
println(math.square(5))
```

### Import with alias

```
import math as m

println(m.PI)
println(m.square(5))
```

### Import specific names

```
import math { PI, square }

println(PI)
println(square(5))
```

## Module Search Path

The module system looks for modules in the following order:

1. Current directory
2. Standard library directory (`src/stdlib/`)

## Creating Modules

A module is simply an `.aic` file. All top-level definitions (let, const, fn) are automatically exported.

Example module (`math.aic`):
```
let PI = 3.14159
let E = 2.71828

fn square(x)
  return x * x

fn cube(x)
  return x * x * x
```

## Standard Library Modules

### Math Module (`math.aic`)

```
import math

# Constants
math.PI          # 3.14159...
math.E           # 2.71828...

# Functions
math.square(x)   # x squared
math.cube(x)     # x cubed
math.abs(x)      # Absolute value
math.max(a, b)   # Maximum of two values
math.min(a, b)   # Minimum of two values
math.factorial(n) # Factorial of n
math.fibonacci(n) # nth Fibonacci number
math.is_even(n)  # Check if even
math.is_odd(n)   # Check if odd
math.gcd(a, b)   # Greatest common divisor
math.lcm(a, b)   # Least common multiple
```

### String Module (`string.aic`)

```
import string

string.reverse(s)      # Reverse a string
string.uppercase(s)    # Convert to uppercase
string.lowercase(s)    # Convert to lowercase
string.contains(s, substr)  # Check if substring exists
string.starts_with(s, prefix)
string.ends_with(s, suffix)
string.trim(s)         # Remove whitespace from ends
string.split(s, delimiter)  # Split string into list
string.join(strings, delimiter)  # Join list into string
```

## Error Handling

- **Module not found**: Error E413 when trying to import a non-existent module
- **Circular imports**: Error E414 when circular dependencies are detected
- **Undefined export**: Error E413 when accessing a name that wasn't exported

## Examples

See the `examples/` directory for working module examples:
- `math.aic` - Mathematical functions and constants
- `string.aic` - String manipulation utilities
