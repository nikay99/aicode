"""
AICode Lexer - Tokenisiert den Sourcecode
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator, Any
from .errors import LexerError, invalid_character, unterminated_string, invalid_indentation, invalid_escape_sequence


class TokenType(Enum):
    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    NULL = auto()

    # Keywords
    LET = auto()
    CONST = auto()
    MUT = auto()
    FN = auto()
    IF = auto()
    ELSE = auto()
    MATCH = auto()
    FOR = auto()
    IN = auto()
    WHILE = auto()
    RETURN = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPORT = auto()
    EXPORT = auto()
    FROM = auto()
    AS = auto()

    # Types
    BOOL_TYPE = auto()
    INT_TYPE = auto()
    FLOAT_TYPE = auto()
    STR_TYPE = auto()
    LIST = auto()
    DICT = auto()
    OPTION = auto()
    RESULT = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    ARROW = auto()  # ->
    PIPE = auto()  # |>
    QMARK = auto()  # ?

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    BACKSLASH = auto()  # \ für Lambdas
    UNDERSCORE = auto()

    # Special
    IDENTIFIER = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        if self.value is not None and self.value != self.type.name.lower():
            return f"{self.type.name}({self.value})"
        return self.type.name


class Lexer:
    KEYWORDS = {
        "let": TokenType.LET,
        "const": TokenType.CONST,
        "mut": TokenType.MUT,
        "fn": TokenType.FN,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "match": TokenType.MATCH,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "while": TokenType.WHILE,
        "return": TokenType.RETURN,
        "struct": TokenType.STRUCT,
        "enum": TokenType.ENUM,
        "import": TokenType.IMPORT,
        "export": TokenType.EXPORT,
        "from": TokenType.FROM,
        "as": TokenType.AS,
        "bool": TokenType.BOOL_TYPE,
        "int": TokenType.INT_TYPE,
        "float": TokenType.FLOAT_TYPE,
        "str": TokenType.STR_TYPE,
        # Types are parsed as identifiers in context
        # "list": TokenType.LIST,
        # "dict": TokenType.DICT,
        # "option": TokenType.OPTION,
        # "result": TokenType.RESULT,
        "true": TokenType.BOOL,
        "false": TokenType.BOOL,
        "null": TokenType.NULL,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]  # Stack für Indent-Levels

    def error(self, msg: str, code: str = "E101"):
        raise LexerError(code, msg, self.line, self.column)

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

    def skip_whitespace(self):
        """Skippt whitespace außer Newlines (die sind signifikant)"""
        while self.peek() in " \t\r":
            self.advance()

    def skip_comment(self):
        """Skippt Kommentare (# bis Zeilenende)"""
        if self.peek() == "#":
            while self.peek() not in "\n\0":
                self.advance()

    def read_string(self) -> str:
        """Liest einen String ("...")"""
        quote = self.advance()  # Öffnende "
        result = []

        while self.peek() not in '"\n\0':
            char = self.advance()
            if char == "\\":
                # Escape-Sequenzen
                escape = self.advance()
                if escape == "n":
                    result.append("\n")
                elif escape == "t":
                    result.append("\t")
                elif escape == "\\":
                    result.append("\\")
                elif escape == '"':
                    result.append('"')
                else:
                    result.append(escape)
            else:
                result.append(char)

        if self.peek() != '"':
            raise unterminated_string(self.line, self.column)

        self.advance()  # Schließende "
        return "".join(result)

    def read_number(self) -> Token:
        """Liest eine Zahl (int oder float)"""
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
        """Liest einen Identifier oder Keyword"""
        start_line, start_col = self.line, self.column
        result = []

        while self.peek().isalnum() or self.peek() == "_":
            result.append(self.advance())

        value = "".join(result)
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)

        # Bool-Wert speichern
        if token_type == TokenType.BOOL:
            return Token(token_type, value == "true", start_line, start_col)

        # For operators (and, or, not), keep the value
        if token_type in (TokenType.AND, TokenType.OR, TokenType.NOT):
            return Token(token_type, value, start_line, start_col)

        return Token(
            token_type,
            value if token_type == TokenType.IDENTIFIER else None,
            start_line,
            start_col,
        )

    def handle_indentation(self) -> List[Token]:
        """Verarbeitet Indentation am Zeilenanfang"""
        tokens = []

        # Zähle Leerzeichen am Zeilenanfang
        indent = 0
        while self.peek() in " \t":
            if self.advance() == "\t":
                indent += 4  # Tab = 4 Spaces
            else:
                indent += 1

        # Skippe leere Zeilen und Kommentare
        if self.peek() in "\n#":
            return tokens  # Keine Indent-Tokens für leere Zeilen

        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            # Indent
            self.indent_stack.append(indent)
            tokens.append(Token(TokenType.INDENT, indent, self.line, self.column))
        elif indent < current_indent:
            # Dedents
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(
                    Token(
                        TokenType.DEDENT, self.indent_stack[-1], self.line, self.column
                    )
                )
            if indent != self.indent_stack[-1]:
                raise invalid_indentation(self.line, self.column)

        return tokens

    def tokenize(self) -> List[Token]:
        """Haupt-Tokenizer"""
        while True:
            self.skip_whitespace()
            self.skip_comment()

            char = self.peek()
            line, col = self.line, self.column

            # EOF
            if char == "\0":
                # Dedent am Ende
                while len(self.indent_stack) > 1:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, 0, line, col))
                self.tokens.append(Token(TokenType.EOF, None, line, col))
                break

            # Newline (startet möglicherweise Indentation)
            if char == "\n":
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, None, line, col))

                # Verarbeite Indentation am Zeilenanfang
                if self.peek() not in "\n#\0":  # Nicht bei leeren Zeilen
                    indent_tokens = self.handle_indentation()
                    self.tokens.extend(indent_tokens)
                continue

            # Strings
            if char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, col))
                continue

            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Identifiers
            if char.isalpha() or char == "_":
                self.tokens.append(self.read_identifier())
                continue

            # Two-character operators
            if char == "-" and self.peek(1) == ">":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, "->", line, col))
                continue

            if char == "|" and self.peek(1) == ">":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.PIPE, "|>", line, col))
                continue

            if char == "!" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NEQ, "!=", line, col))
                continue

            if char == "=" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQEQ, "==", line, col))
                continue

            if char == "<" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LTE, "<=", line, col))
                continue

            if char == ">" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GTE, ">=", line, col))
                continue

            # Single-character operators
            single_tokens = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "%": TokenType.PERCENT,
                "=": TokenType.EQ,
                "<": TokenType.LT,
                ">": TokenType.GT,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                ":": TokenType.COLON,
                ",": TokenType.COMMA,
                ".": TokenType.DOT,
                "\\": TokenType.BACKSLASH,
                "?": TokenType.QMARK,
                "_": TokenType.UNDERSCORE,
            }

            if char in single_tokens:
                self.advance()
                self.tokens.append(Token(single_tokens[char], char, line, col))
                continue

            # Unbekanntes Zeichen
            raise invalid_character(char, self.line, self.column)

        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Hilfsfunktion zum Tokenisieren"""
    lexer = Lexer(source)
    return lexer.tokenize()
