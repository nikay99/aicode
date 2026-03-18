"""
Error Tests - Comprehensive error handling tests
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.lexer import tokenize, TokenType
from src.parser import parse, ParseError
from src.interpreter import Interpreter, AICodeError


class TestLexerErrors(unittest.TestCase):
    """Test lexer error handling"""

    def test_unterminated_string(self):
        source = 'let x = "hello'
        with self.assertRaises(Exception):
            tokenize(source)

    def test_invalid_character(self):
        source = "let x = @"
        with self.assertRaises(Exception):
            tokenize(source)

    def test_invalid_number_format(self):
        source = "let x = 1.2.3"
        with self.assertRaises(Exception):
            tokenize(source)


class TestParserErrors(unittest.TestCase):
    """Test parser error handling"""

    def test_unexpected_token(self):
        source = "let x ="
        with self.assertRaises(Exception):
            parse(source)

    def test_missing_paren(self):
        source = "fn add(a, b"
        with self.assertRaises(Exception):
            parse(source)

    def test_missing_brace(self):
        source = "let x = {a: 1"
        with self.assertRaises(Exception):
            parse(source)

    def test_invalid_function_syntax(self):
        source = "fn"
        with self.assertRaises(Exception):
            parse(source)

    def test_invalid_if_syntax(self):
        source = "if"
        with self.assertRaises(Exception):
            parse(source)

    def test_invalid_match_syntax(self):
        source = "match"
        with self.assertRaises(Exception):
            parse(source)

    def test_invalid_for_syntax(self):
        source = "for"
        with self.assertRaises(Exception):
            parse(source)

    def test_invalid_while_syntax(self):
        source = "while"
        with self.assertRaises(Exception):
            parse(source)


class TestRuntimeErrors(unittest.TestCase):
    """Test runtime error handling"""

    def test_undefined_variable(self):
        source = "println(undefined_var)"
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_undefined_function(self):
        source = "undefined_function()"
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_type_mismatch_add(self):
        source = """
let x = "hello"
let y = 42
println(x + y)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_type_mismatch_multiply(self):
        source = """
let x = "hello"
let y = "world"
println(x * y)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_division_by_zero(self):
        source = """
let x = 10 / 0
println(x)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_index_out_of_bounds(self):
        source = """
let arr = [1, 2, 3]
println(arr[10])
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_negative_index(self):
        source = """
let arr = [1, 2, 3]
println(arr[-1])
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_unwrap_error(self):
        source = """
let result = Err("error")
let value = unwrap(result)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_call_non_function(self):
        source = """
let x = 42
x()
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_wrong_number_of_args(self):
        source = """
fn add(a, b)
  return a + b

add(1)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery"""

    def test_partial_program_after_error(self):
        source = """
let x = undefined
let y = 42
println(y)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)


class TestEdgeCaseErrors(unittest.TestCase):
    """Test edge case error handling"""

    def test_empty_list_access(self):
        source = """
let arr = []
println(arr[0])
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_null_access(self):
        source = """
let x = null
println(x.field)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_circular_reference(self):
        source = """
fn foo()
  return foo()

foo()
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)


class TestTypeErrors(unittest.TestCase):
    """Test type-related errors"""

    def test_string_indexing(self):
        source = """
let s = "hello"
println(s[0])
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_number_indexing(self):
        source = """
let x = 42
println(x[0])
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)


if __name__ == "__main__":
    unittest.main()
