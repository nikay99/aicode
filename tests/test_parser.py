"""
Comprehensive Parser Tests
Tests for 100% coverage of src/parser.py
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import Parser, ParseError, parse
from src.lexer import tokenize, TokenType
import src.ast_nodes as ast


class TestParserLiterals(unittest.TestCase):
    """Test parsing literals"""
    
    def test_integer_literal(self):
        """Test integer literal"""
        result = parse("42")
        self.assertEqual(len(result.statements), 1)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ExprStmt)
        self.assertIsInstance(stmt.expr, ast.IntLiteral)
        self.assertEqual(stmt.expr.value, 42)
    
    def test_float_literal(self):
        """Test float literal"""
        result = parse("3.14")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.FloatLiteral)
        self.assertEqual(stmt.expr.value, 3.14)
    
    def test_string_literal(self):
        """Test string literal"""
        result = parse('"hello"')
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.StringLiteral)
        self.assertEqual(stmt.expr.value, "hello")
    
    def test_bool_literal_true(self):
        """Test boolean true"""
        result = parse("true")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BoolLiteral)
        self.assertEqual(stmt.expr.value, True)
    
    def test_bool_literal_false(self):
        """Test boolean false"""
        result = parse("false")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BoolLiteral)
        self.assertEqual(stmt.expr.value, False)
    
    def test_null_literal(self):
        """Test null literal"""
        result = parse("null")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.NullLiteral)


class TestParserIdentifiers(unittest.TestCase):
    """Test parsing identifiers"""
    
    def test_simple_identifier(self):
        """Test simple identifier"""
        result = parse("x")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.Identifier)
        self.assertEqual(stmt.expr.name, "x")
    
    def test_underscore_identifier(self):
        """Test underscore identifier"""
        result = parse("_private")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.Identifier)
        self.assertEqual(stmt.expr.name, "_private")


class TestParserBinaryOperations(unittest.TestCase):
    """Test parsing binary operations"""
    
    def test_addition(self):
        """Test addition"""
        result = parse("1 + 2")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "+")
    
    def test_subtraction(self):
        """Test subtraction"""
        result = parse("5 - 3")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "-")
    
    def test_multiplication(self):
        """Test multiplication"""
        result = parse("2 * 3")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "*")
    
    def test_division(self):
        """Test division"""
        result = parse("10 / 2")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "/")
    
    def test_modulo(self):
        """Test modulo"""
        result = parse("10 % 3")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "%")
    
    def test_precedence(self):
        """Test operator precedence"""
        result = parse("1 + 2 * 3")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "+")
        # Right side should be multiplication
        self.assertIsInstance(stmt.expr.right, ast.BinaryOp)
        self.assertEqual(stmt.expr.right.op, "*")
    
    def test_equality(self):
        """Test equality"""
        result = parse("x == y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "==")
    
    def test_inequality(self):
        """Test inequality"""
        result = parse("x != y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "!=")
    
    def test_less_than(self):
        """Test less than"""
        result = parse("x < y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "<")
    
    def test_greater_than(self):
        """Test greater than"""
        result = parse("x > y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, ">")
    
    def test_less_equal(self):
        """Test less or equal"""
        result = parse("x <= y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "<=")
    
    def test_greater_equal(self):
        """Test greater or equal"""
        result = parse("x >= y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, ">=")
    
    def test_and(self):
        """Test logical and"""
        result = parse("a and b")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "and")
    
    def test_or(self):
        """Test logical or"""
        result = parse("a or b")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)
        self.assertEqual(stmt.expr.op, "or")
    
    def test_pipe(self):
        """Test pipe operator"""
        result = parse("x |> f")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.PipeExpr)


class TestParserUnaryOperations(unittest.TestCase):
    """Test parsing unary operations"""
    
    def test_negation(self):
        """Test negation"""
        result = parse("-x")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.UnaryOp)
        self.assertEqual(stmt.expr.op, "-")
    
    def test_not(self):
        """Test logical not"""
        result = parse("not x")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.UnaryOp)
        self.assertEqual(stmt.expr.op, "not")
    
    def test_not_symbol(self):
        """Test logical not with !"""
        result = parse("!x")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.UnaryOp)
        self.assertEqual(stmt.expr.op, "!")


class TestParserLists(unittest.TestCase):
    """Test parsing lists"""
    
    def test_empty_list(self):
        """Test empty list"""
        result = parse("[]")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.ListExpr)
        self.assertEqual(len(stmt.expr.elements), 0)
    
    def test_list_with_elements(self):
        """Test list with elements"""
        result = parse("[1, 2, 3]")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.ListExpr)
        self.assertEqual(len(stmt.expr.elements), 3)
    
    def test_nested_list(self):
        """Test nested list"""
        result = parse("[[1, 2], [3, 4]]")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.ListExpr)
        self.assertEqual(len(stmt.expr.elements), 2)


class TestParserDicts(unittest.TestCase):
    """Test parsing dictionaries"""
    
    def test_empty_dict(self):
        """Test empty dict"""
        result = parse("{}")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.DictExpr)
        self.assertEqual(len(stmt.expr.entries), 0)
    
    def test_dict_with_entries(self):
        """Test dict with entries"""
        result = parse("{x: 1, y: 2}")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.DictExpr)
        self.assertEqual(len(stmt.expr.entries), 2)
    
    def test_dict_with_string_keys(self):
        """Test dict with string keys"""
        result = parse('{"key": "value"}')
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.DictExpr)


class TestParserLetStatements(unittest.TestCase):
    """Test parsing let statements"""
    
    def test_simple_let(self):
        """Test simple let"""
        result = parse("let x = 42")
        self.assertEqual(len(result.statements), 1)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.LetStmt)
        self.assertEqual(stmt.name, "x")
        self.assertFalse(stmt.mutable)
    
    def test_mutable_let(self):
        """Test mutable let"""
        result = parse("let mut x = 42")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.LetStmt)
        self.assertTrue(stmt.mutable)
    
    def test_let_with_type(self):
        """Test let with type annotation"""
        result = parse("let x: int = 42")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.LetStmt)
        self.assertIsNotNone(stmt.type)
    
    def test_let_with_expression(self):
        """Test let with expression value"""
        result = parse("let x = 1 + 2")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.value, ast.BinaryOp)


class TestParserConstStatements(unittest.TestCase):
    """Test parsing const statements"""
    
    def test_simple_const(self):
        """Test simple const"""
        result = parse("const PI = 3.14")
        self.assertEqual(len(result.statements), 1)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ConstStmt)
        self.assertEqual(stmt.name, "PI")


class TestParserFunctionDeclarations(unittest.TestCase):
    """Test parsing function declarations"""
    
    def test_simple_function(self):
        """Test simple function"""
        source = """fn add(a, b)
  return a + b
