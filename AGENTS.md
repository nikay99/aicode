# AICode-AI Agent Guidelines

> Comprehensive guide for AI agents working on the AICode-AI project

## Project Overview

**AICode-AI** is a programming language designed specifically for LLMs, using mathematical Unicode symbols to achieve 40-60% token reduction compared to Python.

- **Language Type**: Compiled language with Hindley-Milner type inference
- **Architecture**: Lexer → Parser → Type Checker → Compiler → VM
- **Version**: 0.2.0
- **Python Version**: 3.10+

## Directory Structure

```
/root/snap/tomber/AICode/
├── src/                    # Core source code
│   ├── __init__.py        # Package exports
│   ├── lexer.py           # ASCII lexer (v1 compatible)
│   ├── lexer_ai.py        # Unicode lexer (v2)
│   ├── parser.py          # ASCII parser (v1 compatible)
│   ├── parser_ai.py       # Unicode parser (v2)
│   ├── ast_nodes.py       # AST node definitions
│   ├── ast_ai.py          # Additional AST utilities
│   ├── type_checker.py    # Hindley-Milner type inference
│   ├── compiler.py        # Bytecode compiler
│   ├── bytecode.py        # Bytecode format & instructions
│   └── vm.py              # Stack-based virtual machine
├── tests/                  # Test suite
│   └── test_aicode.py     # Main test file
├── examples/               # Example AICode programs
│   ├── hello.aic
│   ├── fizzbuzz.aic
│   ├── fibonacci.aic
│   └── ...
├── docs/                   # Documentation
│   └── V2_ARCHITECTURE.md
├── legacy/                 # Legacy v1 code (reference)
│   ├── interpreter.py
│   └── run_v2.py
├── main.py                 # CLI entry point
├── setup.py                # Package setup
├── Makefile                # Development commands
└── TODO.md                # Task roadmap
```

## Core Components

### 1. Lexer (`src/lexer.py`, `src/lexer_ai.py`)

Tokenizes source code into tokens.

**Main Classes/Functions:**
- `TokenType` - Enum of all token types
- `Token` - Dataclass with type, value, position
- `tokenize(source: str) -> List[Token]`

**Key Token Types:**
- Literals: `INT`, `FLOAT`, `STRING`, `BOOL`, `NULL`
- Keywords: `LET`, `CONST`, `MUT`, `FN`, `IF`, `ELSE`, `MATCH`, `FOR`, `WHILE`, `RETURN`, `STRUCT`, `ENUM`, `IMPORT`
- Operators: `PLUS`, `MINUS`, `STAR`, `SLASH`, `EQ`, `NE`, `LT`, `GT`, `LE`, `GE`, `AND`, `OR`, `NOT`
- Symbols: `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `LBRACKET`, `RBRACKET`, `COMMA`, `DOT`, `COLON`, `ARROW`, `ASSIGN`

**Unicode Symbols (lexer_ai.py):**
- `𝕍` - Variable declaration
- `𝔠` - Constant
- `λ` - Function/lambda
- `?` - If expression
- `:` - Else/branch separator
- `←` - Return
- `∀` - For/map
- `∃` - Filter
- `∑` - Reduce
- `∈` - In operator

### 2. Parser (`src/parser.py`, `src/parser_ai.py`)

Builds AST from tokens.

**Main Classes/Functions:**
- `parse(source: str) -> Program`
- `ParseError` - Parser exception

**AST Node Types (src/ast_nodes.py):**

*Expressions:*
- `IntLiteral(value: int)`
- `FloatLiteral(value: float)`
- `StringLiteral(value: str)`
- `BoolLiteral(value: bool)`
- `NullLiteral()`
- `Identifier(name: str)`
- `ListExpr(elements: List[Expr])`
- `DictExpr(entries: List[DictEntry])`
- `TupleExpr(elements: List[Expr])`
- `FieldAccess(obj: Expr, field: str)`
- `IndexExpr(obj: Expr, index: Expr)`
- `CallExpr(func: Expr, args: List[Expr])`
- `BinaryOp(op: str, left: Expr, right: Expr)`
- `UnaryOp(op: str, operand: Expr)`
- `LambdaExpr(params: List[Param], return_type: Optional[Type], body: Expr)`
- `IfExpr(condition: Expr, then_branch: List[Stmt], else_branch: Optional[Union[List[Stmt], IfExpr]])`
- `MatchExpr(expr: Expr, arms: List[MatchArm])`
- `PipeExpr(left: Expr, right: Expr)`

*Patterns:*
- `LiteralPattern(value: Expr)`
- `IdentifierPattern(name: str)`
- `ConstructorPattern(name: str, args: List[Pattern])`
- `WildcardPattern()`

*Statements:*
- `LetStmt(name: str, type: Optional[Type], value: Expr, mutable: bool)`
- `ConstStmt(name: str, value: Expr)`
- `ReturnStmt(value: Optional[Expr])`
- `ExprStmt(expr: Expr)`
- `AssignStmt(name: str, value: Expr)`
- `FnStmt(name: str, params: List[Param], return_type: Optional[Type], body: List[Stmt], exported: bool)`
- `StructStmt(name: str, fields: List[Param], exported: bool)`
- `EnumStmt(name: str, variants: List[EnumVariant], exported: bool)`
- `ForStmt(var: str, iterable: Expr, body: List[Stmt])`
- `WhileStmt(condition: Expr, body: List[Stmt])`
- `ImportStmt(module: str, names: Optional[List[str]], alias: Optional[str])`

*Types:*
- `SimpleType(name: str)`
- `GenericType(base: str, args: List[Type])`
- `FunctionType(param_types: List[Type], return_type: Type)`

*Program:*
- `Program(statements: List[Stmt])`

### 3. Type Checker (`src/type_checker.py`)

Implements Hindley-Milner type inference (654 lines).

**Main Classes:**
- `TypeVar` - Type variable for polymorphism (with counter for unique IDs)
- `TypeConst(name: str)` - Concrete type (int, str, bool, etc.)
- `TypeArrow(arg_types: List[Type], return_type: Type)` - Function type
- `TypeList(element_type: Type)` - List type

**Key Functions:**
- `infer(expr: Expr, env: Dict[str, TypeScheme]) -> Type`
- `unify(t1: Type, t2: Type) -> None` - Unification algorithm
- `generalize(t: Type, env: Dict) -> TypeScheme` - Create polymorphic type
- `instantiate(scheme: TypeScheme) -> Type` - Instantiate polymorphic type
- `check_statement(stmt: Stmt, env: Dict) -> Dict`

**Type Scheme:**
```python
@dataclass
class TypeScheme:
    vars: List[TypeVar]
    type: Type
