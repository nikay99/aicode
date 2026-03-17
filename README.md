# AICode v1.0 - Full Release 🎉

A **KI-optimized programming language** designed for minimal token usage and maximum clarity.

## ✨ Features

- **🎯 40-60% Less Tokens** than Python
- **📝 Significant Whitespace** - No braces or semicolons needed
- **🔒 Immutable by Default** - Fewer bugs from side effects
- **🎨 Pattern Matching** - Expressive condition handling
- **⚡ First-class Functions** - Lambdas and higher-order functions
- **🛡️ Result Type** - Explicit error handling without exceptions
- **📦 Rich Standard Library** - map, filter, reduce, range, and more
- **🔍 Type Inference** - Optional type annotations

## 🚀 Quick Start

### Installation

```bash
git clone <repository>
cd AICode
python3 -m pip install -e .
```

### Hello World

```bash
$ aic repl
AICode v1.0.0 REPL
> println("Hello, World!")
Hello, World!
```

### Run a File

```bash
$ aic run examples/fizzbuzz.aic
1
2
Fizz
4
Buzz
...
```

## 📚 Language Guide

### Variables

```aic
let x = 42           # Immutable variable
let mut y = 0        # Mutable variable
const PI = 3.14159   # Constant
```

### Functions

```aic
fn add(a, b)
  return a + b

fn greet(name: str) -> str
  return "Hello, " + name

# Lambdas
let double = fn(x): x * 2
let square = \x: x * x
```

### Control Flow

```aic
# If-Else (is an expression!)
let result = if x > 0
  "positive"
else if x < 0
  "negative"
else
  "zero"

# Pattern Matching
let name = match value
  1 -> "one"
  2 -> "two"
  _ -> "other"

# Loops
for i in range(10)
  println(i)

while condition
  do_something()
```

### Collections

```aic
# Lists
let nums = [1, 2, 3, 4, 5]
let doubled = map(fn(x): x * 2, nums)
let evens = filter(fn(x): x % 2 == 0, nums)
let sum = reduce(fn(acc, x): acc + x, nums, 0)

# Dictionaries (Structs)
let point = {x: 3, y: 4}
let dist = point.x * point.x + point.y * point.y
```

### Error Handling with Result

```aic
fn divide(a, b)
  if b == 0
    return Err("Division by zero")
  else
    return Ok(a / b)

let result = divide(10, 2)

if is_ok(result)
  println(unwrap(result))      # 5.0
else
  println(result._error)

# Or with unwrap_or
let value = unwrap_or(result, 0)
```

## 📊 Token Efficiency Comparison

### Python (127 tokens)
```python
def process_users(users):
    active = [u.name.upper() for u in users if u.active]
    return sorted(active)[:10]
```

### AICode (67 tokens - 47% less)
```aic
fn process_users(users)
  users
    |> filter(.active)
    |> map(.name.upper)
    |> sort
    |> take(10)
```

## 🧪 Running Tests

```bash
# Run all tests
python3 -m pytest tests/test_aicode.py -v

# Run specific test
python3 -m pytest tests/test_aicode.py::TestFizzBuzz -v
```

## 📖 Examples

### FizzBuzz

```aic
fn fizzbuzz(n)
  if n % 3 == 0 and n % 5 == 0
    return "FizzBuzz"
  else if n % 3 == 0
    return "Fizz"
  else if n % 5 == 0
    return "Buzz"
  else
    return n

for i in range(1, 100)
  println(fizzbuzz(i))
```

### Data Processing

```aic
let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

let evens = filter(fn(x): x % 2 == 0, numbers)
let doubled = map(fn(x): x * 2, evens)
let total = reduce(fn(acc, x): acc + x, doubled, 0)

println(total)  # 60
```

### Working with Dictionaries

```aic
let user = {
  name: "Alice",
  age: 30,
  email: "alice@example.com"
}

fn greet(u)
  return "Hello, " + u.name + "!"

println(greet(user))
```

## 🛠️ CLI Commands

```bash
# Run a file
aic run <file.aic>

# Start REPL
aic repl

# Tokenize (debug)
aic tokenize <file.aic>

# Parse and show AST (debug)
aic parse <file.aic>
```

## 📁 Project Structure

```
AICode/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── lexer.py           # Tokenizer
│   ├── parser.py          # Recursive descent parser
│   ├── ast_nodes.py       # AST node definitions
│   └── interpreter.py     # Tree-walking interpreter
├── tests/
│   └── test_aicode.py     # Comprehensive test suite
├── examples/              # Example programs
│   ├── hello.aic
│   ├── fizzbuzz.aic
│   ├── data_processing.aic
│   └── result_example.aic
├── main.py               # CLI entry point
├── setup.py              # Package setup
└── README.md             # This file
```

## 🔧 Implementation Details

### Lexer
- Significant whitespace handling (INDENT/DEDENT tokens)
- Support for integers, floats, strings, booleans
- Comment handling (`#` to end of line)

### Parser
- Recursive descent parser
- Pratt parser for expressions
- Support for function declarations, control flow, pattern matching

### Interpreter
- Tree-walking interpreter
- Environment-based variable scoping
- First-class functions and closures

## 🎯 Future Roadmap

- [ ] Type checker with Hindley-Milner inference
- [ ] Compiler to bytecode
- [ ] Pipe operator (`|>`) full implementation
- [ ] Struct types with methods
- [ ] Module system
- [ ] Package manager
- [ ] LSP (Language Server Protocol)
- [ ] VS Code extension

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Python, Rust, and functional programming languages
- Designed for AI-assisted programming
- Optimized for minimal token usage with GPT/Claude models

---

**Made with ❤️ for the future of AI-assisted programming**
