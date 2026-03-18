"""
AICode-AI - Programming language designed for LLMs
"""

# Legacy ASCII (v1 compatible)
from .lexer import tokenize, Token, TokenType
from .parser import parse
from .ast_nodes import *

# AI Unicode (v2)
from .lexer_ai import (
    tokenize as tokenize_ai,
    Token as TokenAI,
    TokenType as TokenTypeAI,
)
from .parser_ai import parse as parse_ai
from .ast_ai import *

# Interpreter (Compiler + VM)
from .interpreter import interpret, Interpreter

__version__ = "0.2.0"
__all__ = [
    # Legacy
    "tokenize",
    "parse",
    "Token",
    "TokenType",
    "Program",
    # AI
    "tokenize_ai",
    "parse_ai",
    "TokenAI",
    "TokenTypeAI",
    # Interpreter
    "interpret",
    "Interpreter",
]
