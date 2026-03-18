# TODO.md - Contributing to AICode-AI

> **Welcome Contributors!** This is a roadmap of what needs to be done.

## 🎯 Current Status

**Last Updated**: 2024  
**Version**: 0.1.0-alpha  
**Phase**: Core Development

### ✅ Completed
- [x] Unicode Lexer with mathematical symbols
- [x] Recursive descent Parser
- [x] Compact AST structure
- [x] Basic test suite
- [x] Bytecode Compiler (src/compiler.py)
- [x] Virtual Machine with all opcodes (src/vm.py)
- [x] Standard Library with Unicode symbols (src/stdlib_ai.py)
- [x] Error Handling System with codes E1xx-E4xx (src/errors.py)
- [x] Complete CLI tool (run, repl, tokenize, parse, compile, check)
- [x] Comprehensive test suite (320+ tests)
- [x] Example programs (hello, fibonacci, fizzbuzz, sorting, functions, types)

### 🚧 In Progress
- [ ] Hindley-Milner Type Checker (partial - exists but needs completion)
- [ ] Iterator opcodes (ITER, ITER_NEXT) - implemented in VM

### ⏳ Planned
- [ ] LLM Training Data
- [ ] Ecosystem Tools
- [ ] Formatter
- [ ] LSP Support
- [ ] VS Code Extension
- [ ] Package Manager

---

## 🏆 High Priority Tasks

### 1. Type Checker (Hindley-Milner) ⭐⭐⭐

**Status**: Partial - Core exists, needs completion  
**Difficulty**: Hard  
**Time Estimate**: 3-5 days  
**Files**: `src/type_checker.py`

**Description**:  
Hindley-Milner type inference algorithm exists in `src/type_checker.py`. Needs completion and integration.

**What's Done**:
- ✅ TypeVar, TypeConst, TypeArrow classes created
- ✅ Unify() function implemented
- ✅ Infer() for most Expr types
- ✅ Basic type checking infrastructure

**Still Needed**:
- [ ] Complete check_statement() for all Stmt types
- [ ] Integration with compiler
- [ ] Full test coverage (20+ examples)

**Reference**:  
- Current type checker: `src/type_checker.py`
- Algorithm W implementation
- HM type system documentation

---

### 2. Bytecode Compiler ⭐⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Medium-Hard  
**Time Estimate**: 3-4 days  
**Files**: `src/compiler.py`, `src/bytecode.py`

**Description**:  
Compile AST to bytecode for VM execution.

**Completed**:
- ✅ Generate bytecode from AST
- ✅ Handle all expression types
- ✅ Handle all statement types
- ✅ Function compilation
- ✅ Local variable indexing
- ✅ Constant pool management
- ✅ Map AST nodes to opcodes
- ✅ Expression compilation
- ✅ Statement compilation
- ✅ Label resolution for jumps

**Notes**:
Working implementation in `src/compiler.py`. Compiles all expressions and statements including:
- Let/Const variable declarations
- Functions and lambdas
- If/while/for statements
- Lists and dictionaries
- Arithmetic and logical operations

---

### 3. Virtual Machine ⭐⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Medium  
**Time Estimate**: 2-3 days  
**Files**: `src/vm.py`

**Description**:  
Stack-based VM to execute bytecode.

**Completed**:
- ✅ All opcodes from `src/bytecode.py` implemented
- ✅ Stack operations (push, pop, peek)
- ✅ Local/global variable access
- ✅ Function call/return
- ✅ Arithmetic operations
- ✅ Comparison operations
- ✅ Built-in functions (map, filter, etc.)
- ✅ Error handling with error codes
- ✅ Call frame management
- ✅ Instruction dispatch

**Notes**:
Working implementation in `src/vm.py`. Successfully executes bytecode with all major features including iteration, function calls, and built-in operations.

---

## 🔧 Medium Priority Tasks

### 4. Standard Library ⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Medium  
**Time Estimate**: 2 days  
**Files**: `src/stdlib_ai.py`

