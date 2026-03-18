"""
Integration Tests for AICode
End-to-end tests combining lexer, parser, type checker, compiler, and VM
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.utils import run_aicode, assert_output


class TestIntegrationBasics(unittest.TestCase):
    """Test basic integration scenarios"""
    
    def test_hello_world(self):
        """Test hello world program"""
        source = 'println("Hello, World!")'
        output = run_aicode(source)
        self.assertEqual(output, ["Hello, World!"])
    
    def test_arithmetic(self):
        """Test arithmetic operations"""
        source = """println(1 + 2)
println(10 - 3)
println(4 * 5)
println(20 / 4)
println(17 % 5)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["3", "7", "20", "5.0", "2"])
    
    def test_variables(self):
        """Test variable declarations and usage"""
        source = """let x = 10
let y = 20
let sum = x + y
println(sum)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["30"])
    
    def test_mutable_variables(self):
        """Test mutable variables"""
        source = """let mut x = 10
x = 20
println(x)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["20"])


class TestIntegrationFunctions(unittest.TestCase):
    """Test function integration"""
    
    def test_simple_function(self):
        """Test simple function definition and call"""
        source = """fn greet()
  println("Hello!")

greet()
"""
        output = run_aicode(source)
        self.assertEqual(output, ["Hello!"])
    
    def test_function_with_params(self):
        """Test function with parameters"""
        source = """fn add(a, b)
  return a + b

println(add(3, 4))
"""
        output = run_aicode(source)
        self.assertEqual(output, ["7"])
    
    def test_function_with_return(self):
        """Test function with return value"""
        source = """fn square(n)
  return n * n

let result = square(5)
println(result)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["25"])
    
    def test_recursive_function(self):
        """Test recursive function"""
        source = """fn factorial(n)
  if n <= 1
    return 1
  else
    return n * factorial(n - 1)

println(factorial(5))
"""
        output = run_aicode(source)
        self.assertEqual(output, ["120"])
    
    def test_lambda_function(self):
        """Test lambda function"""
        source = """let double = fn(x): x * 2
println(double(5))
"""
        output = run_aicode(source)
        self.assertEqual(output, ["10"])


class TestIntegrationControlFlow(unittest.TestCase):
    """Test control flow integration"""
    
    def test_if_statement(self):
        """Test if statement"""
        source = """let x = 10
if x > 5
  println("big")
else
  println("small")
"""
        output = run_aicode(source)
        self.assertEqual(output, ["big"])
    
    def test_if_else_if(self):
        """Test if-else if chain"""
        source = """let x = 0
if x > 0
  println("positive")
else if x < 0
  println("negative")
else
  println("zero")
"""
        output = run_aicode(source)
        self.assertEqual(output, ["zero"])
    
    def test_while_loop(self):
        """Test while loop"""
        source = """let i = 0
while i < 3
  println(i)
  i = i + 1
"""
        output = run_aicode(source)
        self.assertEqual(output, ["0", "1", "2"])
    
    def test_for_loop(self):
        """Test for loop"""
        source = """for i in [1, 2, 3]
  println(i)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["1", "2", "3"])


class TestIntegrationLists(unittest.TestCase):
    """Test list integration"""
    
    def test_empty_list(self):
        """Test empty list"""
        source = "println([])"
        output = run_aicode(source)
        self.assertEqual(output, ["[]"])
    
    def test_list_creation(self):
        """Test list creation"""
        source = "println([1, 2, 3])"
        output = run_aicode(source)
        self.assertEqual(output, ["[1, 2, 3]"])
    
    def test_list_indexing(self):
        """Test list indexing"""
        source = """let nums = [10, 20, 30]
println(nums[0])
println(nums[1])
println(nums[2])
"""
        output = run_aicode(source)
        self.assertEqual(output, ["10", "20", "30"])
    
    def test_nested_list(self):
        """Test nested list"""
        source = "println([[1, 2], [3, 4]])"
        output = run_aicode(source)
        self.assertEqual(output, ["[[1, 2], [3, 4]]"])


class TestIntegrationDicts(unittest.TestCase):
    """Test dictionary integration"""
    
    def test_empty_dict(self):
        """Test empty dict"""
        source = "println({})"
        output = run_aicode(source)
        self.assertEqual(output, ["{}"])
    
    def test_dict_creation(self):
        """Test dict creation"""
        source = 'println({"a": 1, "b": 2})'
        output = run_aicode(source)
        self.assertIn(output[0], ["{'a': 1, 'b': 2}", "{'b': 2, 'a': 1}"])
    
    def test_dict_field_access(self):
        """Test dict field access"""
        source = """let person = {"name": "Alice", "age": 30}
println(person.name)
println(person.age)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["Alice", "30"])


class TestIntegrationHigherOrder(unittest.TestCase):
    """Test higher-order function integration"""
    
    def test_map_function(self):
        """Test map function"""
        source = """let nums = [1, 2, 3, 4]
