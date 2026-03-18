# AICode Error Handling System - Summary

## Overview
A comprehensive error handling system has been implemented for AICode with standardized error codes (E1xx-E4xx), making errors easier to reference, handle programmatically, and debug.

## Files Created/Modified

### New Files
- **src/errors.py** - Complete error handling system (412 lines)
- **tests/test_errors.py** - Comprehensive test suite (450 lines, 50 tests)

### Modified Files
- **src/lexer.py** - Updated to use E1xx error codes
- **src/parser.py** - Updated to use E2xx error codes  
- **src/type_checker.py** - Updated to use E3xx error codes
- **src/vm.py** - Updated to use E4xx error codes
- **src/compiler.py** - Updated to use appropriate error codes

## Error Code Schema

### E1xx - Lexer Errors (10 codes)
| Code | Description | Used In |
|------|-------------|---------|
| E101 | Invalid character | lexer.py |
| E102 | Unterminated string | lexer.py |
| E103 | Invalid escape sequence | errors.py |
| E104 | Invalid number format | errors.py |
| E105 | Invalid indentation | lexer.py |
| E106 | Unexpected end of file | vm.py |
| E107 | Invalid Unicode character | errors.py |
| E108 | String exceeds maximum length | errors.py |
| E109 | Invalid identifier | errors.py |
| E110 | Unexpected character in number | errors.py |

### E2xx - Parser Errors (20 codes)
| Code | Description | Used In |
|------|-------------|---------|
| E201 | Unexpected token | parser.py |
| E202 | Expected token not found | parser.py |
| E203 | Missing closing delimiter | parser.py |
| E204 | Invalid syntax | compiler.py |
| E205 | Missing expression | errors.py |
| E206 | Unexpected end of input | errors.py |
| E207 | Invalid pattern | errors.py |
| E208 | Invalid type annotation | errors.py |
| E209 | Missing return type | parser.py |
| E210 | Invalid function signature | errors.py |
| E211 | Duplicate parameter name | errors.py |
| E212 | Invalid struct field | errors.py |
| E213 | Invalid enum variant | errors.py |
| E214 | Missing import path | errors.py |
| E215 | Invalid export statement | parser.py |
| E216 | Invalid lambda expression | errors.py |
| E217 | Invalid match arm | errors.py |
| E218 | Invalid dictionary key | parser.py |
| E219 | Invalid array literal | errors.py |
| E220 | Invalid generic type parameters | errors.py |

### E3xx - Type Errors (20 codes)
| Code | Description | Used In |
|------|-------------|---------|
| E301 | Type mismatch | type_checker.py |
| E302 | Undefined variable | type_checker.py |
| E303 | Undefined function | errors.py |
| E304 | Type inference failed | type_checker.py |
| E305 | Occurs check failed (recursive type) | type_checker.py |
| E306 | Function arity mismatch | type_checker.py |
| E307 | Invalid type annotation | errors.py |
| E308 | Cannot unify types | type_checker.py |
| E309 | Invalid operand type | type_checker.py, compiler.py |
| E310 | Invalid index type | errors.py |
| E311 | Invalid key type | errors.py |
| E312 | Missing type annotation | errors.py |
| E313 | Invalid return type | errors.py |
| E314 | Invalid generic type argument | errors.py |
| E315 | Invalid pattern type | errors.py |
| E316 | Invalid struct field access | errors.py |
| E317 | Invalid enum constructor | errors.py |
| E318 | Invalid type conversion | errors.py |
| E319 | Undefined type | errors.py |
| E320 | Incompatible types in operation | errors.py |

### E4xx - Runtime Errors (20 codes)
| Code | Description | Used In |
|------|-------------|---------|
| E401 | Division by zero | vm.py |
| E402 | Index out of bounds | vm.py |
| E403 | Key not found | vm.py |
| E404 | Undefined variable | errors.py |
| E405 | Undefined function | vm.py |
| E406 | Stack overflow | errors.py |
| E407 | Stack underflow | vm.py |
| E408 | Invalid operation | vm.py |
| E409 | Null reference | errors.py |
| E410 | Invalid argument type | vm.py |
| E411 | Wrong number of arguments | errors.py |
| E412 | Invalid iterator | errors.py |
| E413 | Module not found | vm.py |
| E414 | Circular import | errors.py |
| E415 | Memory limit exceeded | errors.py |
| E416 | Timeout exceeded | errors.py |
| E417 | Invalid bytecode | errors.py |
| E418 | Unknown opcode | vm.py |
| E419 | Call frame error | vm.py |
| E420 | Runtime assertion failed | errors.py |

## Error Classes

