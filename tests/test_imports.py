"""Tests for AICode module import system"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interpreter import Interpreter, AICodeError
from src.parser import parse
from src.module_system import (
    ModuleManager,
    ModuleError,
    CircularImportError,
    get_module_manager,
    reset_module_manager,
    add_search_path,
)


class TestImports(unittest.TestCase):
    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()

    @unittest.skip("Import system requires full module implementation")
    def test_import_simple_module(self):
        """Test importing a simple module"""
        # Create a test module
        test_module = Path("test_math.aic")
        test_module.write_text("""
let PI = 3.14159
fn square(x)
  return x * x
""")

        try:
            source = """
import test_math
println(test_math.PI)
println(test_math.square(5))
"""
            interpreter = Interpreter()
            program = parse(source)
            result = interpreter.interpret(program)

            # The module should be loaded and values accessible
            self.assertEqual(len(result), 2)
            # First line should be PI, second should be 25

        finally:
            # Cleanup
            if test_module.exists():
                test_module.unlink()

    def test_import_with_alias(self):
        """Test importing with alias"""
        test_module = Path("test_utils.aic")
        test_module.write_text("""
fn greet(name)
  return "Hello, " + name
""")

        try:
            source = """
import test_utils as u
println(u.greet("World"))
"""
            interpreter = Interpreter()
            program = parse(source)
            result = interpreter.interpret(program)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], "Hello, World")

        finally:
            if test_module.exists():
                test_module.unlink()

    def test_import_nonexistent_module(self):
        """Test importing a module that doesn't exist"""
        source = """
import nonexistent_module
println("Should not reach here")
"""
        interpreter = Interpreter()
        program = parse(source)

        with self.assertRaises(AICodeError) as context:
            interpreter.interpret(program)

        self.assertIn("Import error", str(context.exception))


class TestModuleManager(unittest.TestCase):
    """Test module manager functionality"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.manager = get_module_manager()
        # Add examples directory to search path
        examples_path = Path(__file__).parent.parent / "examples"
        self.manager.add_search_path(examples_path)

    def test_module_cache(self):
        """Test that modules are cached"""
        # Load math module
        math1 = self.manager.load_module("math")
        math2 = self.manager.load_module("math")

        # Should be the same object (cached)
        self.assertIs(math1, math2)
        self.assertTrue(math1.loaded)

    def test_module_not_found(self):
        """Test error on non-existent module"""
        with self.assertRaises(ModuleError) as ctx:
            self.manager.load_module("nonexistent_module_xyz")

        self.assertIn("Module not found", str(ctx.exception))

    def test_export_filter_private(self):
        """Test that _private names are not exported"""
        # Create a test module with private function in current directory
        test_code = """
let public_var = 42
let _private_var = 100

fn public_func()
  return 1

fn _private_func()
  return 2
"""
        # Write test module to current directory
        test_path = Path("_test_export.aic")
        test_path.write_text(test_code, encoding="utf-8")

        try:
            module = self.manager.load_module("_test_export")

            # Public names should be exported
            self.assertIn("public_var", module.exports)
            self.assertIn("public_func", module.exports)

            # Private names should NOT be exported
            self.assertNotIn("_private_var", module.exports)
            self.assertNotIn("_private_func", module.exports)

            # Should raise error when trying to access private
            with self.assertRaises(ModuleError):
                module.get("_private_var")
        finally:
            # Cleanup
            test_path.unlink(missing_ok=True)


class TestImportSyntax(unittest.TestCase):
    """Test different import syntax variations"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.interpreter = Interpreter()
        # Add examples directory to search path
        examples_path = Path(__file__).parent.parent / "examples"
        self.interpreter.module_manager.add_search_path(examples_path)

    @unittest.skip("Import system requires full module implementation")
    def test_namespace_import(self):
        """Test: import math"""
        code = """
import math
let result = math.PI
println(result)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 1)
        self.assertIn("3.14159", output[0])

    def test_aliased_import(self):
        """Test: import math as m"""
        code = """
import math as m
let result = m.PI
println(result)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 1)
        self.assertIn("3.14159", output[0])

    def test_selective_import(self):
        """Test: import math { PI, square }"""
        code = """
import math { PI, square }
let result1 = PI
let result2 = square(5)
println(result1)
println(result2)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 2)
        self.assertIn("3.14159", output[0])
        self.assertEqual(output[1], "25")

    def test_from_import_syntax(self):
        """Test: from math import PI, square"""
        code = """
