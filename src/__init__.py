"""
AICode - KI-optimierte Programmiersprache
"""

from .lexer import tokenize, Token, TokenType
from .parser import parse
from .interpreter import interpret, Interpreter
from .ast_nodes import *

__version__ = "0.1.0"
__all__ = [
    "tokenize",
    "parse",
    "interpret",
    "Interpreter",
    "Token",
    "TokenType",
    "Program",
]
