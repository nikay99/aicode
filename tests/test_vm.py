"""
Comprehensive VM Tests
Tests for VM execution
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import parse
from src.compiler import BytecodeCompiler
from src.vm import VirtualMachine, VMError, CallFrame
from src.bytecode import BytecodeFunction, BytecodeModule, Instruction, OpCode


class TestVMBasics(unittest.TestCase):
    """Test basic VM operations"""
    
    def test_push_const(self):
        """Test pushing constants"""
        source = "42"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        vm.run(module)
        # Should complete without error
    
    def test_push_null(self):
        """Test pushing null"""
        source = "null"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        vm.run(module)
    
    def test_pop(self):
        """Test pop operation"""
        source = "1 + 2"
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        vm.run(module)


class TestVMArithmetic(unittest.TestCase):
    """Test VM arithmetic operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        # Capture println output
        def capture_println(*args):
            outputs.append(" ".join(str(a) for a in args))
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_addition(self):
        """Test addition"""
        outputs = self.run_and_capture("println(1 + 2)")
        self.assertEqual(outputs, ["3"])
    
    def test_subtraction(self):
        """Test subtraction"""
        outputs = self.run_and_capture("println(5 - 3)")
        self.assertEqual(outputs, ["2"])
    
    def test_multiplication(self):
        """Test multiplication"""
        outputs = self.run_and_capture("println(3 * 4)")
        self.assertEqual(outputs, ["12"])
    
    def test_division(self):
        """Test division"""
        outputs = self.run_and_capture("println(10 / 2)")
        self.assertEqual(outputs, ["5.0"])
    
    def test_modulo(self):
        """Test modulo"""
        outputs = self.run_and_capture("println(10 % 3)")
        self.assertEqual(outputs, ["1"])
    
    def test_negation(self):
        """Test negation"""
        outputs = self.run_and_capture("println(-5)")
        self.assertEqual(outputs, ["-5"])
    
    def test_complex_arithmetic(self):
        """Test complex arithmetic expression"""
        outputs = self.run_and_capture("println((1 + 2) * (3 + 4))")
        self.assertEqual(outputs, ["21"])


class TestVMComparison(unittest.TestCase):
    """Test VM comparison operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_equality(self):
        """Test equality"""
        outputs = self.run_and_capture("println(1 == 1)")
        self.assertEqual(outputs, ["True"])
    
    def test_inequality(self):
        """Test inequality"""
        outputs = self.run_and_capture("println(1 != 2)")
        self.assertEqual(outputs, ["True"])
    
    def test_less_than(self):
        """Test less than"""
        outputs = self.run_and_capture("println(1 < 2)")
        self.assertEqual(outputs, ["True"])
    
    def test_greater_than(self):
        """Test greater than"""
        outputs = self.run_and_capture("println(2 > 1)")
        self.assertEqual(outputs, ["True"])
    
    def test_less_equal(self):
        """Test less or equal"""
        outputs = self.run_and_capture("println(1 <= 1)")
        self.assertEqual(outputs, ["True"])
    
    def test_greater_equal(self):
        """Test greater or equal"""
        outputs = self.run_and_capture("println(1 >= 1)")
        self.assertEqual(outputs, ["True"])


class TestVMLogical(unittest.TestCase):
    """Test VM logical operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_and_true(self):
        """Test and with true values"""
        outputs = self.run_and_capture("println(true and true)")
        self.assertEqual(outputs, ["True"])
    
    def test_and_false(self):
        """Test and with false value"""
        outputs = self.run_and_capture("println(true and false)")
        self.assertEqual(outputs, ["False"])
    
    def test_or_true(self):
        """Test or with true value"""
        outputs = self.run_and_capture("println(true or false)")
        self.assertEqual(outputs, ["True"])
    
    def test_or_false(self):
        """Test or with false values"""
        outputs = self.run_and_capture("println(false or false)")
        self.assertEqual(outputs, ["False"])
    
    def test_not(self):
        """Test not"""
        outputs = self.run_and_capture("println(not false)")
        self.assertEqual(outputs, ["True"])


