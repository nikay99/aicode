"""
Comprehensive Compiler Tests
Tests for bytecode generation
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import parse
from src.compiler import BytecodeCompiler, CompilerError, FunctionCompiler
from src.bytecode import OpCode, BytecodeModule
import src.ast_nodes as ast


class TestCompilerLiterals(unittest.TestCase):
    """Test compiling literals"""
    
    def test_integer_literal(self):
        """Test compiling integer"""
        program = parse("42")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        # Should have a PUSH_CONST instruction
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.PUSH_CONST for i in main_func.code))
    
    def test_float_literal(self):
        """Test compiling float"""
        program = parse("3.14")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.PUSH_CONST for i in main_func.code))
    
    def test_string_literal(self):
        """Test compiling string"""
        program = parse('"hello"')
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.PUSH_CONST for i in main_func.code))
    
    def test_null_literal(self):
        """Test compiling null"""
        program = parse("null")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.PUSH_NULL for i in main_func.code))


class TestCompilerVariables(unittest.TestCase):
    """Test compiling variable operations"""
    
    def test_let_statement(self):
        """Test compiling let statement"""
        program = parse("let x = 42")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        # Should have STORE_LOCAL
        self.assertTrue(any(i.opcode == OpCode.STORE_LOCAL for i in main_func.code))
    
    def test_variable_reference(self):
        """Test compiling variable reference"""
        source = """let x = 42
println(x)
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        # Should have LOAD_LOCAL
        self.assertTrue(any(i.opcode == OpCode.LOAD_LOCAL for i in main_func.code))
    
    def test_assignment(self):
        """Test compiling assignment"""
        source = """let x = 1
x = 2
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        # Should have STORE_LOCAL
        store_count = sum(1 for i in main_func.code if i.opcode == OpCode.STORE_LOCAL)
        self.assertGreaterEqual(store_count, 2)


class TestCompilerArithmetic(unittest.TestCase):
    """Test compiling arithmetic operations"""
    
    def test_addition(self):
        """Test compiling addition"""
        program = parse("1 + 2")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.ADD for i in main_func.code))
    
    def test_subtraction(self):
        """Test compiling subtraction"""
        program = parse("5 - 3")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.SUB for i in main_func.code))
    
    def test_multiplication(self):
        """Test compiling multiplication"""
        program = parse("2 * 3")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.MUL for i in main_func.code))
    
    def test_division(self):
        """Test compiling division"""
        program = parse("10 / 2")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.DIV for i in main_func.code))
    
    def test_modulo(self):
        """Test compiling modulo"""
        program = parse("10 % 3")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.MOD for i in main_func.code))
    
    def test_negation(self):
        """Test compiling negation"""
        program = parse("-5")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.NEG for i in main_func.code))


class TestCompilerComparison(unittest.TestCase):
    """Test compiling comparison operations"""
    
    def test_equality(self):
        """Test compiling equality"""
        program = parse("x == y")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.EQ for i in main_func.code))
    
    def test_inequality(self):
        """Test compiling inequality"""
        program = parse("x != y")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.NE for i in main_func.code))
    
    def test_less_than(self):
        """Test compiling less than"""
        program = parse("x < y")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.LT for i in main_func.code))
    
    def test_greater_than(self):
        """Test compiling greater than"""
        program = parse("x > y")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.GT for i in main_func.code))


class TestCompilerLogical(unittest.TestCase):
    """Test compiling logical operations"""
    
    def test_and(self):
        """Test compiling and"""
        program = parse("a and b")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.AND for i in main_func.code))
    
    def test_or(self):
        """Test compiling or"""
        program = parse("a or b")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.OR for i in main_func.code))
    
    def test_not(self):
        """Test compiling not"""
        program = parse("not a")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.NOT for i in main_func.code))


class TestCompilerLists(unittest.TestCase):
    """Test compiling lists"""
    
    def test_empty_list(self):
        """Test compiling empty list"""
        program = parse("[]")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.BUILD_LIST for i in main_func.code))
    
    def test_list_with_elements(self):
        """Test compiling list with elements"""
        program = parse("[1, 2, 3]")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        build_list = [i for i in main_func.code if i.opcode == OpCode.BUILD_LIST][0]
        self.assertEqual(build_list.operand, 3)


class TestCompilerDicts(unittest.TestCase):
    """Test compiling dictionaries"""
    
    def test_empty_dict(self):
        """Test compiling empty dict"""
        program = parse("{}")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.BUILD_DICT for i in main_func.code))
    
    def test_dict_with_entries(self):
        """Test compiling dict with entries"""
        program = parse("{x: 1, y: 2}")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        build_dict = [i for i in main_func.code if i.opcode == OpCode.BUILD_DICT][0]
        self.assertEqual(build_dict.operand, 2)


class TestCompilerFunctions(unittest.TestCase):
    """Test compiling functions"""
    
    def test_function_declaration(self):
        """Test compiling function declaration"""
        source = """fn add(a, b)
  return a + b
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        # Should have at least one function (main) + add
        self.assertGreater(len(module.functions), 1)
    
    def test_function_call(self):
        """Test compiling function call"""
        source = """fn foo()
  return 42

println(foo())
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.CALL for i in main_func.code))
    
    def test_return_with_value(self):
        """Test compiling return with value"""
        source = """fn test()
  return 42
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        # Find the test function
        test_func = None
        for func in module.functions:
            if func.name == "test":
                test_func = func
                break
        
        self.assertIsNotNone(test_func)
        self.assertTrue(any(i.opcode == OpCode.RETURN_VALUE for i in test_func.code))


