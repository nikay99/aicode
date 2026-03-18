"""
Edge Case Tests - Tests for boundary conditions and unusual inputs
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.lexer import tokenize, TokenType, LexerError
from src.lexer_ai import tokenize as tokenize_ai
from src.parser import parse, ParseError
from src.interpreter import Interpreter


class TestEmptyInputs(unittest.TestCase):
    """Test empty and minimal inputs"""

    def test_empty_string(self):
        tokens = tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_whitespace_only(self):
        tokens = tokenize("   \n\t  ")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_empty_program(self):
        program = parse("")
        self.assertEqual(len(program.statements), 0)

    def test_only_newlines(self):
        tokens = tokenize("\n\n\n")
        self.assertTrue(len(tokens) > 0)


class TestVeryLongInputs(unittest.TestCase):
    """Test very long inputs"""

    def test_very_long_line(self):
        long_expr = "1 + " * 1000 + "1"
        tokens = tokenize(long_expr)
        self.assertTrue(len(tokens) > 1000)

    def test_very_long_string(self):
        long_string = '"' + "a" * 10000 + '"'
        tokens = tokenize(long_string)
        string_token = [t for t in tokens if t.type == TokenType.STRING][0]
        self.assertEqual(len(string_token.value), 10000)

    def test_very_long_identifier(self):
        long_id = "a" * 1000
        tokens = tokenize(long_id)
        self.assertEqual(len(tokens), 2)

    def test_many_statements(self):
        source = "\n".join([f"let x{i} = {i}" for i in range(1000)])
        program = parse(source)
        self.assertEqual(len(program.statements), 1000)


class TestDeepNesting(unittest.TestCase):
    """Test deeply nested structures"""

    def test_deeply_nested_parens(self):
        depth = 50
        source = "(" * depth + "42" + ")" * depth
        tokens = tokenize(source)
        self.assertEqual(len(tokens), depth * 2 + 2)

    def test_deeply_nested_lists(self):
        depth = 20
        source = "[" * depth + "1" + "]" * depth
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > depth * 2)

    def test_deeply_nested_ifs(self):
        depth = 10
        source = (
            "let x = "
            + "if true\n  " * depth
            + "1"
            + "\n"
            + ("else\n  " + "0" + "\n") * depth
        )
        program = parse(source)
        self.assertIsNotNone(program)

    def test_deeply_nested_functions(self):
        source = """
fn f1()
  fn f2()
    fn f3()
      fn f4()
        fn f5()
          return 42
        return f5()
      return f4()
    return f3()
  return f2()
println(f1())
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["42"])


class TestUnicodeEdgeCases(unittest.TestCase):
    """Test Unicode edge cases"""

    def test_unicode_in_string(self):
        source = 'println("Hello, 世界! 🌍")'
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["Hello, 世界! 🌍"])

    def test_mixed_ascii_unicode(self):
        source = """
let x = 42
𝕍 y = 100
println(x + y)
"""
        tokens = tokenize_ai(source)
        self.assertTrue(len(tokens) > 0)

    def test_unicode_whitespace(self):
        source = "let\u00a0x\u00a0=\u00a042"  # Non-breaking spaces
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestSpecialCharacters(unittest.TestCase):
    """Test special character handling"""

    def test_escaped_characters_in_string(self):
        source = r'"hello\nworld"'
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_tabs_in_string(self):
        source = '"hello\tworld"'
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestNumberEdgeCases(unittest.TestCase):
    """Test number edge cases"""

    def test_zero(self):
        source = "let x = 0"
        tokens = tokenize(source)
        int_tokens = [t for t in tokens if t.type == TokenType.INT]
        self.assertEqual(int_tokens[0].value, 0)

    def test_negative_zero(self):
        source = "let x = -0"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_very_large_int(self):
        source = "let x = 999999999999999999"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_very_small_float(self):
        source = "let x = 0.0000000001"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_very_large_float(self):
        source = "let x = 1e308"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_float_with_many_decimals(self):
        source = "let x = 3.14159265358979323846"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestStringEdgeCases(unittest.TestCase):
    """Test string edge cases"""

    def test_empty_string(self):
        source = 'let x = ""'
        tokens = tokenize(source)
        string_token = [t for t in tokens if t.type == TokenType.STRING][0]
        self.assertEqual(string_token.value, "")

    def test_single_char_string(self):
        source = 'let x = "a"'
        tokens = tokenize(source)
        string_token = [t for t in tokens if t.type == TokenType.STRING][0]
        self.assertEqual(string_token.value, "a")

    def test_string_with_quotes(self):
        source = r'"He said: \"Hello\""'
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestListEdgeCases(unittest.TestCase):
    """Test list edge cases"""

    def test_empty_list(self):
        source = "let x = []"
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(len(result), 0)

    def test_single_element_list(self):
        source = "let x = [1]"
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(len(result), 0)

    def test_very_long_list(self):
        source = "let x = [" + ", ".join(str(i) for i in range(1000)) + "]"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 2000)


class TestDictEdgeCases(unittest.TestCase):
    """Test dictionary edge cases"""

    def test_empty_dict(self):
        source = "let x = {}"
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(len(result), 0)

    def test_single_entry_dict(self):
        source = "let x = {a: 1}"
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(len(result), 0)


class TestFunctionEdgeCases(unittest.TestCase):
    """Test function edge cases"""

    def test_function_no_params(self):
        source = """
fn constant()
  return 42

println(constant())
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["42"])

    def test_function_many_params(self):
        source = """
fn many(a, b, c, d, e, f, g, h, i, j)
  return a + b + c + d + e + f + g + h + i + j

println(many(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["55"])

    def test_recursive_deep_call(self):
        source = """
fn sum(n)
  if n <= 0
    return 0
  else
    return n + sum(n - 1)

println(sum(100))
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["5050"])


class TestIndentationEdgeCases(unittest.TestCase):
    """Test indentation edge cases"""

    def test_inconsistent_indentation(self):
        source = """
fn test()
  x = 1
    y = 2
"""
        with self.assertRaises(Exception):
            parse(source)

    def test_tabs_and_spaces(self):
        source = "fn test()\n\tx = 1\n        y = 2"
        with self.assertRaises(Exception):
            parse(source)


class TestCommentEdgeCases(unittest.TestCase):
    """Test comment edge cases (if supported)"""

    def test_line_with_only_whitespace(self):
        source = """
let x = 1
   
let y = 2
"""
        program = parse(source)
        self.assertEqual(len(program.statements), 2)


class TestBooleanEdgeCases(unittest.TestCase):
    """Test boolean edge cases"""

    def test_true_and_false(self):
        source = """
println(true and false)
println(true or false)
println(not true)
println(not false)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["False", "True", "False", "True"])


class TestNullEdgeCases(unittest.TestCase):
    """Test null/None edge cases"""

    def test_null_value(self):
        source = "let x = null"
        tokens = tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestOperatorEdgeCases(unittest.TestCase):
    """Test operator edge cases"""

    def test_chained_comparison(self):
        source = """
let x = 5
println(1 < x and x < 10)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["True"])

    def test_multiple_operators(self):
        source = "let x = 1 + 2 + 3 + 4 + 5"
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
