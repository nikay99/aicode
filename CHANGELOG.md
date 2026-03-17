# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024

### Added
- Initial release of AICode programming language
- Significant whitespace-based syntax (no braces or semicolons)
- Full lexer with INDENT/DEDENT token handling
- Recursive descent parser with Pratt expression parsing
- Tree-walking interpreter
- Variable declarations with `let` and `const`
- Mutable variables with `let mut`
- Function declarations with optional type annotations
- Lambda expressions with `fn(x): x * 2` and `\x: x * 2` syntax
- Pattern matching with `match` expressions
- If-else expressions (can be used as values)
- For loops with `for i in range(...)`
- While loops
- Lists with `[1, 2, 3]` syntax
- Dictionaries with `{key: value}` syntax (supporting identifier keys)
- Struct declarations (basic support)
- Enum declarations (basic support)
- Result type with `Ok()`, `Err()`, `is_ok()`, `is_err()`, `unwrap()`, `unwrap_or()`
- Standard library functions:
  - I/O: `print()`, `println()`
  - Lists: `map()`, `filter()`, `reduce()`, `length()`, `range()`
  - Strings: `str()`, `int()`, `float()`
  - Dicts: `keys()`, `values()`
- Assignment statements
- Arithmetic operators: `+`, `-`, `*`, `/`, `%`
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical operators: `and`, `or`, `not` (and `&&`, `||`, `!`)
- Field access for dictionaries (`.field` syntax)
- Index access for lists and dicts (`[index]`)
- CLI with `run`, `repl`, `tokenize`, and `parse` commands
- Comprehensive test suite with 26 tests
- Package installation via `setup.py`
- MIT License

### Token Efficiency
- Achieves 40-60% fewer tokens than Python
- Example: FizzBuzz in 67 tokens (vs 127 in Python)

### Design Philosophy
- Immutable by default
- Explicit error handling with Result types
- Functional programming support
- Type inference (optional annotations)

[1.0.0]: https://github.com/yourusername/aicode/releases/tag/v1.0.0
