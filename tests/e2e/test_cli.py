"""
CLI E2E Tests - End-to-end tests for CLI commands
"""

import unittest
import subprocess
import sys
import os
import tempfile
from pathlib import Path


class TestCLIRun(unittest.TestCase):
    """Test 'aic run' command"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_run_hello_world(self):
        source = 'println("Hello, World!")'
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello, World!", result.stdout)

    def test_run_arithmetic(self):
        source = """
let x = 10
let y = 5
println(x + y)
"""
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("15", result.stdout)

    def test_run_function(self):
        source = """
fn square(n)
  return n * n

println(square(5))
"""
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("25", result.stdout)

    def test_run_list_operations(self):
        source = """
let nums = [1, 2, 3, 4, 5]
let doubled = map(nums, fn(x): x * 2)
println(doubled)
"""
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("[2, 4, 6, 8, 10]", result.stdout)

    def test_run_file_not_found(self):
        result = self._run_aic(["run", "/nonexistent/file.aic"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("not found", result.stderr.lower())

    def test_run_parse_error(self):
        source = "let x = "
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 1)
        self.assertIn("parse", result.stderr.lower())

    def test_run_runtime_error(self):
        source = "println(undefined_var)"
        filepath = self._create_test_file(source)
        result = self._run_aic(["run", filepath])
        self.assertEqual(result.returncode, 1)


class TestCLITokenize(unittest.TestCase):
    """Test 'aic tokenize' command"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_tokenize_simple(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["tokenize", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("LET", result.stdout)
        self.assertIn("IDENTIFIER", result.stdout)
        self.assertIn("INT", result.stdout)

    def test_tokenize_function(self):
        source = "fn add(a, b)"
        filepath = self._create_test_file(source)
        result = self._run_aic(["tokenize", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("FN", result.stdout)
        self.assertIn("LPAREN", result.stdout)

    def test_tokenize_file_not_found(self):
        result = self._run_aic(["tokenize", "/nonexistent.aic"])
        self.assertEqual(result.returncode, 1)


class TestCLIParse(unittest.TestCase):
    """Test 'aic parse' command"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_parse_variable(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["parse", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Program", result.stdout)

    def test_parse_function(self):
        source = """
fn add(a, b)
  return a + b
"""
        filepath = self._create_test_file(source)
        result = self._run_aic(["parse", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("FnStmt", result.stdout)

    def test_parse_error(self):
        source = "let x = "
        filepath = self._create_test_file(source)
        result = self._run_aic(["parse", filepath])
        self.assertEqual(result.returncode, 1)


class TestCLICompile(unittest.TestCase):
    """Test 'aic compile' command"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_compile_simple(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["compile", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Bytecode", result.stdout)

    def test_compile_function(self):
        source = """
fn add(a, b)
  return a + b
"""
        filepath = self._create_test_file(source)
        result = self._run_aic(["compile", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Function:", result.stdout)

    def test_compile_verbose(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["compile", "-v", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Constants:", result.stdout)


class TestCLICheck(unittest.TestCase):
    """Test 'aic check' command"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_check_valid(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["check", filepath])
        self.assertEqual(result.returncode, 0)
        self.assertIn("passed", result.stdout.lower())


class TestCLIGeneral(unittest.TestCase):
    """Test general CLI functionality"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_version(self):
        result = self._run_aic(["--version"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("aic", result.stdout)

    def test_help(self):
        result = self._run_aic(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_no_command(self):
        result = self._run_aic([])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_unknown_command(self):
        result = self._run_aic(["unknown"])
        self.assertEqual(result.returncode, 2)


class TestCLIVerbose(unittest.TestCase):
    """Test verbose flag"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_file(self, content, name="test.aic"):
        filepath = os.path.join(self.test_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def _run_aic(self, args):
        cmd = [sys.executable, self.main_py] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_verbose_run(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["-v", "run", filepath])
        self.assertEqual(result.returncode, 0)

    def test_verbose_tokenize(self):
        source = "let x = 42"
        filepath = self._create_test_file(source)
        result = self._run_aic(["--verbose", "tokenize", filepath])
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