### Base Class
- **AICodeError** - Base class for all errors
  - `code`: Error code (e.g., "E101")
  - `message`: Human-readable message
  - `line`: Line number (1-indexed)
  - `column`: Column number (1-indexed)
  - `filename`: Source file name
  - `context`: Additional context
  - `stack_trace`: List of StackFrame objects

### Specific Error Classes
- **LexerError** - Lexer errors (E1xx)
- **ParserError** - Parser errors (E2xx)
- **TypeCheckError** - Type errors (E3xx)
- **RuntimeError** - Runtime errors (E4xx)
- **CompilerError** - Compilation errors (can be E2xx or E3xx)

## Helper Functions

### Lexer Helpers
```python
invalid_character(char, line, column, filename) -> LexerError
unterminated_string(line, column, filename) -> LexerError
invalid_escape_sequence(seq, line, column, filename) -> LexerError
invalid_indentation(line, column, filename) -> LexerError
```

### Parser Helpers
```python
unexpected_token(token, expected, line, column, filename, context) -> ParserError
expected_token(expected, found, line, column, filename) -> ParserError
missing_delimiter(delimiter, line, column, filename) -> ParserError
```

### Type Checker Helpers
```python
undefined_variable(name, line, column, filename) -> TypeCheckError
type_mismatch(expected, actual, line, column, filename) -> TypeCheckError
occurs_check(tvar, t, line, column, filename) -> TypeCheckError
```

### Runtime Helpers
```python
division_by_zero(line, column, filename) -> RuntimeError
index_out_of_bounds(index, length, line, column, filename) -> RuntimeError
key_not_found(key, line, column, filename) -> RuntimeError
undefined_function(name, line, column, filename) -> RuntimeError
stack_overflow(line, column, filename) -> RuntimeError
stack_underflow(line, column, filename) -> RuntimeError
```

### Utility Functions
```python
get_error_description(code: str) -> str
is_lexer_error(code: str) -> bool
is_parser_error(code: str) -> bool
is_type_error(code: str) -> bool
is_runtime_error(code: str) -> bool
```

## Example Usage

### Basic Error Creation
```python
from src.errors import LexerError, E101

# Create error with all context
err = LexerError(E101, "Invalid character: '$'", line=5, column=10, filename="test.aic")
print(err.code)      # "E101"
print(err.message)   # "Invalid character: '$'"
print(err.line)      # 5
print(err.column)    # 10
```

### Using Helper Functions
```python
from src.errors import invalid_character, type_mismatch

# Lexer error
err = invalid_character("$", line=5, column=10)

# Type error
err = type_mismatch("int", "str", line=20, column=5, filename="test.aic")
```

### Stack Traces
```python
from src.errors import RuntimeError, E401

err = RuntimeError(E401, "Division by zero")
err.add_frame("main", 10, 5, "main.aic")
err.add_frame("divide", 25, 3, "math.aic")

print(err)
# [E401] Division by zero
# Stack trace:
#   at main (main.aic:line 10, column 5)
#   at divide (math.aic:line 25, column 3)
```

### Error Handling in Components
```python
# In lexer.py
raise invalid_character(char, self.line, self.column)

# In parser.py
raise expected_token("IDENTIFIER", found_token, token.line, token.column)

# In type_checker.py
raise undefined_variable(var_name, expr.line, expr.column)

# In vm.py
raise stack_underflow()
```

## Test Results

All 50 error handling tests pass:
- TestErrorCodes: 4 tests ✓
- TestErrorDescriptions: 5 tests ✓
- TestBaseError: 5 tests ✓
- TestLexerErrors: 6 tests ✓
- TestParserErrors: 5 tests ✓
- TestTypeCheckErrors: 5 tests ✓
- TestRuntimeErrors: 7 tests ✓
- TestCompilerErrors: 2 tests ✓
- TestStackFrame: 3 tests ✓
- TestErrorCategorization: 4 tests ✓
- TestIntegration: 4 tests ✓

**Total: 50 tests passed**

## Benefits

1. **Standardized Codes**: Every error has a unique code for easy reference
2. **Rich Context**: Line numbers, column numbers, and filenames included
3. **Stack Traces**: Runtime errors include full call stack
4. **Programmatic Handling**: Error codes enable structured error handling
5. **Better Debugging**: Clear, formatted error messages
6. **Documentation**: 80 error codes with descriptions documented
7. **Extensibility**: Easy to add new error codes as needed
8. **Backward Compatibility**: Existing code continues to work

## Future Enhancements

- Add error recovery mechanisms
- Implement error code suggestions/fixes
- Add source code snippets to error context
- Implement error suppression/warning system
- Add localization support for error messages