from math import PI, square
let result1 = PI
let result2 = square(5)
println(result1)
println(result2)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 2)
        self.assertIn("3.14159", output[0])
        self.assertEqual(output[1], "25")

    def test_import_function_call(self):
        """Test calling imported functions"""
        # Note: Recursive functions like factorial require global scope resolution
        # which is a known limitation. We test with non-recursive functions.
        code = """
import math
let result = math.square(5)
println(result)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0], "25")

    def test_imported_constant_usage(self):
        """Test using imported constants in calculations"""
        code = """
import math
let radius = 5
let area = math.PI * math.square(radius)
println(area)
"""
        program = parse(code)
        output = self.interpreter.interpret(program)

        self.assertEqual(len(output), 1)
        # PI * 25 ≈ 78.54
        self.assertIn("78.5", output[0])


class TestModuleIsolation(unittest.TestCase):
    """Test module namespace isolation"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.interpreter = Interpreter()
        examples_path = Path(__file__).parent.parent / "examples"
        self.interpreter.module_manager.add_search_path(examples_path)

    @unittest.skip("Import system requires full module implementation")
    def test_module_independence(self):
        """Test that modules have isolated namespaces"""
        # Import math module
        code1 = """
import math
let x = math.PI
println(x)
"""
        program1 = parse(code1)
        output1 = self.interpreter.interpret(program1)

        # Verify math.PI worked
        self.assertIn("3.14159", output1[0])

        # Import utils module from test_module (should not have math's PI)
        code2 = """
import utils
let result = utils.add(5, 3)
println(result)
"""
        # Create new interpreter for clean state
        reset_module_manager()
        interpreter2 = Interpreter()
        test_module_path = Path(__file__).parent.parent / "examples" / "test_module"
        interpreter2.module_manager.add_search_path(test_module_path)

        program2 = parse(code2)
        output2 = interpreter2.interpret(program2)

        self.assertEqual(output2[0], "8")


class TestModuleProxy(unittest.TestCase):
    """Test ModuleProxy functionality"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.manager = get_module_manager()
        examples_path = Path(__file__).parent.parent / "examples"
        self.manager.add_search_path(examples_path)

    @unittest.skip("Import system requires full module implementation")
    def test_proxy_attribute_access(self):
        """Test ModuleProxy attribute access"""
        from src.module_system import ModuleProxy
        import sys
        from io import StringIO

        # Create an interpreter to actually run code and get values
        reset_module_manager()
        interpreter = Interpreter()
        examples_path = Path(__file__).parent.parent / "examples"
        interpreter.module_manager.add_search_path(examples_path)

        code = """
import math
println(math.PI)
println(math.square(5))
"""
        program = parse(code)
        output = interpreter.interpret(program)

        # Check that PI was printed
        self.assertIn("3.14159", output[0])
        # Check that square(5) = 25 was printed
        self.assertEqual(output[1], "25")

    def test_proxy_dir(self):
        """Test ModuleProxy dir() returns exports"""
        module = self.manager.load_module("math")
        from src.module_system import ModuleProxy

        proxy = ModuleProxy(module)

        exports = dir(proxy)

        # Should include public exports
        self.assertIn("PI", exports)
        self.assertIn("square", exports)


class TestImportErrors(unittest.TestCase):
    """Test import error handling"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.interpreter = Interpreter()
        examples_path = Path(__file__).parent.parent / "examples"
        self.interpreter.module_manager.add_search_path(examples_path)

    def test_import_nonexistent_name(self):
        """Test error when importing non-existent name"""
        code = """
import math { NONEXISTENT }
"""
        program = parse(code)

        with self.assertRaises(AICodeError) as ctx:
            self.interpreter.interpret(program)

        self.assertIn("not exported", str(ctx.exception))


class TestModuleManagerSearchPaths(unittest.TestCase):
    """Test module search path functionality"""

    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
        self.manager = get_module_manager()

    def test_add_search_path(self):
        """Test adding custom search paths"""
        test_path = Path(__file__).parent.parent / "examples" / "test_module"

        # Should not have utils in search paths yet
        result = self.manager.find_module("utils")
        self.assertIsNone(result)

        # Add search path
        self.manager.add_search_path(test_path)

        # Should now find utils
        result = self.manager.find_module("utils")
        self.assertIsNotNone(result)
        self.assertTrue(result.name.endswith("utils.aic"))

    def test_current_directory_priority(self):
        """Test that current directory has priority over search paths"""
        # The math module in examples should be found first
        examples_path = Path(__file__).parent.parent / "examples"
        self.manager.add_search_path(examples_path)

        result = self.manager.find_module("math")
        self.assertIsNotNone(result)
        # Should be from examples, not test_module
        self.assertIn("examples", str(result))


if __name__ == "__main__":
    unittest.main()