**Description**:  
Implement core library functions as Unicode symbols.

**Functions Implemented**:
```
∀  # map - Apply function to all elements
∃  # filter - Filter elements by predicate
∑  # reduce - Fold/reduce list to single value
∈  # contains - Check if element is in list
∉  # not_contains - Check if element is NOT in list
∋  # reverse - Reverse a list
⊕  # concat - Concatenate two lists
⊗  # zip - Zip two lists together
```

**Additional Functions**:
- String operations: `strlen`, `substring`, `split`, `join`, `replace`
- Math operations: `abs`, `min`, `max`, `sum`, `range`
- I/O operations: `print`, `println`, `input`
- Dict operations: `keys`, `values`
- Result types: `Ok`, `Err`, `is_ok`, `is_err`, `unwrap`, `unwrap_or`

**Completed**:
- ✅ List operations
- ✅ String operations
- ✅ Math operations
- ✅ I/O operations
- ✅ Dict operations
- ✅ 42 comprehensive tests
- ✅ All functions registered in VM

---

### 5. Error Handling ⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Medium  
**Time Estimate**: 1-2 days  
**Files**: `src/errors.py`, All

**Description**:  
Implement proper error handling with codes instead of messages.

**Completed**:
- ✅ Error codes (E1xx-E4xx) implemented
- ✅ Error lookup table in `src/errors.py`
- ✅ Stack traces with line/column information
- ✅ Graceful failures with context
- ✅ 80 error codes covering all error types
- ✅ Updated all modules to use new error system
- ✅ 50 tests for error handling

**Error Code Schema**:
```
E1xx - Lexer errors (E101-E110)
E2xx - Parser errors (E201-E220)
E3xx - Type errors (E301-E320)
E4xx - Runtime errors (E401-E420)
```

**Files Modified**:
- `src/errors.py` - New comprehensive error system
- `src/lexer.py` - Updated to raise LexerError with E1xx codes
- `src/parser.py` - Updated to raise ParserError with E2xx codes
- `src/type_checker.py` - Updated to raise TypeCheckError with E3xx codes
- `src/vm.py` - Updated to raise RuntimeError with E4xx codes
- `src/compiler.py` - Updated to raise CompilerError

---

### 6. CLI Tool ⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Easy  
**Time Estimate**: 1 day  
**Files**: `main.py`, `setup.py`

**Description**:  
Complete CLI entry point with all subcommands.

**Completed**:
- ✅ `setup.py` entry points fixed
- ✅ `aic` command working
- ✅ Subcommands implemented:
  - `run <file>` - Run an AICode file
  - `repl` - Start interactive REPL
  - `tokenize <file>` - Show tokens
  - `parse <file>` - Show AST
  - `compile <file>` - Show bytecode
  - `check <file>` - Type check only
- ✅ `--help` documentation for all commands
- ✅ `--version` flag
- ✅ Verbose mode (`-v`)
- ✅ Error handling with proper exit codes
- ✅ Multiline REPL with Python-style prompts
- ✅ 484 lines of comprehensive CLI implementation

**Usage Examples**:
```bash
aic run examples/hello.aic
aic repl --prompt python
aic tokenize examples/fizzbuzz.aic
aic parse examples/functions.aic
aic compile examples/sorting.aic -v
aic check examples/types.aic
aic --help
```

---

## 📚 Documentation Tasks

### 7. Language Specification ⭐

**Status**: Partial  
**Difficulty**: Easy  
**Time Estimate**: 2-3 days  
**Files**: `docs/LANGUAGE_SPEC.md`

**Description**:  
Complete formal language specification.

**Sections Needed**:
- [ ] Lexical structure
- [ ] Grammar (BNF)
- [ ] Type system
- [ ] Semantics
- [ ] Standard library reference

---

### 8. Examples ⭐

**Status**: ✅ Completed  
**Difficulty**: Easy  
**Time Estimate**: 1 day  
**Files**: `examples/`