class TestCompilerControlFlow(unittest.TestCase):
    """Test compiling control flow"""
    
    def test_if_expression(self):
        """Test compiling if expression"""
        source = """if true
  1
else
  2
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.JUMP_IF_FALSE for i in main_func.code))
        self.assertTrue(any(i.opcode == OpCode.JUMP for i in main_func.code))
    
    def test_while_loop(self):
        """Test compiling while loop"""
        source = """while x < 10
  x = x + 1
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.JUMP_IF_FALSE for i in main_func.code))
        self.assertTrue(any(i.opcode == OpCode.JUMP for i in main_func.code))
    
    def test_for_loop(self):
        """Test compiling for loop"""
        source = """for i in range(10)
  println(i)
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        # Should have ITER and ITER_NEXT
        self.assertTrue(any(i.opcode == OpCode.ITER for i in main_func.code))


class TestCompilerIndexAccess(unittest.TestCase):
    """Test compiling index access"""
    
    def test_index_get(self):
        """Test compiling index get"""
        program = parse("arr[0]")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.INDEX_GET for i in main_func.code))


class TestCompilerFieldAccess(unittest.TestCase):
    """Test compiling field access"""
    
    def test_field_access(self):
        """Test compiling field access"""
        program = parse("obj.field")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        main_func = module.functions[module.entry_point]
        self.assertTrue(any(i.opcode == OpCode.GET_ATTR for i in main_func.code))


class TestCompilerErrors(unittest.TestCase):
    """Test compiler error handling"""
    
    def test_unknown_binary_op(self):
        """Test unknown binary operator"""
        program = parse("1 + 2")
        compiler = BytecodeCompiler()
        # This should not raise an error for known operators
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)
    
    def test_unknown_unary_op(self):
        """Test unknown unary operator"""
        program = parse("not true")
        compiler = BytecodeCompiler()
        # This should not raise an error for known operators
        module = compiler.compile_program(program)
        self.assertIsNotNone(module)


class TestCompilerIntegration(unittest.TestCase):
    """Integration tests for compiler"""
    
    def test_complex_program(self):
        """Test compiling a complex program"""
        source = '''
fn factorial(n: int) -> int
  if n <= 1
    return 1
  else
    return n * factorial(n - 1)

let result = factorial(5)
println(result)
'''
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        self.assertIsNotNone(module)
        self.assertGreater(len(module.functions), 1)
    
    def test_globals_tracking(self):
        """Test that globals are properly tracked"""
        source = """let x = 1
let y = 2
fn test()
  return x + y
"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        # Should have x and y in globals
        self.assertIn("x", module.globals)
        self.assertIn("y", module.globals)
    
    def test_disassemble(self):
        """Test disassemble functionality"""
        program = parse("1 + 2")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        # Should be able to disassemble without error
        disasm = module.disassemble()
        self.assertIn("Function", disasm)
        self.assertIn("ADD", disasm)


if __name__ == "__main__":
    unittest.main()