"""
        result = parse(source)
        self.assertEqual(len(result.statements), 1)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.FnStmt)
        self.assertEqual(stmt.name, "add")
        self.assertEqual(len(stmt.params), 2)
    
    def test_function_with_types(self):
        """Test function with type annotations"""
        source = """fn add(a: int, b: int) -> int
  return a + b
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.FnStmt)
        self.assertIsNotNone(stmt.return_type)
    
    def test_function_no_params(self):
        """Test function with no parameters"""
        source = """fn hello()
  println("hello")
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertEqual(len(stmt.params), 0)


class TestParserLambda(unittest.TestCase):
    """Test parsing lambda expressions"""
    
    def test_short_lambda(self):
        """Test short lambda form"""
        result = parse("\\x: x * 2")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.LambdaExpr)
        self.assertEqual(len(stmt.expr.params), 1)
    
    def test_long_lambda(self):
        """Test long lambda form"""
        result = parse("fn(x): x * 2")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.LambdaExpr)
        self.assertEqual(len(stmt.expr.params), 1)
    
    def test_multi_param_lambda(self):
        """Test multi-parameter lambda"""
        result = parse("\\x y: x + y")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.LambdaExpr)
        self.assertEqual(len(stmt.expr.params), 2)


class TestParserIfExpressions(unittest.TestCase):
    """Test parsing if expressions"""
    
    def test_simple_if(self):
        """Test simple if"""
        source = """if x > 0
  "positive"
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.IfExpr)
        self.assertIsNone(stmt.expr.else_branch)
    
    def test_if_else(self):
        """Test if-else"""
        source = """if x > 0
  "positive"
else
  "negative"
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.IfExpr)
        self.assertIsNotNone(stmt.expr.else_branch)
    
    def test_if_elif_else(self):
        """Test if-elif-else"""
        source = """if x > 0
  "positive"
else if x < 0
  "negative"
else
  "zero"
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.IfExpr)
        self.assertIsInstance(stmt.expr.else_branch, ast.IfExpr)


class TestParserMatchExpressions(unittest.TestCase):
    """Test parsing match expressions"""
    
    def test_simple_match(self):
        """Test simple match"""
        source = """match x
  1 -> "one"
  2 -> "two"
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.MatchExpr)
        self.assertEqual(len(stmt.expr.arms), 2)
    
    def test_match_with_wildcard(self):
        """Test match with wildcard"""
        source = """match x
  1 -> "one"
  _ -> "other"
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.MatchExpr)
        # Check last arm has wildcard pattern
        last_arm = stmt.expr.arms[-1]
        self.assertIsInstance(last_arm.pattern, ast.WildcardPattern)


class TestParserControlFlow(unittest.TestCase):
    """Test parsing control flow statements"""
    
    def test_for_loop(self):
        """Test for loop"""
        source = """for i in range(10)
  println(i)
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ForStmt)
        self.assertEqual(stmt.var, "i")
    
    def test_while_loop(self):
        """Test while loop"""
        source = """while x < 10
  x = x + 1
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.WhileStmt)
    
    def test_return_with_value(self):
        """Test return with value"""
        result = parse("return 42")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ReturnStmt)
        self.assertIsNotNone(stmt.value)
    
    def test_return_without_value(self):
        """Test return without value"""
        result = parse("return")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ReturnStmt)
        self.assertIsNone(stmt.value)


