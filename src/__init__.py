"""
AICode - A programming language optimized for LLMs with Unicode symbols

AICode uses mathematical Unicode symbols to achieve 40-60% token reduction
compared to Python while maintaining full programming capabilities.
"""

from .lexer import tokenize, Token, TokenType
from .parser import parse, ParseError
from .ast_nodes import *
from .interpreter import Interpreter, AICodeError
from .compiler import BytecodeCompiler, CompilerError
from .vm import VirtualMachine, VMError
from .type_checker import TypeChecker
from .bytecode import BytecodeModule, BytecodeFunction, Instruction, OpCode

__version__ = "0.1.0"
__all__ = [
    # Version
    "__version__",
    # Lexer
    "tokenize",
    "Token",
    "TokenType",
    # Parser
    "parse",
    "ParseError",
    # AST
    "Program",
    "Expr",
    "Stmt",
    # Interpreter
    "Interpreter",
    "AICodeError",
    # Compiler
    "BytecodeCompiler",
    "CompilerError",
    # VM
    "VirtualMachine",
    "VMError",
    # Type Checker
    "TypeChecker",
    # Bytecode
    "BytecodeModule",
    "BytecodeFunction",
    "Instruction",
    "OpCode",
]