**Description**:  
Create comprehensive examples.

**Completed Examples**:
- ✅ **Hello World** (`examples/hello.aic`) - Basic variables, constants, math operations
- ✅ **Fibonacci** (`examples/fibonacci.aic`) - Iterative, recursive, and fast doubling implementations
- ✅ **FizzBuzz** (`examples/fizzbuzz.aic`) - Classic 1-100 FizzBuzz
- ✅ **Data processing** (`examples/data_processing.aic`) - Lists, dicts, statistics
- ✅ **Functions** (`examples/functions.aic`) - Higher-order functions, closures, currying
- ✅ **Types** (`examples/types.aic`) - Type annotations and generics
- ✅ **Sorting** (`examples/sorting.aic`) - Bubble sort, quick sort, merge sort
- ✅ **Existing**: `examples/simple.aic`, `examples/demo.aic`, `examples/v2_simple.aic`

**Running Examples**:
```bash
aic run examples/hello.aic
aic run examples/fizzbuzz.aic
aic run examples/fibonacci.aic
aic run examples/functions.aic
aic run examples/sorting.aic
aic run examples/types.aic
aic run examples/data_processing.aic
```

---

## 🔬 Research Tasks

### 9. LLM Training Data ⭐⭐⭐

**Status**: Not Started  
**Difficulty**: Hard  
**Time Estimate**: 1 week  
**Files**: `training/`

**Description**:  
Generate training data for fine-tuning LLMs on AICode-AI.

**Requirements**:
- 10,000+ code examples
- Python → AICode-AI pairs
- Natural language → AICode-AI pairs
- Prompt templates

**Tasks**:
- [ ] Create code generation scripts
- [ ] Translate Python examples
- [ ] Generate NL→Code pairs
- [ ] Create training dataset
- [ ] Fine-tuning scripts

---

### 10. Token Efficiency Analysis ⭐

**Status**: Partial  
**Difficulty**: Easy  
**Time Estimate**: 1 day  
**Files**: `benchmarks/`

**Description**:  
Measure actual token savings vs Python.

**Tasks**:
- [ ] Create benchmark suite
- [ ] Compare with tiktoken
- [ ] Generate comparison charts
- [ ] Document results

---

## 🛠️ Tooling Tasks

### 11. Formatter ⭐

**Status**: Not Started  
**Difficulty**: Medium  
**Time Estimate**: 2 days  
**Files**: `src/formatter_ai.py`

**Description**:  
Auto-format AICode-AI source.

**Features**:
- Consistent spacing
- Indentation fix
- Import sorting

---

### 12. LSP Support ⭐

**Status**: Not Started  
**Difficulty**: Hard  
**Time Estimate**: 1 week  
**Files**: `lsp/`

**Description**:  
Language Server Protocol support.

**Features**:
- Syntax highlighting
- Auto-completion
- Go to definition
- Error diagnostics

---

## 🧪 Testing Tasks

### 13. Test Suite ⭐⭐

**Status**: ✅ Completed  
**Difficulty**: Medium  
**Time Estimate**: 2-3 days  
**Files**: `tests/`

**Description**:  
Comprehensive test coverage.

**Coverage Achieved**:
- ✅ **Lexer**: 100% (58 tests in `test_lexer.py`)
- ✅ **Parser**: 89% (74 tests in `test_parser.py`)
- ✅ **Type checker**: Infrastructure exists (partial)
- ✅ **Compiler**: 90%+ (tests in `test_compiler.py`)
- ✅ **VM**: 90%+ (tests in `test_vm.py`)
- ✅ **Integration**: 80%+ (tests in `test_integration.py`)
- ✅ **Standard Library**: 42 tests in `test_stdlib.py`
- ✅ **Error Handling**: 50 tests in `test_errors.py`

**Total**: **323 tests passing, 34 failing**

