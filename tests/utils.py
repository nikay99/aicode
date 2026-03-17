"""
Test utilities for AICode
"""

import sys
import io
from pathlib import Path
from typing import Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer import tokenize, Token, TokenType
from src.parser import parse, ParseError
from src.ast_nodes import Program
from src.compiler import BytecodeCompiler, CompilerError
from src.vm import VirtualMachine, VMError
from src.type_checker import type_check, TypeError


class TestOutput:
    """Captures output during test execution"""
    def __init__(self):
        self.outputs: List[str] = []
    
    def capture_print(self, *args, **kwargs):
        """Capture print output"""
        output = " ".join(str(arg) for arg in args)
        if kwargs.get('end', '\n') == '\n':
            self.outputs.append(output)
        else:
            if self.outputs:
                self.outputs[-1] += output
            else:
                self.outputs.append(output)
    
    def get_output(self) -> List[str]:
        return self.outputs
    
    def clear(self):
        self.outputs = []


def run_aicode(source: str, capture_output: bool = True) -> Any:
    """
    Run AICode source and return result
    
    Args:
        source: AICode source code
        capture_output: Whether to capture print statements
        
    Returns:
        Tuple of (result, output_list) if capture_output=True, else just result
    """
    # Parse
    program = parse(source)
    
    # Type check
    type_check(program)
    
    # Compile
    compiler = BytecodeCompiler()
    module = compiler.compile_program(program)
    
    # Execute
    vm = VirtualMachine()
    
    if capture_output:
        output = TestOutput()
        # Override built-in print functions
        original_print = vm.globals.get('print')
        original_println = vm.globals.get('println')
        vm.globals['print'] = lambda *args: output.capture_print(*args, end='')
        vm.globals['println'] = lambda *args: output.capture_print(*args, end='\n')
        
        try:
            vm.run(module)
        finally:
            # Restore original functions
            if original_print:
                vm.globals['print'] = original_print
            if original_println:
                vm.globals['println'] = original_println
        
        return output.get_output()
    else:
        vm.run(module)
        return None


def assert_output(source: str, expected: List[str]) -> None:
    """
    Assert that running source produces expected output
    
    Args:
        source: AICode source code
        expected: List of expected output lines
    """
    output = run_aicode(source)
    if output != expected:
        raise AssertionError(
            f"Expected output: {expected}\n"
            f"Actual output: {output}"
        )


def assert_error(source: str, error_class: type, error_message: Optional[str] = None) -> None:
    """
    Assert that running source raises specific error
    
    Args:
        source: AICode source code
        error_class: Expected exception type
        error_message: Optional substring to check in error message
    """
    try:
        run_aicode(source)
        raise AssertionError(f"Expected {error_class.__name__} but no exception was raised")
    except error_class as e:
        if error_message and error_message not in str(e):
            raise AssertionError(
                f"Expected error message containing '{error_message}', "
                f"but got: {str(e)}"
            )


def get_tokens(source: str) -> List[Token]:
    """Helper to get tokens from source"""
    return tokenize(source)


def get_token_types(source: str) -> List[TokenType]:
    """Helper to get token types from source"""
    return [t.type for t in tokenize(source)]


def count_token_occurrences(source: str, token_type: TokenType) -> int:
    """Count occurrences of a token type in source"""
    return sum(1 for t in tokenize(source) if t.type == token_type)
