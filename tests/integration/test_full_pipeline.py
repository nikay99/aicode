"""
Integration Tests - Full pipeline tests
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lexer import tokenize as ascii_tokenize
from src.lexer_ai import tokenize as unicode_tokenize
from src.parser import parse
from src.compiler import BytecodeCompiler
from src.vm import VirtualMachine
from src.interpreter import Interpreter


class TestLexerToParser(unittest.TestCase):
    """Test Lexer → Parser integration"""

    def test_simple_variable(self):
        source = "let x = 42"
        program = parse(source)
        self.assertEqual(len(program.statements), 1)

    def test_function_definition(self):
        source = """
fn add(a, b)
  return a + b
"""
        program = parse(source)
        self.assertEqual(len(program.statements), 1)

    def test_unicode_variable(self):
        source = "𝕍 x ≔ 42"
        tokens = unicode_tokenize(source)
        self.assertTrue(len(tokens) > 0)

    def test_unicode_function(self):
        source = """
λ add(α, β)
  ← α + β
"""
        tokens = unicode_tokenize(source)
        self.assertTrue(len(tokens) > 0)


class TestParserToCompiler(unittest.TestCase):
    """Test Parser → Compiler integration"""

    def test_compile_variable(self):
        source = "let x = 42"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)
        self.assertEqual(len(module.functions), 1)

    def test_compile_function(self):
        source = """
fn add(a, b)
  return a + b
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)
        self.assertEqual(len(module.functions), 2)

    def test_compile_list(self):
        source = "let nums = [1, 2, 3]"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)

    def test_compile_dict(self):
        source = "let point = {x: 3, y: 4}"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)


class TestCompilerToVM(unittest.TestCase):
    """Test Compiler → VM integration"""

    def test_run_constant(self):
        source = "let x = 42"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        vm = VirtualMachine()
        vm.run(module)
        self.assertIn("x", vm.globals)
        self.assertEqual(vm.globals["x"], 42)

    def test_run_arithmetic(self):
        source = """
let x = 10
let y = 5
let sum = x + y
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        vm = VirtualMachine()
        vm.run(module)
        self.assertEqual(vm.globals["sum"], 15)

    def test_run_function(self):
        source = """
fn add(a, b)
  return a + b

let result = add(3, 4)
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        vm = VirtualMachine()
        vm.run(module)
        self.assertEqual(vm.globals["result"], 7)


class TestFullPipeline(unittest.TestCase):
    """Test full pipeline: Lexer → Parser → Compiler → VM"""

    def test_full_pipeline_println(self):
        interpreter = Interpreter()
        source = 'println("Hello, World!")'
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["Hello, World!"])

    def test_full_pipeline_arithmetic(self):
        interpreter = Interpreter()
        source = """
let x = 10
let y = 5
println(x + y)
println(x - y)
println(x * y)
println(x / y)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["15", "5", "50", "2.0"])

    def test_full_pipeline_function(self):
        interpreter = Interpreter()
        source = """
fn square(n)
  return n * n

println(square(5))
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["25"])

    def test_full_pipeline_lambda(self):
        interpreter = Interpreter()
        source = """
let double = fn(x): x * 2
println(double(5))
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["10"])

    def test_full_pipeline_list(self):
        interpreter = Interpreter()
        source = """
let nums = [1, 2, 3, 4, 5]
println(nums)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["[1, 2, 3, 4, 5]"])

    def test_full_pipeline_map(self):
        interpreter = Interpreter()
        source = """
let nums = [1, 2, 3]
let doubled = map(nums, fn(x): x * 2)
println(doubled)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["[2, 4, 6]"])

    def test_full_pipeline_filter(self):
        interpreter = Interpreter()
        source = """