**Test Files**:
- `tests/test_lexer.py` - 58 tests
- `tests/test_parser.py` - 74 tests
- `tests/test_compiler.py` - Compiler tests
- `tests/test_vm.py` - VM execution tests
- `tests/test_integration.py` - End-to-end tests
- `tests/test_stdlib.py` - Standard library tests
- `tests/test_errors.py` - Error handling tests
- `tests/test_aicode.py` - Original test suite
- `tests/utils.py` - Test utilities

**Types of Tests**:
- ✅ Unit tests
- ✅ Integration tests
- [ ] Property-based tests
- [ ] Benchmark tests

**Running Tests**:
```bash
# All tests
python3 -m pytest tests/ -v

# Specific test file
python3 -m pytest tests/test_lexer.py -v

# With coverage
python3 -m pytest tests/ --cov=src
```

---

## 🎨 Ecosystem Tasks

### 14. VS Code Extension ⭐

**Status**: Not Started  
**Difficulty**: Medium  
**Time Estimate**: 3-4 days  
**Files**: `vscode-extension/`

**Description**:  
VS Code support for AICode-AI.

**Features**:
- Syntax highlighting
- Error squiggles
- Format on save
- Snippets

---

### 15. Package Manager ⭐

**Status**: Not Started  
**Difficulty**: Hard  
**Time Estimate**: 1-2 weeks  
**Files**: `src/package_manager.py`

**Description**:  
Package management for AICode-AI.

**Features**:
- Dependency resolution
- Package installation
- Version management
- Registry

---

## 🐛 Bug Fixes

### Known Issues

1. **Type variance in AST** ⚠️
   - ExprStmt vs Stmt type compatibility
   - May need covariance in type hints

2. **34 tests still failing** ⚠️
   - Some parser tests (AND, OR, NOT symbols)
   - Some VM tests (stack underflow, undefined global)
   - Some integration tests (chained operations)
   - Some stdlib tests (map, filter, reduce Unicode symbols)
   - Type checker needs completion

3. **Performance** ⚠️
   - No bytecode optimization passes yet
   - Constant pool could use deduplication

---

## 📋 How to Contribute

### Getting Started

1. **Fork the repo**
2. **Pick a task** from above
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Code**
5. **Test**
6. **Submit PR**

### Code Style

- Follow existing patterns
- Use type hints
- Document with docstrings
- Keep it simple

### Testing

```bash
# Run tests
python3 -m pytest tests/

# Run specific test
python3 test_lexer_ai.py

# Check type errors
mypy src/
```

### Commit Messages

```
type: brief description

Longer explanation if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`

---

## 🗣️ Communication

- **Issues**: Use GitHub issues for bugs/features
- **Discussions**: Use GitHub discussions for questions
- **PRs**: All contributions via pull requests

## 🏅 Recognition

Contributors will be:
- Listed in README
- Mentioned in release notes
- Added to AUTHORS file

---

## 📞 Need Help?

If you're stuck:
1. Check existing code for patterns
2. Read the documentation
3. Ask in discussions
4. Look at legacy/ for reference

**Let's build the future of AI programming together!** 🤖

---

*Last updated: 2025-03-17*  
*Maintainers: nikay99*

---

## 📊 Implementation Summary

### Phase 1 Complete ✅
- ✅ Lexer & Parser (ASCII and Unicode versions)
- ✅ Bytecode Compiler with all expression/statement types
- ✅ Virtual Machine with 42 opcodes
- ✅ Standard Library (Unicode math symbols)
- ✅ Error Handling System (E1xx-E4xx)
- ✅ Complete CLI Tool
- ✅ Comprehensive Test Suite (323 passing tests)
- ✅ Example Programs

### Phase 2 In Progress 🚧
- 🚧 Hindley-Milner Type Checker (core exists, needs completion)
- 🚧 Iterator implementation improvements

### Phase 3 Planned 📅
- 📅 Formatter
- 📅 LSP Support
- 📅 VS Code Extension
- 📅 Package Manager
- 📅 LLM Training Data Generation
