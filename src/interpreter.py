"""
AICode Interpreter
Combines Compiler and VM for execution
"""

import sys
from typing import List, Any
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.compiler import BytecodeCompiler, CompilerError
from src.vm import VirtualMachine, VMError
from src.bytecode import BytecodeModule


class AICodeError(Exception):
    """AICode runtime error"""
    pass


class Interpreter:
    """Interpreter using compiler + VM"""

    def __init__(self):
        self.vm = VirtualMachine()
        self.output: List[str] = []

    def interpret(self, program) -> List[str]:
        """Interpret an AST program"""
        self.output = []

        try:
            compiler = BytecodeCompiler()
            module = compiler.compile_program(program)

            self.vm.run(module)

        except CompilerError as e:
            raise AICodeError(f"Compilation error: {e}")
        except VMError as e:
            raise AICodeError(f"Runtime error: {e}")

        return self.output


def interpret(program) -> List[str]:
    """Convenience function to interpret a program"""
    interpreter = Interpreter()
    return interpreter.interpret(program)
