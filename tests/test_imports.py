"""Tests for AICode module import system"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interpreter import Interpreter, AICodeError
from src.parser import parse
from src.module_system import reset_module_manager


class TestImports(unittest.TestCase):
    def setUp(self):
        """Reset module manager before each test"""
        reset_module_manager()
    
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


if __name__ == "__main__":
    unittest.main()