```

### 4. Compiler (`src/compiler.py`)

Compiles AST to bytecode (419 lines).

**Main Classes:**
- `CompilerError` - Compilation error
- `LocalScope` - Local variable scope management

**Key Methods:**
- `compile_module(ast: Program) -> BytecodeModule`
- `compile_statement(stmt: Stmt) -> List[Instruction]`
- `compile_expression(expr: Expr) -> List[Instruction]`
- `compile_function(fn: FnStmt) -> BytecodeFunction`

### 5. Bytecode (`src/bytecode.py`)

Bytecode format and instruction definitions (199 lines).

**OpCodes:**
```
Stack:     PUSH_CONST, PUSH_NULL, POP, DUP, SWAP
Variables: LOAD_LOCAL, STORE_LOCAL, LOAD_GLOBAL, STORE_GLOBAL
Arithmetic: ADD, SUB, MUL, DIV, MOD, NEG
Comparison: EQ, NE, LT, GT, LE, GE
Logical:   NOT, AND, OR
Control:   JUMP, JUMP_IF_FALSE, JUMP_IF_TRUE, CALL, RETURN, RETURN_VALUE
Collections: BUILD_LIST, BUILD_DICT, INDEX_GET, INDEX_SET, GET_ATTR, SET_ATTR
Iteration: ITER, ITER_NEXT
Misc:      PRINT, PRINTLN, NOP, HALT
```

**Data Structures:**
- `Instruction(opcode: OpCode, operand: int = 0)`
- `BytecodeFunction(name: str, code: List[Instruction], locals: int, params: int, constants: List)`
- `BytecodeModule(functions: List[BytecodeFunction], constants: List, global_names: List[str])`
- `BytecodeBuilder` - Builder for constructing bytecode

### 6. VM (`src/vm.py`)

Stack-based virtual machine execution (353 lines).

**Main Classes:**
- `VMError` - Runtime error
- `CallFrame` - Function call frame (function, ip, locals)

**Key Methods:**
- `run(module: BytecodeModule) -> Any`
- `execute_instruction(instr: Instruction) -> None`
- `call_function(func: BytecodeFunction, args: List) -> Any`

**Runtime Stack:**
- Value stack for operands
- Call stack for function frames
- Global variables dictionary

## Development Commands

```bash
# Install package
pip install -e .

# Run tests
python3 -m pytest tests/test_aicode.py -v

# Run specific test files
python3 test_lexer_ai.py
python3 test_parser_ai.py

# Run examples
python3 main.py run examples/hello.aic
python3 main.py run examples/fizzbuzz.aic
python3 main.py run examples/demo.aic

# Start REPL
python3 main.py repl

# Clean build artifacts
make clean

# Format code
make format  # uses black