let nums = [1, 2, 3, 4, 5, 6]
let evens = filter(nums, fn(x): x % 2 == 0)
println(evens)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["[2, 4, 6]"])

    def test_full_pipeline_reduce(self):
        interpreter = Interpreter()
        source = """
let nums = [1, 2, 3, 4, 5]
let sum = reduce(nums, fn(acc, x): acc + x, 0)
println(sum)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["15"])

    def test_full_pipeline_if(self):
        interpreter = Interpreter()
        source = """
let x = 10
if x > 5
  println("big")
else
  println("small")
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["big"])

    def test_full_pipeline_while(self):
        interpreter = Interpreter()
        source = """
let i = 0
let sum = 0
while i < 5
  sum = sum + i
  i = i + 1
println(sum)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["10"])

    def test_full_pipeline_for(self):
        interpreter = Interpreter()
        source = """
let sum = 0
for i in range(1, 6)
  sum = sum + i
println(sum)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["15"])

    def test_full_pipeline_dict(self):
        interpreter = Interpreter()
        source = """
let point = {x: 3, y: 4}
println(point.x + point.y)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["7"])

    def test_full_pipeline_match(self):
        interpreter = Interpreter()
        source = """
let x = 2
let name = match x
  1 -> "one"
  2 -> "two"
  _ -> "other"
println(name)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["two"])

    def test_full_pipeline_result_type(self):
        interpreter = Interpreter()
        source = """
fn divide(a, b)
  if b == 0
    return Err("Division by zero")
  else
    return Ok(a / b)

let result = divide(10, 2)
if is_ok(result)
  println("ok")
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["ok"])

    def test_full_pipeline_string_concat(self):
        interpreter = Interpreter()
        source = """
let greeting = "Hello"
let name = "World"
let message = greeting + ", " + name + "!"
println(message)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["Hello, World!"])

    def test_full_pipeline_comparison(self):
        interpreter = Interpreter()
        source = """
println(5 > 3)
println(5 < 3)
println(5 == 5)
println(5 != 3)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["True", "False", "True", "True"])

    def test_full_pipeline_logical(self):
        interpreter = Interpreter()
        source = """
println(true and true)
println(true and false)
println(true or false)
println(not false)
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["True", "False", "True", "True"])

    def test_full_pipeline_fizzbuzz(self):
        interpreter = Interpreter()
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

for i in range(1, 6)
  println(fizzbuzz(i))
"""
        program = parse(source)
        result = interpreter.interpret(program)
        expected = ["1", "2", "Fizz", "4", "Buzz"]
        self.assertEqual(result, expected)

    @unittest.skip("Nested functions not yet supported by compiler")
    def test_full_pipeline_nested_functions(self):
        interpreter = Interpreter()
        source = """
fn outer()
  fn inner()
    return 42
  return inner()

println(outer())
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["42"])

    @unittest.skip("Closures not yet supported by compiler")
    def test_full_pipeline_closure(self):
        interpreter = Interpreter()
        source = """
fn make_adder(n)
  fn adder(x)
    return x + n
  return adder

let add5 = make_adder(5)
println(add5(10))
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["15"])

    def test_full_pipeline_list_indexing(self):
        interpreter = Interpreter()
        source = """
let nums = [10, 20, 30]
println(nums[1])
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["20"])

    def test_full_pipeline_recursive_function(self):
        interpreter = Interpreter()
        source = """
fn factorial(n)
  if n <= 1
    return 1
  else
    return n * factorial(n - 1)

println(factorial(5))
"""
        program = parse(source)
        result = interpreter.interpret(program)
        self.assertEqual(result, ["120"])


class TestUnicodeIntegration(unittest.TestCase):
    """Test Unicode lexer with ASCII parser"""

    def test_unicode_arithmetic(self):
        tokens = unicode_tokenize("42 + 8")
        self.assertTrue(len(tokens) > 0)
        int_tokens = [t for t in tokens if t.type.name == "INT"]
        self.assertEqual(len(int_tokens), 2)


if __name__ == "__main__":
    unittest.main()
