"""
AICode Error Handling System
Standardized error codes (E1xx-E4xx) with context support
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


# Error Code Definitions
E101 = "E101"
E102 = "E102"
E103 = "E103"
E104 = "E104"
E105 = "E105"
E106 = "E106"
E107 = "E107"
E108 = "E108"
E109 = "E109"
E110 = "E110"

E201 = "E201"
E202 = "E202"
E203 = "E203"
E204 = "E204"
E205 = "E205"
E206 = "E206"
E207 = "E207"
E208 = "E208"
E209 = "E209"
E210 = "E210"
E211 = "E211"
E212 = "E212"
E213 = "E213"
E214 = "E214"
E215 = "E215"
E216 = "E216"
E217 = "E217"
E218 = "E218"
E219 = "E219"
E220 = "E220"

E301 = "E301"
E302 = "E302"
E303 = "E303"
E304 = "E304"
E305 = "E305"
E306 = "E306"
E307 = "E307"
E308 = "E308"
E309 = "E309"
E310 = "E310"
E311 = "E311"
E312 = "E312"
E313 = "E313"
E314 = "E314"
E315 = "E315"
E316 = "E316"
E317 = "E317"
E318 = "E318"
E319 = "E319"
E320 = "E320"

E401 = "E401"
E402 = "E402"
E403 = "E403"
E404 = "E404"
E405 = "E405"
E406 = "E406"
E407 = "E407"
E408 = "E408"
E409 = "E409"
E410 = "E410"
E411 = "E411"
E412 = "E412"
E413 = "E413"
E414 = "E414"
E415 = "E415"
E416 = "E416"
E417 = "E417"
E418 = "E418"
E419 = "E419"
E420 = "E420"
E421 = "E421"
E422 = "E422"
E423 = "E423"
E424 = "E424"
E425 = "E425"
E426 = "E426"


# Error Messages Dictionary
ERROR_MESSAGES: Dict[str, str] = {
    # Lexer Errors (E1xx)
    E101: "Invalid character",
    E102: "Unterminated string",
    E103: "Invalid escape sequence",
    E104: "Invalid number format",
    E105: "Invalid indentation",
    E106: "Unexpected end of file",
    E107: "Invalid Unicode character",
    E108: "String exceeds maximum length",
    E109: "Invalid identifier",
    E110: "Unexpected character in number",
    # Parser Errors (E2xx)
    E201: "Unexpected token",
    E202: "Expected token not found",
    E203: "Missing closing delimiter",
    E204: "Invalid syntax",
    E205: "Missing expression",
    E206: "Unexpected end of input",
    E207: "Invalid pattern",
    E208: "Invalid type annotation",
    E209: "Missing return type",
    E210: "Invalid function signature",
    E211: "Duplicate parameter name",
    E212: "Invalid struct field",
    E213: "Invalid enum variant",
    E214: "Missing import path",
    E215: "Invalid export statement",
    E216: "Invalid lambda expression",
    E217: "Invalid match arm",
    E218: "Invalid dictionary key",
    E219: "Invalid array literal",
    E220: "Invalid generic type parameters",
    # Type Errors (E3xx)
    E301: "Type mismatch",
    E302: "Undefined variable",
    E303: "Undefined function",
    E304: "Type inference failed",
    E305: "Occurs check failed (recursive type)",
    E306: "Function arity mismatch",
    E307: "Invalid type annotation",
    E308: "Cannot unify types",
    E309: "Invalid operand type",
    E310: "Invalid index type",
    E311: "Invalid key type",
    E312: "Missing type annotation",
    E313: "Invalid return type",
    E314: "Invalid generic type argument",
    E315: "Invalid pattern type",
    E316: "Invalid struct field access",
    E317: "Invalid enum constructor",
    E318: "Invalid type conversion",
    E319: "Undefined type",
    E320: "Incompatible types in operation",
    # Runtime Errors (E4xx)
    E401: "Division by zero",
    E402: "Index out of bounds",
    E403: "Key not found",
    E404: "Undefined variable",
    E405: "Undefined function",
    E406: "Stack overflow",
    E407: "Stack underflow",
    E408: "Invalid operation",
    E409: "Null reference",
    E410: "Invalid argument type",
    E411: "Wrong number of arguments",
    E412: "Invalid iterator",
    E413: "Module not found",
    E414: "Circular import",
    E415: "Memory limit exceeded",
    E416: "Timeout exceeded",
    E417: "Invalid bytecode",
    E418: "Unknown opcode",
    E419: "Call frame error",
    E420: "Runtime assertion failed",
    E421: "Path traversal detected",
    E422: "File not found",
    E423: "Error reading file",
    E424: "Error writing file",
    E425: "File not found for deletion",
    E426: "Error deleting file",
}


@dataclass
class StackFrame:
    """Represents a single frame in the stack trace"""

    function: str
    line: int
    column: int
    filename: Optional[str] = None

    def __str__(self) -> str:
        loc = f"{self.filename}:" if self.filename else ""
        return f"  at {self.function} ({loc}line {self.line}, column {self.column})"


@dataclass
class AICodeError(Exception):
    """Base class for all AICode errors"""

    code: str
    message: str
    line: int = 0
    column: int = 0
    filename: Optional[str] = None
    context: Optional[str] = None
    stack_trace: List[StackFrame] = field(default_factory=list)

    def __post_init__(self):
        Exception.__init__(self, self.format_message())

    def format_message(self) -> str:
        """Format the error message with context"""
        parts = [f"[{self.code}] {self.message}"]

        if self.filename:
            parts.append(f" in {self.filename}")

        if self.line > 0:
            loc = f" at line {self.line}"
            if self.column > 0:
                loc += f", column {self.column}"
            parts.append(loc)

        result = "".join(parts)

        if self.context:
            result += f"\n  Context: {self.context}"

        if self.stack_trace:
            result += "\nStack trace:\n" + "\n".join(
                str(frame) for frame in self.stack_trace
            )

        return result

    def __str__(self) -> str:
        return self.format_message()

    def add_frame(
        self,
        function: str,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
    ):
        """Add a frame to the stack trace"""
        self.stack_trace.append(StackFrame(function, line, column, filename))

    def with_context(
        self,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ) -> "AICodeError":
        """Return a new error with additional context"""
        return AICodeError(
            code=self.code,
            message=self.message,
            line=line if line > 0 else self.line,
            column=column if column > 0 else self.column,
            filename=filename or self.filename,
            context=context or self.context,
            stack_trace=self.stack_trace.copy(),
        )


class LexerError(AICodeError):
    """Error during lexical analysis (E1xx)"""

    def __init__(
        self,
        code: str,
        message: Optional[str] = None,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ):
        if message is None:
            message = ERROR_MESSAGES.get(code, "Unknown lexer error")
        super().__init__(code, message, line, column, filename, context)


class ParserError(AICodeError):
    """Error during parsing (E2xx)"""

    def __init__(
        self,
        code: str,
        message: Optional[str] = None,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ):
        if message is None:
            message = ERROR_MESSAGES.get(code, "Unknown parser error")
        super().__init__(code, message, line, column, filename, context)


class TypeCheckError(AICodeError):
    """Error during type checking (E3xx)"""

    def __init__(
        self,
        code: str,
        message: Optional[str] = None,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_type: Optional[str] = None,
    ):
        if message is None:
            message = ERROR_MESSAGES.get(code, "Unknown type error")

        if expected_type and actual_type:
            message += f": expected '{expected_type}', found '{actual_type}'"
        elif expected_type:
            message += f": expected '{expected_type}'"
        elif actual_type:
            message += f": found '{actual_type}'"

        super().__init__(code, message, line, column, filename, context)


class RuntimeError(AICodeError):
    """Error during execution (E4xx)"""

    def __init__(
        self,
        code: str,
        message: Optional[str] = None,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ):
        if message is None:
            message = ERROR_MESSAGES.get(code, "Unknown runtime error")
        super().__init__(code, message, line, column, filename, context)


class CompilerError(AICodeError):
    """Error during compilation (can be E2xx or E3xx depending on phase)"""

    def __init__(
        self,
        code: str,
        message: Optional[str] = None,
        line: int = 0,
        column: int = 0,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ):
        if message is None:
            message = ERROR_MESSAGES.get(code, "Unknown compiler error")
        super().__init__(code, message, line, column, filename, context)


# Helper functions for creating common errors
def invalid_character(
    char: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> LexerError:
    """Create an invalid character error"""
    return LexerError(E101, f"Invalid character: '{char}'", line, column, filename)


def unterminated_string(
    line: int = 0, column: int = 0, filename: Optional[str] = None
) -> LexerError:
    """Create an unterminated string error"""
    return LexerError(E102, "Unterminated string literal", line, column, filename)


def invalid_escape_sequence(
    seq: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> LexerError:
    """Create an invalid escape sequence error"""
    return LexerError(
        E103, f"Invalid escape sequence: '\\{seq}'", line, column, filename
    )


def invalid_indentation(
    line: int = 0, column: int = 0, filename: Optional[str] = None
) -> LexerError:
    """Create an invalid indentation error"""
    return LexerError(E105, "Invalid indentation", line, column, filename)


def unexpected_token(
    token: str,
    expected: Optional[str] = None,
    line: int = 0,
    column: int = 0,
    filename: Optional[str] = None,
    context: Optional[str] = None,
) -> ParserError:
    """Create an unexpected token error"""
    msg = f"Unexpected token: '{token}'"
    if expected:
        msg += f", expected: {expected}"
    return ParserError(E201, msg, line, column, filename, context)


def expected_token(
    expected: str,
    found: str,
    line: int = 0,
    column: int = 0,
    filename: Optional[str] = None,
) -> ParserError:
    """Create an expected token not found error"""
    return ParserError(
        E202, f"Expected '{expected}', found '{found}'", line, column, filename
    )


def missing_delimiter(
    delimiter: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> ParserError:
    """Create a missing delimiter error"""
    return ParserError(
        E203, f"Missing closing delimiter: '{delimiter}'", line, column, filename
    )


def undefined_variable(
    name: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> TypeCheckError:
    """Create an undefined variable error"""
    return TypeCheckError(E302, f"Undefined variable: '{name}'", line, column, filename)


def type_mismatch(
    expected: str,
    actual: str,
    line: int = 0,
    column: int = 0,
    filename: Optional[str] = None,
) -> TypeCheckError:
    """Create a type mismatch error"""
    return TypeCheckError(
        E301,
        f"Type mismatch: expected '{expected}', found '{actual}'",
        line,
        column,
        filename,
        expected_type=expected,
        actual_type=actual,
    )


def occurs_check(
    tvar: str, t: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> TypeCheckError:
    """Create an occurs check error"""
    return TypeCheckError(
        E305, f"Occurs check failed: {tvar} occurs in {t}", line, column, filename
    )


def division_by_zero(
    line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create a division by zero error"""
    return RuntimeError(E401, "Division by zero", line, column, filename)


