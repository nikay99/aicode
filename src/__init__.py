"""
AICode - KI-optimierte Programmiersprache
"""

from .lexer import tokenize, Token, TokenType
from .parser import parse
from .ast_nodes import *

__version__ = "0.1.0"
__all__ = [
    "tokenize",
    "parse",
    "Token",
    "TokenType",
    "Program",
]
