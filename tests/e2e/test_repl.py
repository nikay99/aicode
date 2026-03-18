"""
REPL E2E Tests - End-to-end tests for REPL functionality
"""

import unittest
import subprocess
import sys
import os
from pathlib import Path
import time
import signal


class TestREPLBasic(unittest.TestCase):
    """Test basic REPL functionality"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _start_repl(self):
        cmd = [sys.executable, self.main_py, "repl"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc

    def test_repl_exit(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(input="exit\n", timeout=2)
            self.assertEqual(proc.returncode, 0)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not exit in time")

    def test_repl_quit(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(input="quit\n", timeout=2)
            self.assertEqual(proc.returncode, 0)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not exit in time")

    def test_repl_help(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(input="help\nexit\n", timeout=2)
            self.assertIn("help", stdout.lower())
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLExecution(unittest.TestCase):
    """Test REPL code execution"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _start_repl(self):
        cmd = [sys.executable, self.main_py, "repl"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc

    def test_repl_println(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(
                input='println("hello")\nexit\n', timeout=2
            )
            self.assertIn("hello", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")

    def test_repl_arithmetic(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(input="println(2 + 3)\nexit\n", timeout=2)
            self.assertIn("5", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")

    def test_repl_variable(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(
                input="let x = 10\nprintln(x)\nexit\n", timeout=2
            )
            self.assertIn("10", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLPrompt(unittest.TestCase):
    """Test REPL prompt styles"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def test_repl_python_prompt(self):
        cmd = [sys.executable, self.main_py, "repl", "--prompt", "python"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(input="exit\n", timeout=2)
            self.assertIn(">>>", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")

    def test_repl_simple_prompt(self):
        cmd = [sys.executable, self.main_py, "repl", "--prompt", "simple"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(input="exit\n", timeout=2)
            self.assertIn(">", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLMultiline(unittest.TestCase):
    """Test REPL multiline input"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _start_repl(self):
        cmd = [sys.executable, self.main_py, "repl"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc

    def test_repl_function(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(
                input="fn add(a, b)\n  return a + b\nprintln(add(2, 3))\nexit\n",
                timeout=2,
            )
            self.assertIn("5", stdout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLClear(unittest.TestCase):
    """Test REPL clear command"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def test_repl_clear(self):
        proc = subprocess.Popen(
            [sys.executable, self.main_py, "repl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(input="clear\nexit\n", timeout=2)
            self.assertEqual(proc.returncode, 0)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLParserErrors(unittest.TestCase):
    """Test REPL error handling"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _start_repl(self):
        cmd = [sys.executable, self.main_py, "repl"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc

    def test_repl_parse_error(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(input="let x = \nexit\n", timeout=2)
            self.assertIn("parse", stdout.lower())
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


class TestREPLRuntimeErrors(unittest.TestCase):
    """Test REPL runtime error handling"""

    def setUp(self):
        self.main_py = str(Path(__file__).parent.parent.parent.parent / "main.py")

    def _start_repl(self):
        cmd = [sys.executable, self.main_py, "repl"]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc

    def test_repl_undefined_variable(self):
        proc = self._start_repl()
        try:
            stdout, stderr = proc.communicate(
                input="println(undefined)\nexit\n", timeout=2
            )
            combined = stdout + stderr
            self.assertTrue(
                "error" in combined.lower() or "undefined" in combined.lower()
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("REPL did not respond in time")


if __name__ == "__main__":
    unittest.main()
