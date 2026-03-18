"""
Security Test Suite for AICode
Tests critical security vulnerabilities: Path Traversal, Code Injection, Division by Zero, Index Out of Bounds
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.stdlib_ai import (
    read_file_func,
    write_file_func,
    delete_file_func,
    file_exists_func,
    StdlibError,
)
from src.vm import VirtualMachine, VMError
from src.bytecode import BytecodeModule, BytecodeFunction, Instruction, OpCode


class TestPathTraversal(unittest.TestCase):
    """Test Path Traversal vulnerability fixes"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create a test file
        with open("test.txt", "w") as f:
            f.write("test content")

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_read_file_blocks_traversal(self):
        """Test that read_file blocks path traversal attacks"""
        with self.assertRaises(StdlibError) as ctx:
            read_file_func("../../../etc/passwd")
        self.assertIn("E421", str(ctx.exception))

    def test_read_file_allows_safe_relative_path(self):
        """Test that read_file allows safe relative paths"""
        content = read_file_func("test.txt")
        self.assertEqual(content, "test content")

    def test_write_file_blocks_traversal(self):
        """Test that write_file blocks path traversal attacks"""
        with self.assertRaises(StdlibError) as ctx:
            write_file_func("../../../etc/malware", "evil content")
        self.assertIn("E421", str(ctx.exception))

    def test_write_file_allows_safe_path(self):
        """Test that write_file allows safe paths"""
        write_file_func("newfile.txt", "content")
        self.assertTrue(os.path.exists("newfile.txt"))
        with open("newfile.txt", "r") as f:
            self.assertEqual(f.read(), "content")

    def test_delete_file_blocks_traversal(self):
        """Test that delete_file blocks path traversal attacks"""
        with self.assertRaises(StdlibError) as ctx:
            delete_file_func("../../../etc/passwd")
        self.assertIn("E421", str(ctx.exception))

    def test_delete_file_allows_safe_path(self):
        """Test that delete_file allows safe paths"""
        delete_file_func("test.txt")
        self.assertFalse(os.path.exists("test.txt"))

    def test_file_exists_blocks_traversal(self):
        """Test that file_exists blocks path traversal attacks"""
        with self.assertRaises(StdlibError) as ctx:
            file_exists_func("../../../etc/passwd")
        self.assertIn("E421", str(ctx.exception))

    def test_file_exists_allows_safe_path(self):
        """Test that file_exists allows safe paths"""
        self.assertTrue(file_exists_func("test.txt"))
        self.assertFalse(file_exists_func("nonexistent.txt"))

    def test_null_byte_injection_blocked(self):
        """Test that null byte injection is blocked"""
        with self.assertRaises(StdlibError):
            read_file_func("test.txt\x00/etc/passwd")


class TestDivisionByZero(unittest.TestCase):
    """Test Division by Zero vulnerability fixes"""

    def setUp(self):
        """Set up VM for testing"""
        self.vm = VirtualMachine()

    def test_division_by_zero_raises_error(self):
        """Test that division by zero raises E401 error"""
        # Build a simple bytecode module that divides by zero
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push 10
            Instruction(OpCode.PUSH_CONST, 1),  # Push 0
            Instruction(OpCode.DIV),  # Divide 10 / 0
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__", code=code, locals_count=0, arity=0, constants=[10, 0]
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [10, 0]
        module.globals = []
        module.entry_point = 0

        with self.assertRaises(VMError) as ctx:
            self.vm.run(module)

        self.assertIn("E401", str(ctx.exception))
        self.assertIn("Division by zero", str(ctx.exception))

    def test_normal_division_works(self):
        """Test that normal division still works"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push 10
            Instruction(OpCode.PUSH_CONST, 1),  # Push 2
            Instruction(OpCode.DIV),  # Divide 10 / 2 = 5
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__", code=code, locals_count=0, arity=0, constants=[10, 2]
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [10, 2]
        module.globals = []
        module.entry_point = 0

        self.vm.run(module)
        self.assertEqual(self.vm.pop(), 5.0)


class TestIndexOutOfBounds(unittest.TestCase):
    """Test Index Out of Bounds vulnerability fixes"""

    def setUp(self):
        """Set up VM for testing"""
        self.vm = VirtualMachine()

    def test_negative_index_blocked(self):
        """Test that negative index raises E404 error"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push list
            Instruction(OpCode.PUSH_CONST, 1),  # Push -1
            Instruction(OpCode.INDEX_GET),  # Get item at index -1
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=[[1, 2, 3], -1],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [[1, 2, 3], -1]
        module.globals = []
        module.entry_point = 0

        with self.assertRaises(VMError) as ctx:
            self.vm.run(module)

        self.assertIn("E404", str(ctx.exception))

    def test_out_of_bounds_index_blocked(self):
        """Test that out-of-bounds index raises E404 error"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push list
            Instruction(OpCode.PUSH_CONST, 1),  # Push 5 (out of bounds)
            Instruction(OpCode.INDEX_GET),  # Get item at index 5
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=[[1, 2, 3], 5],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [[1, 2, 3], 5]
        module.globals = []
        module.entry_point = 0

        with self.assertRaises(VMError) as ctx:
            self.vm.run(module)

        self.assertIn("E404", str(ctx.exception))
        self.assertIn("out of bounds", str(ctx.exception))

    def test_valid_index_works(self):
        """Test that valid index still works"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push list
            Instruction(OpCode.PUSH_CONST, 1),  # Push 1
            Instruction(OpCode.INDEX_GET),  # Get item at index 1
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=[[1, 2, 3], 1],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [[1, 2, 3], 1]
        module.globals = []
        module.entry_point = 0

        self.vm.run(module)
        self.assertEqual(self.vm.pop(), 2)


