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

### 🚧 In Progress
- [ ] Hindley-Milner Type Checker
- [ ] Bytecode Compiler
- [ ] Virtual Machine

### ⏳ Planned
- [ ] LLM Training Data
- [ ] Ecosystem Tools

---

## 🏆 High Priority Tasks

### 1. Type Checker (Hindley-Milner) ⭐⭐⭐

**Status**: Not Started  
**Difficulty**: Hard  
**Time Estimate**: 3-5 days  
**Files**: `src/type_checker_ai.py`

**Description**:  
Implement Hindley-Milner type inference algorithm for the new AST.

**Requirements**:
- Type variable generation
- Unification algorithm
- Generalization/instantiation
- Type inference for all AST nodes
- Polymorphic type schemes

**Reference**:  
- Current type checker: `legacy/interpreter.py` (for reference only)
- Algorithm W implementation
- HM type system documentation

**Acceptance Criteria**:
```python
# Should infer types automatically
𝕍 x ≔ 42           # x: ℤ
λ f(α) → α + 1     # f: ℤ → ℤ
∀⟨[1,2,3], λx: x*2⟩  # [∀] : ℤ → [ℤ]
```

**Tasks**:
- [ ] Create TypeVar, TypeConst, TypeArrow classes
- [ ] Implement unify() function
- [ ] Implement infer() for each Expr type
- [ ] Implement check_statement() for each Stmt type
- [ ] Add occurs check
- [ ] Test with 20+ examples

---

### 2. Bytecode Compiler ⭐⭐⭐

**Status**: Not Started  
**Difficulty**: Medium-Hard  
**Time Estimate**: 3-4 days  
**Files**: `src/compiler_ai.py`, `src/bytecode.py`

**Description**:  
Compile AST to bytecode for VM execution.

**Requirements**:
- Generate bytecode from AST
- Handle all expression types
- Handle all statement types
- Function compilation
- Local variable indexing
- Constant pool management

**Acceptance Criteria**:
```bash
$ python3 -c "
from compiler_ai import compile
from vm_ai import VM

ast = parse('𝕍 x ≔ 42')
bytecode = compile(ast)
vm = VM()
result = vm.run(bytecode)
print(result)  # Should output 42
"
```

**Tasks**:
- [ ] Map AST nodes to opcodes
- [ ] Implement expression compilation
- [ ] Implement statement compilation
- [ ] Function compilation with closures
- [ ] Constant pool deduplication
- [ ] Label resolution for jumps
- [ ] Bytecode optimization passes

---

### 3. Virtual Machine ⭐⭐⭐

**Status**: Not Started  
**Difficulty**: Medium  
**Time Estimate**: 2-3 days  
**Files**: `src/vm_ai.py`

**Description**:  
Stack-based VM to execute bytecode.

**Requirements**:
- Stack-based execution
- Instruction dispatch
- Call frame management
- Built-in function support
- Error handling

**Acceptance Criteria**:
- Execute all bytecode instructions correctly
- Handle function calls
- Manage stack properly
- Catch runtime errors

**Tasks**:
- [ ] Implement all opcodes from `src/bytecode.py`
- [ ] Stack operations (push, pop, peek)
- [ ] Local/global variable access
- [ ] Function call/return
- [ ] Arithmetic operations
- [ ] Comparison operations
- [ ] Built-in functions (map, filter, etc.)

---

## 🔧 Medium Priority Tasks

### 4. Standard Library ⭐⭐

**Status**: Not Started  
**Difficulty**: Medium  
**Time Estimate**: 2 days  
**Files**: `src/stdlib_ai.py`

**Description**:  
Implement core library functions as Unicode symbols.

**Functions Needed**:
```
∀  # map
∃  # filter  
∑  # reduce
∈  # contains
∉  # not_contains
∋  # reverse
⊕  # concat
⊗  # zip
...
```

**Tasks**:
- [ ] List operations
- [ ] String operations
- [ ] Math operations
- [ ] I/O operations
- [ ] Dict operations

---

### 5. Error Handling ⭐⭐

**Status**: Not Started  
**Difficulty**: Medium  
**Time Estimate**: 1-2 days  
**Files**: All

**Description**:  
Implement proper error handling with codes instead of messages.

**Requirements**:
- Error codes (E001, E002, etc.)
- Error lookup table
- Stack traces
- Graceful failures

**Error Code Schema**:
```
E1xx - Lexer errors
E2xx - Parser errors
E3xx - Type errors
E4xx - Runtime errors
```

---

### 6. CLI Tool ⭐⭐

**Status**: Partial  
**Difficulty**: Easy  
**Time Estimate**: 1 day  
**Files**: `aic`

**Description**:  
Create working CLI entry point.

**Current Issue**:  
`aic` command is broken after restructure.

**Tasks**:
- [ ] Fix `setup.py` entry points
- [ ] Create `aic` command
- [ ] Add subcommands: run, compile, tokenize, parse
- [ ] Add --help documentation
- [ ] Add --version flag

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

**Status**: Partial  
**Difficulty**: Easy  
**Time Estimate**: 1 day  
**Files**: `examples/`

**Description**:  
Create comprehensive examples.

**Needed Examples**:
- [ ] Hello World
- [ ] Fibonacci
- [ ] FizzBuzz
- [ ] Data processing
- [ ] Web scraping
- [ ] File I/O
- [ ] Algorithms (sort, search)

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

**Status**: Partial  
**Difficulty**: Medium  
**Time Estimate**: 2-3 days  
**Files**: `tests/`

**Description**:  
Comprehensive test coverage.

**Coverage Goals**:
- [ ] Lexer: 100%
- [ ] Parser: 100%
- [ ] Type checker: 90%
- [ ] Compiler: 90%
- [ ] VM: 90%
- [ ] Integration: 80%

**Types of Tests**:
- Unit tests
- Integration tests
- Property-based tests
- Benchmark tests

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

1. **Parser DOT token missing** ⚠️
   - Fixed in lexer, needs verification in parser

2. **Type variance in AST** ⚠️
   - ExprStmt vs Stmt type compatibility
   - May need covariance in type hints

3. **Import paths broken** ⚠️
   - Tests can't find modules
   - Need to fix sys.path handling

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

*Last updated: 2024*  
*Maintainers: nikay99*