class TestParserStruct(unittest.TestCase):
    """Test parsing struct declarations"""
    
    def test_simple_struct(self):
        """Test simple struct"""
        source = """struct Point
  x: int
  y: int
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.StructStmt)
        self.assertEqual(stmt.name, "Point")
        self.assertEqual(len(stmt.fields), 2)


class TestParserEnum(unittest.TestCase):
    """Test parsing enum declarations"""
    
    def test_simple_enum(self):
        """Test simple enum"""
        source = """enum Color
  Red
  Green
  Blue
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.EnumStmt)
        self.assertEqual(stmt.name, "Color")
        self.assertEqual(len(stmt.variants), 3)
    
    def test_enum_with_data(self):
        """Test enum with data"""
        source = """enum Option
  Some(value: int)
  None
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.EnumStmt)
        # First variant should have fields
        self.assertIsNotNone(stmt.variants[0].fields)


class TestParserImport(unittest.TestCase):
    """Test parsing import statements"""
    
    def test_simple_import(self):
        """Test simple import"""
        result = parse("import math")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ImportStmt)
        self.assertEqual(stmt.module, "math")
    
    def test_import_with_alias(self):
        """Test import with alias"""
        result = parse("import math as m")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ImportStmt)
        self.assertEqual(stmt.alias, "m")
    
    def test_from_import(self):
        """Test from-import"""
        result = parse("from math import sin, cos")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.ImportStmt)
        self.assertEqual(stmt.names, ["sin", "cos"])


class TestParserExport(unittest.TestCase):
    """Test parsing export statements"""
    
    def test_export_function(self):
        """Test export function"""
        source = """export fn public_func()
  return 42
"""
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.FnStmt)
        self.assertTrue(stmt.exported)


class TestParserCalls(unittest.TestCase):
    """Test parsing function calls"""
    
    def test_simple_call(self):
        """Test simple call"""
        result = parse("foo()")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.CallExpr)
        self.assertEqual(len(stmt.expr.args), 0)
    
    def test_call_with_args(self):
        """Test call with arguments"""
        result = parse("foo(1, 2, 3)")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.CallExpr)
        self.assertEqual(len(stmt.expr.args), 3)
    
    def test_nested_call(self):
        """Test nested call"""
        result = parse("foo(bar(1))")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.CallExpr)
        self.assertIsInstance(stmt.expr.args[0], ast.CallExpr)


class TestParserIndexAndField(unittest.TestCase):
    """Test parsing index and field access"""
    
    def test_index_access(self):
        """Test index access"""
        result = parse("arr[0]")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.IndexExpr)
    
    def test_field_access(self):
        """Test field access"""
        result = parse("obj.field")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.FieldAccess)
        self.assertEqual(stmt.expr.field, "field")
    
    def test_chained_access(self):
        """Test chained access"""
        result = parse("obj.field[0].next")
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.FieldAccess)


class TestParserAssignment(unittest.TestCase):
    """Test parsing assignments"""
    
    def test_simple_assignment(self):
        """Test simple assignment"""
        result = parse("x = 42")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.AssignStmt)
        self.assertEqual(stmt.name, "x")
    
    def test_assignment_with_expression(self):
        """Test assignment with expression"""
        result = parse("x = y + 1")
        stmt = result.statements[0]
        self.assertIsInstance(stmt, ast.AssignStmt)
        self.assertIsInstance(stmt.value, ast.BinaryOp)


class TestParserErrors(unittest.TestCase):
    """Test parser error handling"""
    
    def test_unexpected_token(self):
        """Test unexpected token"""
        with self.assertRaises(ParseError):
            parse("let")
    
    def test_missing_colon_in_dict(self):
        """Test missing colon in dict"""
        with self.assertRaises(ParseError):
            parse("{key value}")
    
    def test_invalid_match_arm(self):
        """Test invalid match arm"""
        source = """match x
  -
"""
        with self.assertRaises(ParseError):
            parse(source)
    
    def test_export_without_declaration(self):
        """Test export without declaration"""
        with self.assertRaises(ParseError):
            parse("export x")


class TestParserComplex(unittest.TestCase):
    """Test complex parsing scenarios"""
    
    def test_multiple_statements(self):
        """Test multiple statements"""
        source = """let x = 1
let y = 2
let z = x + y
"""
        result = parse(source)
        self.assertEqual(len(result.statements), 3)
    
    def test_nested_function(self):
        """Test nested function"""
        source = """fn outer()
  fn inner()
    return 42
  return inner()
"""
        result = parse(source)
        self.assertEqual(len(result.statements), 1)
    
    def test_complex_expression(self):
        """Test complex expression"""
        source = "((1 + 2) * (3 - 4)) / 5"
        result = parse(source)
        stmt = result.statements[0]
        self.assertIsInstance(stmt.expr, ast.BinaryOp)


if __name__ == "__main__":
    unittest.main()