class TestCodeInjection(unittest.TestCase):
    """Test Code Injection via GET_ATTR/SET_ATTR vulnerability fixes"""

    def setUp(self):
        """Set up VM for testing"""
        self.vm = VirtualMachine()

    def test_getattr_on_dict_allowed(self):
        """Test that getattr on dict is allowed"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push dict
            Instruction(OpCode.GET_ATTR, 1),  # Get attr "key" (index 1 in constants)
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=[{"key": "value"}, "key"],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [{"key": "value"}, "key"]
        module.globals = []
        module.entry_point = 0

        self.vm.run(module)
        self.assertEqual(self.vm.pop(), "value")

    def test_getattr_on_non_dict_blocked(self):
        """Test that getattr on non-dict raises E408 error"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push string (not a dict)
            Instruction(OpCode.GET_ATTR, 1),  # Try to get attr (index 1 in constants)
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=["not a dict", "attr"],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = ["not a dict", "attr"]
        module.globals = []
        module.entry_point = 0

        with self.assertRaises(VMError) as ctx:
            self.vm.run(module)

        self.assertIn("E408", str(ctx.exception))
        self.assertIn("Attribute access only allowed on dicts", str(ctx.exception))

    def test_setattr_on_dict_allowed(self):
        """Test that setattr on dict is allowed"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push dict
            Instruction(OpCode.PUSH_CONST, 1),  # Push value
            Instruction(OpCode.SET_ATTR, 2),  # Set attr "key" (index 2 in constants)
            Instruction(OpCode.HALT),
        ]

        test_dict = {"key": "old_value"}
        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=[test_dict, "new_value", "key"],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = [test_dict, "new_value", "key"]
        module.globals = []
        module.entry_point = 0

        self.vm.run(module)
        self.assertEqual(test_dict["key"], "new_value")

    def test_setattr_on_non_dict_blocked(self):
        """Test that setattr on non-dict raises E408 error"""
        code = [
            Instruction(OpCode.PUSH_CONST, 0),  # Push string (not a dict)
            Instruction(OpCode.PUSH_CONST, 1),  # Push value
            Instruction(OpCode.SET_ATTR, 2),  # Try to set attr (index 2 in constants)
            Instruction(OpCode.HALT),
        ]

        func = BytecodeFunction(
            name="__main__",
            code=code,
            locals_count=0,
            arity=0,
            constants=["not a dict", "value", "attr"],
        )

        module = BytecodeModule()
        module.functions.append(func)
        module.constants = ["not a dict", "value", "attr"]
        module.globals = []
        module.entry_point = 0

        with self.assertRaises(VMError) as ctx:
            self.vm.run(module)

        self.assertIn("E408", str(ctx.exception))
        self.assertIn("Attribute access only allowed on dicts", str(ctx.exception))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPathTraversal))
    suite.addTests(loader.loadTestsFromTestCase(TestDivisionByZero))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexOutOfBounds))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeInjection))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