let doubled = map(nums, fn(x): x * 2)
println(doubled)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["[2, 4, 6, 8]"])
    
    def test_filter_function(self):
        """Test filter function"""
        source = """let nums = [1, 2, 3, 4, 5, 6]
let evens = filter(nums, fn(x): x % 2 == 0)
println(evens)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["[2, 4, 6]"])
    
    def test_reduce_function(self):
        """Test reduce function"""
        source = """let nums = [1, 2, 3, 4, 5]
let sum = reduce(nums, fn(acc, x): acc + x, 0)
println(sum)
"""
        output = run_aicode(source)
        self.assertEqual(output, ["15"])
    
    def test_chained_operations(self):
        """Test chained operations"""
        source = """let nums = [1, 2, 3, 4, 5, 6]
let evens = filter(nums, fn(x): x % 2 == 0)
let doubled = map(evens, fn(x): x * 2)
let sum = reduce(doubled, fn(acc, x): acc + x, 0)
println(sum)
"""
        output = run_aicode(source)
        # evens = [2, 4, 6], doubled = [4, 8, 12], sum = 24
        self.assertEqual(output, ["24"])


class TestIntegrationFizzBuzz(unittest.TestCase):
    """Test FizzBuzz program"""
    
    def test_fizzbuzz(self):
        """Test FizzBuzz implementation"""
        source = """fn fizzbuzz(n)
  if n % 3 == 0 and n % 5 == 0
    return "FizzBuzz"
  else if n % 3 == 0
    return "Fizz"
  else if n % 5 == 0
    return "Buzz"
  else
    return n

for i in [1, 2, 3, 4, 5]
  println(fizzbuzz(i))
"""
        output = run_aicode(source)
        expected = ["1", "2", "Fizz", "4", "Buzz"]
        self.assertEqual(output, expected)


class TestIntegrationFibonacci(unittest.TestCase):
    """Test Fibonacci implementations"""
    
    def test_fibonacci_iterative(self):
        """Test iterative Fibonacci"""
        source = """fn fibonacci(n)
  if n <= 1
    return n
  let a = 0
  let b = 1
  let i = 2
  while i <= n
    let temp = a + b
    a = b
    b = temp
    i = i + 1
  return b

for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]
  println(fibonacci(i))
"""
        output = run_aicode(source)
        expected = ["0", "1", "1", "2", "3", "5", "8", "13", "21"]
        self.assertEqual(output, expected)
    
    def test_fibonacci_recursive(self):
        """Test recursive Fibonacci"""
        source = """fn fib(n)
  if n <= 1
    return n
  else
    return fib(n - 1) + fib(n - 2)

for i in [0, 1, 2, 3, 4, 5]
  println(fib(i))
"""
        output = run_aicode(source)
        expected = ["0", "1", "1", "2", "3", "5"]
        self.assertEqual(output, expected)


class TestIntegrationComparison(unittest.TestCase):
    """Test comparison operators"""
    
    def test_all_comparisons(self):
        """Test all comparison operators"""
        source = """println(5 == 5)
println(5 != 3)
println(3 < 5)
println(5 > 3)
println(3 <= 3)
println(5 >= 5)
"""
        output = run_aicode(source)
        expected = ["True", "True", "True", "True", "True", "True"]
        self.assertEqual(output, expected)


class TestIntegrationLogical(unittest.TestCase):
    """Test logical operators"""
    
    def test_logical_operators(self):
        """Test logical operators"""
        source = """println(true and true)
println(true and false)
println(false or true)
println(false or false)
println(not false)
println(not true)
"""
        output = run_aicode(source)
        expected = ["True", "False", "True", "False", "True", "False"]
        self.assertEqual(output, expected)


class TestIntegrationStrings(unittest.TestCase):
    """Test string operations"""
    
    def test_string_concat(self):
        """Test string concatenation"""
        source = """let greeting = "Hello"
let name = "World"
println(greeting + ", " + name + "!")
"""
        output = run_aicode(source)
        self.assertEqual(output, ["Hello, World!"])


class TestIntegrationComplex(unittest.TestCase):
    """Test complex programs"""
    
    def test_calculator(self):
        """Test simple calculator simulation"""
        source = """fn calculate(a, b, op)
  if op == "+"
    return a + b
  else if op == "-"
    return a - b
  else if op == "*"
    return a * b
  else if op == "/"
    return a / b
  else
    return 0

println(calculate(10, 5, "+"))
println(calculate(10, 5, "-"))
println(calculate(10, 5, "*"))
println(calculate(10, 5, "/"))
"""
        output = run_aicode(source)
        expected = ["15", "5", "50", "2.0"]
        self.assertEqual(output, expected)
    
    def test_sum_and_average(self):
        """Test sum and average calculation"""
        source = """fn sum_list(nums)
  let total = 0
  for n in nums
    total = total + n
  return total

fn average(nums)
  return sum_list(nums) / length(nums)

let nums = [1, 2, 3, 4, 5]
println(sum_list(nums))
"""
        output = run_aicode(source)
        self.assertEqual(output, ["15"])


if __name__ == "__main__":
    unittest.main()