def index_out_of_bounds(
    index: int,
    length: int,
    line: int = 0,
    column: int = 0,
    filename: Optional[str] = None,
) -> RuntimeError:
    """Create an index out of bounds error"""
    return RuntimeError(
        E402, f"Index {index} out of bounds for length {length}", line, column, filename
    )


def key_not_found(
    key: Any, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create a key not found error"""
    return RuntimeError(E403, f"Key not found: {key}", line, column, filename)


def undefined_function(
    name: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create an undefined function error"""
    return RuntimeError(E405, f"Undefined function: '{name}'", line, column, filename)


def stack_overflow(
    line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create a stack overflow error"""
    return RuntimeError(E406, "Stack overflow", line, column, filename)


def stack_underflow(
    line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create a stack underflow error"""
    return RuntimeError(E407, "Stack underflow", line, column, filename)


def path_traversal_detected(
    filepath: str, line: int = 0, column: int = 0, filename: Optional[str] = None
) -> RuntimeError:
    """Create a path traversal error"""
    return RuntimeError(
        E421, f"Path traversal detected: {filepath}", line, column, filename
    )


def get_error_description(code: str) -> str:
    """Get the description for an error code"""
    return ERROR_MESSAGES.get(code, "Unknown error")


def is_lexer_error(code: str) -> bool:
    """Check if error code is a lexer error"""
    return code.startswith("E1")


def is_parser_error(code: str) -> bool:
    """Check if error code is a parser error"""
    return code.startswith("E2")


def is_type_error(code: str) -> bool:
    """Check if error code is a type error"""
    return code.startswith("E3")


def is_runtime_error(code: str) -> bool:
    """Check if error code is a runtime error"""
    return code.startswith("E4")