# Lint code
make lint    # uses flake8

# Development helpers
make help
```

## Code Conventions

### Style Guidelines
- **Type hints required** on all function signatures
- **No comments** (per project philosophy - "Zero Boilerplate")
- **Dataclasses** for AST nodes and simple data structures
- **100 char max line length**
- **Snake_case** for variables and functions
- **PascalCase** for classes and types

### Pattern: Error Handling
```python
class SpecificError(Exception):
    """Error with code and message"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")
```

### Pattern: Building Lists of Instructions
```python
def compile_expression(self, expr: Expr) -> List[Instruction]:
    instructions: List[Instruction] = []
    # ... build instructions
    return instructions
```

### Pattern: Type Inference
```python
def infer(self, expr: Expr, env: Dict[str, TypeScheme]) -> Type:
    if isinstance(expr, IntLiteral):
        return TypeConst("int")
    # ... handle other expression types
```

## Current Status

**All 26 tests passing** as of 2026-03-18.

### Working Components
- Lexer (ASCII + Unicode)
- Parser (ASCII + Unicode)
- Bytecode Compiler — all core constructs working
- Stack-based VM — all opcodes implemented including ITER/ITER_NEXT
- Interpreter (`src/interpreter.py`) — wraps Compiler + VM with output capture
- Built-ins: `println`, `print`, `range`, `map`, `filter`, `reduce`, `length`, `str`, `int`, `float`, `keys`, `values`, `Ok`, `Err`, `is_ok`, `is_err`, `unwrap`, `unwrap_or`

### Remaining Work
- Standard library (`src/stdlib_ai.py`) — not implemented; add Unicode symbol aliases
- Type checker integration — `src/type_checker.py` exists but is not wired into the pipeline
- CLI tool (`main.py`) — needs updating for new interpreter module path
- Module/import system — `import` is a no-op

## Priority Tasks

### Medium Priority
1. **Standard Library** — Wire up Unicode symbols (∀=map, ∃=filter, ∑=reduce) as aliases in VM builtins
2. **Type Checker** — Integrate `src/type_checker.py` into Interpreter pipeline before compilation
3. **CLI Tool** — Update `main.py` to use `src.interpreter`

### Lower Priority
4. **Error Handling** — Implement error codes (E1xx-E4xx) throughout
5. **Language Specification** — Complete formal spec in `docs/`
6. **More Examples** — Expand `examples/` directory

## Testing Approach

### Unit Tests
Tests should be in `tests/` directory. Use `unittest` framework.

### Running Tests
```bash
# All tests
python3 -m pytest tests/ -v

# Specific test file
python3 -m pytest tests/test_aicode.py -v

# With coverage
python3 -m pytest tests/ --cov=src
```

### Test Structure
```python
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lexer import tokenize, TokenType
from src.parser import parse

class TestLexer(unittest.TestCase):
    def test_example(self):
        tokens = tokenize("let x = 42")
        # assertions
```

## Key Patterns for Implementation

### Adding New AST Nodes
1. Add to `src/ast_nodes.py` as dataclass
2. Add parser rule in `src/parser_ai.py`
3. Add type inference in `src/type_checker.py`
4. Add compilation in `src/compiler.py`
5. Add VM execution in `src/vm.py`
6. Add tests

### Adding New Bytecode OpCode
1. Add to `OpCode` enum in `src/bytecode.py`
2. Implement in compiler's `compile_expression`/`compile_statement`
3. Implement in VM's `execute_instruction`
4. Add test

### Adding Standard Library Function
1. Implement in Python in `src/stdlib_ai.py`
2. Register in VM's built-in functions
3. Add Unicode symbol mapping

## File Naming Conventions

- `*_ai.py` - Unicode version (v2)
- `*.py` - ASCII version (v1 compatible)
- `src/` - Core implementation
- `tests/` - Test files
- `examples/` - Example .aic files

## Common Error Codes

Future error handling system (not yet implemented):
```
E1xx - Lexer errors
E2xx - Parser errors  
E3xx - Type errors
E4xx - Runtime errors
```

## Architecture Pipeline

```
Source Code (.aic)
      ↓
   Lexer (Tokens)
      ↓
   Parser (AST)
      ↓
   Type Checker (Typed AST)
      ↓
   Bytecode Compiler (Bytecode)
      ↓
   VM (Execution)
      ↓
   Output
```

## Performance Goals

- Type checking: Catch errors at compile time
- Bytecode: Faster than v1 interpreter
- VM: Stack-based for efficiency

## References

- Hindley-Milner: Algorithm W implementation
- VM Design: Stack-based with call frames
- Unicode: Mathematical Alphanumeric Symbols

---

*Last Updated: 2026-03-18*
*Maintainers: nikay99*
