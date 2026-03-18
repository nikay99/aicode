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
    def __init__(self):
        self.output: List[str] = []
        self.vm = VirtualMachine()
        self._inject_output_capture()

    def _inject_output_capture(self):
        output = self.output

        def _captured_print(*args):
            output.append("".join(str(a) for a in args))

        def _captured_println(*args):
            output.append(" ".join(str(a) for a in args))

        self.vm.globals["print"] = _captured_print
        self.vm.globals["println"] = _captured_println

    def interpret(self, program) -> List[str]:
        self.output = []
        self._inject_output_capture()

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