class TestVMVariables(unittest.TestCase):
    """Test VM variable operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_let_statement(self):
        """Test let statement"""
        outputs = self.run_and_capture("""let x = 42
println(x)
""")
        self.assertEqual(outputs, ["42"])
    
    def test_assignment(self):
        """Test assignment"""
        outputs = self.run_and_capture("""let x = 1
x = 2
println(x)
""")
        self.assertEqual(outputs, ["2"])


class TestVMLoops(unittest.TestCase):
    """Test VM loop operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_while_loop(self):
        """Test while loop"""
        outputs = self.run_and_capture("""let i = 0
let sum = 0
while i < 5
  sum = sum + i
  i = i + 1
println(sum)
""")
        self.assertEqual(outputs, ["10"])  # 0+1+2+3+4
    
    def test_for_loop(self):
        """Test for loop"""
        source = """let sum = 0
for i in [1, 2, 3, 4, 5]
  sum = sum + i
println(sum)
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["15"])  # 1+2+3+4+5


class TestVMLists(unittest.TestCase):
    """Test VM list operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_empty_list(self):
        """Test empty list"""
        outputs = self.run_and_capture("println([1])")
        self.assertEqual(outputs, ["[1]"])
    
    def test_list_indexing(self):
        """Test list indexing"""
        outputs = self.run_and_capture("println([10, 20, 30][1])")
        self.assertEqual(outputs, ["20"])


class TestVMDicts(unittest.TestCase):
    """Test VM dict operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_dict_creation(self):
        """Test dict creation"""
        outputs = self.run_and_capture('println({"a": 1})')
        self.assertEqual(outputs, ["{'a': 1}"])
    
    def test_dict_field_access(self):
        """Test dict field access"""
        source = """let d = {"x": 10}
println(d.x)
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["10"])


class TestVMFunctions(unittest.TestCase):
    """Test VM function operations"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_function_call(self):
        """Test function call"""
        source = """fn greet()
  println("hello")

greet()
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["hello"])
    
    def test_function_with_params(self):
        """Test function with parameters"""
        source = """fn add(a, b)
  return a + b

println(add(2, 3))
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["5"])
    
    def test_function_return_value(self):
        """Test function return value"""
        source = """fn square(n)
  return n * n

println(square(4))
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["16"])


class TestVMStackOperations(unittest.TestCase):
    """Test VM stack operations"""
    
    def test_push_and_pop(self):
        """Test push and pop operations"""
        vm = VirtualMachine()
        vm.push(42)
        self.assertEqual(vm.pop(), 42)
    
    def test_peek(self):
        """Test peek operation"""
        vm = VirtualMachine()
        vm.push(1)
        vm.push(2)
        self.assertEqual(vm.peek(), 2)
        self.assertEqual(vm.peek(1), 1)
    
    def test_stack_underflow(self):
        """Test stack underflow error"""
        vm = VirtualMachine()
        with self.assertRaises(VMError):
            vm.pop()


class TestVMBuiltins(unittest.TestCase):
    """Test VM built-in functions"""
    
    def run_and_capture(self, source: str) -> list:
        """Helper to run code and capture output"""
        program = parse(source)
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        outputs = []
        
        def capture_println(*args):
            outputs.append(str(args[0]) if args else "")
        
        vm.globals['println'] = capture_println
        vm.run(module)
        
        return outputs
    
    def test_range_builtin(self):
        """Test range builtin"""
        source = """let nums = range(5)
println(length(nums))
"""
        outputs = self.run_and_capture(source)
        self.assertEqual(outputs, ["5"])
    
    def test_length_builtin(self):
        """Test length builtin"""
        outputs = self.run_and_capture("println(length([1, 2, 3]))")
        self.assertEqual(outputs, ["3"])


class TestVMErrors(unittest.TestCase):
    """Test VM error handling"""
    
    def test_undefined_global(self):
        """Test undefined global variable"""
        program = parse("println(undefined)")
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        vm = VirtualMachine()
        with self.assertRaises(VMError):
            vm.run(module)


if __name__ == "__main__":
    unittest.main()
