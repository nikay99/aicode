"""
AICode-AI Lexer - Unicode Mathematical Tokenizer
Optimized for LLM token efficiency
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator, Any
import unicodedata


class TokenType(Enum):
    # Single Unicode Character Tokens
    # Declarations
    VAR = auto()  # 𝕍 (U+1D54D) - Variable
    CONST = auto()  # 𝔠 (U+1D520) - Constant
    MUT = auto()  # μ (U+03BC) - Mutable
    FUNC = auto()  # λ (U+03BB) - Function

    # Control Flow
    IF = auto()  # ? (U+003F) - If
    ELSE = auto()  # : (U+003A) - Else
    MATCH = auto()  # ∼ (U+223C) - Match
    FOR = auto()  # ∀ (U+2200) - For
    IN = auto()  # ∈ (U+2208) - In
    WHILE = auto()  # ⟲ (U+27F2) - While
    RETURN = auto()  # ← (U+2190) - Return

    # Types
    INT_TYPE = auto()  # ℤ (U+2124) - Integer
    FLOAT_TYPE = auto()  # ℝ (U+211D) - Real/Float
    STR_TYPE = auto()  # 𝕊 (U+1D54A) - String
    BOOL_TYPE = auto()  # 𝔹 (U+1D539) - Boolean
    LIST_TYPE = auto()  # 𝕃 (U+1D543) - List
    DICT_TYPE = auto()  # 𝔻 (U+1D53B) - Dict

    # Data Structures
    STRUCT = auto()  # Σ (U+03A3) - Struct
    ENUM = auto()  # 𝔼 (U+1D53C) - Enum

    # Module System
    IMPORT = auto()  # ↓ (U+2193) - Import
    EXPORT = auto()  # ↑ (U+2191) - Export

    # Logic
    AND = auto()  # ∧ (U+2227) - And
    OR = auto()  # ∨ (U+2228) - Or
    NOT = auto()  # ¬ (U+00AC) - Not

    # Literals
    BOOL = auto()  # ⊤ or ⊥ (True/False)
    NULL = auto()  # ∅ (U+2205) - Null/Empty

    # Operators
    ASSIGN = auto()  # ≔ (U+2254) - Assignment
    ARROW = auto()  # → (U+2192) - Return type / implication
    PIPE = auto()  # ▷ (U+25B7) - Pipe
    EQ = auto()  # = (U+003D) - Equal
    NEQ = auto()  # ≠ (U+2260) - Not equal
    LT = auto()  # < (U+003C) - Less than
    GT = auto()  # > (U+003E) - Greater than
    LTE = auto()  # ≤ (U+2264) - Less or equal
    GTE = auto()  # ≥ (U+2265) - Greater or equal
    PLUS = auto()  # + (U+002B) - Plus
    MINUS = auto()  # - (U+002D) - Minus
    STAR = auto()  # * (U+002A) - Multiply
    SLASH = auto()  # / (U+002F) - Divide
    PERCENT = auto()  # % (U+0025) - Modulo

    # Functional
    MAP = auto()  # ∀ (reuse FOR symbol in context)
    FILTER = auto()  # ∃ (U+2203) - Exists/Filter
    REDUCE = auto()  # ∑ (U+2211) - Sum/Reduce
    COMPOSE = auto()  # ∘ (U+2218) - Compose

    # Separators
    COMMA = auto()  # ,
    DOT = auto()  # .
    SEMICOLON = auto()  # ;

    # Brackets
    LPAREN = auto()  # ( (U+0028)
    RPAREN = auto()  # ) (U+0029)
    LBRACKET = auto()  # [ (U+005B)
    RBRACKET = auto()  # ] (U+005D)
    LBRACE = auto()  # { (U+007B)
    RBRACE = auto()  # } (U+007D)
    LANGLE = auto()  # ⟨ (U+27E8) - Application
    RANGLE = auto()  # ⟩ (U+27E9)

    # Values
    INT = auto()  # Integer literal
    FLOAT = auto()  # Float literal
    STRING = auto()  # String literal
    IDENTIFIER = auto()  # Greek letters or indexed vars

    # Whitespace
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


# Unicode to Token mapping
UNICODE_TOKENS = {
    # Declarations
    "\U0001d54d": TokenType.VAR,  # 𝕍
    "\U0001d520": TokenType.CONST,  # 𝔠
    "\u03bc": TokenType.MUT,  # μ
    "\u03bb": TokenType.FUNC,  # λ
    # Control Flow
    "?": TokenType.IF,
    ":": TokenType.ELSE,
    "\u223c": TokenType.MATCH,  # ∼
    "\u2200": TokenType.FOR,  # ∀
    "\u2208": TokenType.IN,  # ∈
    "\u27f2": TokenType.WHILE,  # ⟲
    "\u2190": TokenType.RETURN,  # ←
    # Types
    "\u2124": TokenType.INT_TYPE,  # ℤ
    "\u211d": TokenType.FLOAT_TYPE,  # ℝ
    "\U0001d54a": TokenType.STR_TYPE,  # 𝕊
    "\U0001d539": TokenType.BOOL_TYPE,  # 𝔹
    "\U0001d543": TokenType.LIST_TYPE,  # 𝕃
    "\U0001d53b": TokenType.DICT_TYPE,  # 𝔻
    # Data Structures
    "\u03a3": TokenType.STRUCT,  # Σ
    "\U0001d53c": TokenType.ENUM,  # 𝔼
    # Modules
    "\u2193": TokenType.IMPORT,  # ↓
    "\u2191": TokenType.EXPORT,  # ↑
    # Logic
    "\u2227": TokenType.AND,  # ∧
    "\u2228": TokenType.OR,  # ∨
    "\u00ac": TokenType.NOT,  # ¬
    # Literals - both map to BOOL
    "\u22a4": TokenType.BOOL,  # ⊤ (True)
    "\u22a5": TokenType.BOOL,  # ⊥ (False)
    "\u2205": TokenType.NULL,  # ∅
    # Operators
    "\u2254": TokenType.ASSIGN,  # ≔
    "\u2192": TokenType.ARROW,  # →
    "\u25b7": TokenType.PIPE,  # ▷
    "=": TokenType.EQ,
    "\u2260": TokenType.NEQ,  # ≠
    "<": TokenType.LT,
    ">": TokenType.GT,
    "\u2264": TokenType.LTE,  # ≤
    "\u2265": TokenType.GTE,  # ≥
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    # Functional
    "\u2203": TokenType.FILTER,  # ∃
    "\u2211": TokenType.REDUCE,  # ∑
    "\u2218": TokenType.COMPOSE,  # ∘
    # Separators
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    # Brackets
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "\u27e8": TokenType.LANGLE,  # ⟨
    "\u27e9": TokenType.RANGLE,  # ⟩
}


# Greek letters for parameters
GREEK_LETTERS = set("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ")


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        if self.value is not None:
            return f"{self.type.name}({self.value})"
        return self.type.name


class Lexer:
    """Unicode-aware lexer for AICode-AI"""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]

    def error(self, msg: str):
        raise SyntaxError(f"E001:{self.line}:{self.column}")

    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.source):
            return "\0"
        return self.source[pos]

    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def skip_whitespace_inline(self):
        """Skip whitespace except newlines"""
        while self.peek() in " \t\r":
            self.advance()

    def read_string(self) -> str:
        """Read a string literal (no escape sequences, simplified)"""
        quote = self.advance()  # Opening quote
        result = []

        while self.peek() not in '"\n\0':
            result.append(self.advance())

        if self.peek() != '"':
            self.error("E002")  # Unterminated string

        self.advance()  # Closing quote
        return "".join(result)

    def read_number(self) -> Token:
        """Read integer or float"""
        start_line, start_col = self.line, self.column
        result = []
        is_float = False

        while self.peek().isdigit():
            result.append(self.advance())

        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            result.append(self.advance())  # .
            while self.peek().isdigit():
                result.append(self.advance())

        value = "".join(result)

        if is_float:
            return Token(TokenType.FLOAT, float(value), start_line, start_col)
        else:
            return Token(TokenType.INT, int(value), start_line, start_col)

    def read_identifier(self) -> Token:
        """Read identifier (Greek letters or alphanumeric)"""
        start_line, start_col = self.line, self.column
        result = []

        # First char
        char = self.peek()
        if char in GREEK_LETTERS or char.isalpha() or char == "_":
            result.append(self.advance())
        else:
            self.error("E003")  # Invalid identifier

        # Rest
        while (
            self.peek() in GREEK_LETTERS
            or self.peek().isalnum()
            or self.peek() in "_₀₁₂₃₄₅₆₇₈₉"
        ):
            result.append(self.advance())

        value = "".join(result)
        return Token(TokenType.IDENTIFIER, value, start_line, start_col)

    def handle_indentation(self) -> List[Token]:
        """Handle Python-style indentation"""
        tokens = []

        # Count spaces at line start
        indent = 0
        while self.peek() in " \t":
            if self.advance() == "\t":
                indent += 4
            else:
                indent += 1

        # Skip empty lines and comments (but we don't have comments!)
        if self.peek() in "\n\0":
            return tokens  # Empty line

        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            self.indent_stack.append(indent)
            tokens.append(Token(TokenType.INDENT, indent, self.line, self.column))
        elif indent < current_indent:
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(
                    Token(
                        TokenType.DEDENT, self.indent_stack[-1], self.line, self.column
                    )
                )
            if indent != self.indent_stack[-1]:
                self.error("E004")  # Invalid dedent

        return tokens

    def tokenize(self) -> List[Token]:
        """Main tokenizer"""
        while True:
            self.skip_whitespace_inline()

            char = self.peek()
            line, col = self.line, self.column

            # EOF
            if char == "\0":
                # Dedent at end
                while len(self.indent_stack) > 1:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, 0, line, col))
                self.tokens.append(Token(TokenType.EOF, None, line, col))
                break

            # Newline (triggers indentation check)
            if char == "\n":
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, None, line, col))
                indent_tokens = self.handle_indentation()
                self.tokens.extend(indent_tokens)
                continue

            # String literal
            if char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, col))
                continue

            # Number
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Unicode tokens
            if char in UNICODE_TOKENS:
                token_type = UNICODE_TOKENS[char]
                # Check for boolean values (both ⊤ and ⊥ map to BOOL)
                if token_type == TokenType.BOOL:
                    self.advance()
                    value = True if char == "\u22a4" else False  # ⊤ = True, ⊥ = False
                    self.tokens.append(Token(TokenType.BOOL, value, line, col))
                elif token_type == TokenType.NULL:
                    self.advance()
                    self.tokens.append(Token(TokenType.NULL, None, line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(token_type, char, line, col))
                continue

            # Greek letters or identifiers
            if char in GREEK_LETTERS or char.isalpha() or char == "_":
                self.tokens.append(self.read_identifier())
                continue

            # Unknown character
            self.error("E005")  # Unknown character

        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Helper function to tokenize source"""
    lexer = Lexer(source)
    return lexer.tokenize()
