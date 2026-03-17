"""
AICode Test Suite
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lexer import tokenize, TokenType
from src.parser import parse, ParseError
from src.interpreter import interpret, Interpreter, AICodeError


class TestLexer(unittest.TestCase):
    def test_simple_tokens(self):
        source = "let x = 42"
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.LET, types)
        self.assertIn(TokenType.IDENTIFIER, types)
        self.assertIn(TokenType.EQ, types)
        self.assertIn(TokenType.INT, types)
        self.assertIn(TokenType.EOF, types)

    def test_indentation(self):
        source = """fn test()
  x = 1
  y = 2
"""
        tokens = tokenize(source)
        indent_found = any(t.type == TokenType.INDENT for t in tokens)
        dedent_found = any(t.type == TokenType.DEDENT for t in tokens)
        self.assertTrue(indent_found)
        self.assertTrue(dedent_found)

    def test_string_literal(self):
        source = 'let s = "hello"'
        tokens = tokenize(source)
        string_token = [t for t in tokens if t.type == TokenType.STRING][0]
        self.assertEqual(string_token.value, "hello")


class TestParser(unittest.TestCase):
    def test_variable_declaration(self):
        source = "let x = 42"
        ast = parse(source)
        self.assertEqual(len(ast.statements), 1)
        self.assertEqual(ast.statements[0].name, "x")

    def test_function_declaration(self):
        source = """fn add(a, b)
  return a + b
"""
        ast = parse(source)
        self.assertEqual(len(ast.statements), 1)
        self.assertEqual(ast.statements[0].name, "add")
        self.assertEqual(len(ast.statements[0].params), 2)

    def test_if_expression(self):
        source = """if x > 0
  "positive"
else
  "negative"
"""
        ast = parse(source)
        self.assertEqual(len(ast.statements), 1)

    def test_match_expression(self):
        source = """match x
  1 -> "one"
  2 -> "two"
  _ -> "other"
"""
        ast = parse(source)
        self.assertEqual(len(ast.statements), 1)


class TestInterpreter(unittest.TestCase):
    def test_arithmetic(self):
        source = """
let x = 10
let y = 5
let sum = x + y
let diff = x - y
let prod = x * y
let quot = x / y
println(sum)
println(diff)
println(prod)
println(quot)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "15")
        self.assertEqual(result[1], "5")
        self.assertEqual(result[2], "50")
        self.assertEqual(result[3], "2.0")

    def test_functions(self):
        source = """
fn square(n)
  return n * n

let result = square(5)
println(result)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "25")

    def test_lambda(self):
        source = """
let double = fn(x): x * 2
let result = double(5)
println(result)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "10")

    def test_lists(self):
        source = """
let nums = [1, 2, 3, 4, 5]
let doubled = map(nums, fn(x): x * 2)
println(doubled)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "[2, 4, 6, 8, 10]")

    def test_filter(self):
        source = """
let nums = [1, 2, 3, 4, 5, 6]
let evens = filter(nums, fn(x): x % 2 == 0)
println(evens)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "[2, 4, 6]")

    def test_reduce(self):
        source = """
let nums = [1, 2, 3, 4, 5]
let sum = reduce(nums, fn(acc, x): acc + x, 0)
println(sum)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "15")

    def test_result_type(self):
        source = """
fn divide(a, b)
  if b == 0
    return Err("Division by zero")
  else
    return Ok(a / b)

let result1 = divide(10, 2)
let result2 = divide(10, 0)

if is_ok(result1)
  println("ok")
else
  println("err")

if is_err(result2)
  println("error")
else
  println("success")
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "ok")
        self.assertEqual(result[1], "error")

    def test_unwrap_or(self):
        source = """
fn divide(a, b)
  if b == 0
    return Err("Division by zero")
  else
    return Ok(a / b)

let result = divide(10, 0)
let value = unwrap_or(result, 0)
println(value)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "0")

    def test_match(self):
        source = """
let x = 2
let name = match x
  1 -> "one"
  2 -> "two"
  _ -> "other"
println(name)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "two")

    def test_for_loop(self):
        source = """
let sum = 0
for i in range(1, 6)
  sum = sum + i
println(sum)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "15")

    def test_while_loop(self):
        source = """
let i = 0
let sum = 0
while i < 5
  sum = sum + i
  i = i + 1
println(sum)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "10")

    def test_dictionaries(self):
        source = """
let point = {x: 3, y: 4}
let dist = point.x * point.x + point.y * point.y
println(dist)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "25")

    def test_string_concat(self):
        source = """
let greeting = "Hello"
let name = "World"
let message = greeting + ", " + name + "!"
println(message)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "Hello, World!")

    def test_comparison(self):
        source = """
println(5 > 3)
println(5 < 3)
println(5 == 5)
println(5 != 3)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "True")
        self.assertEqual(result[1], "False")
        self.assertEqual(result[2], "True")
        self.assertEqual(result[3], "True")

    def test_logical_operators(self):
        source = """
println(true and true)
println(true and false)
println(true or false)
println(not false)
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result[0], "True")
        self.assertEqual(result[1], "False")
        self.assertEqual(result[2], "True")
        self.assertEqual(result[3], "True")


class TestErrorHandling(unittest.TestCase):
    def test_undefined_variable(self):
        source = "println(undefined_var)"
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)

    def test_parse_error(self):
        source = "let x = "
        with self.assertRaises(ParseError):
            parse(source)

    def test_unwrap_on_err(self):
        source = """
let result = Err("error")
let value = unwrap(result)
"""
        interpreter = Interpreter()
        program = parse(source)
        with self.assertRaises(AICodeError):
            interpreter.interpret(program)


class TestFizzBuzz(unittest.TestCase):
    def test_fizzbuzz(self):
        source = """
fn fizzbuzz(n)
  if n % 3 == 0 and n % 5 == 0
    return "FizzBuzz"
  else if n % 3 == 0
    return "Fizz"
  else if n % 5 == 0
    return "Buzz"
  else
    return n

for i in range(1, 16)
  println(fizzbuzz(i))
"""
        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)

        expected = [
            "1",
            "2",
            "Fizz",
            "4",
            "Buzz",
            "Fizz",
            "7",
            "8",
            "Fizz",
            "Buzz",
            "11",
            "Fizz",
            "13",
            "14",
            "FizzBuzz",
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
