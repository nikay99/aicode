"""
AICode Interpreter
Combines Compiler and VM for execution
"""

from typing import List, Any, Optional
from src.compiler import BytecodeCompiler, CompilerError
from src.vm import VirtualMachine, VMError
from src.stdlib_ai import StdlibError
from src.module_system import get_module_manager, ModuleError, CircularImportError
from src.ast_nodes import ImportStmt, Program
from src import ast_nodes as ast


class AICodeError(Exception):
    """AICode runtime error"""

    pass


class Interpreter:
    """Interpreter using compiler + VM"""

    def __init__(self):
        self.output: List[str] = []
        self.vm = VirtualMachine()
        self.module_manager = get_module_manager()
        self._inject_output_capture()

    def _inject_output_capture(self):
        """Replace built-in print/println to capture output"""
        output = self.output

        def _captured_print(*args):
            output.append("".join(str(a) for a in args))

        def _captured_println(*args):
            output.append(" ".join(str(a) for a in args))

        self.vm.globals["print"] = _captured_print
        self.vm.globals["println"] = _captured_println

    def _process_imports(self, program: Program):
        """Process import statements before compilation"""
        for stmt in program.statements:
            if isinstance(stmt, ImportStmt):
                self._handle_import(stmt)

    def _handle_import(self, stmt: ImportStmt):
        """Handle a single import statement

        Supports:
        - import math              -> Namespace import
        - import math as m        -> With alias
        - import math { PI, sqrt } -> Selective import
        - from math import PI, sqrt -> Alternative syntax
        """
        try:
            if stmt.names:
                # Selective import: import module { name1, name2 }
                # Or: from module import name1, name2
                self.module_manager.import_selective(
                    stmt.module, stmt.names, self.vm.globals
                )
            else:
                # Namespace import: import module [as alias]
                self.module_manager.import_module(
                    stmt.module, self.vm.globals, alias=stmt.alias
                )
        except ModuleError as e:
            raise AICodeError(f"Import error: {e}")
        except CircularImportError as e:
            raise AICodeError(f"Circular import error: {e}")

    def _collect_imported_names(self, program: Program) -> List[str]:
        """Collect names that are imported from other modules"""
        imported_names = []
        for stmt in program.statements:
            if isinstance(stmt, ImportStmt):
                if stmt.alias:
                    # import module as alias
                    imported_names.append(stmt.alias)
                elif stmt.names:
                    # import module { name1, name2 }
                    imported_names.extend(stmt.names)
                else:
                    # import module - module name becomes namespace
                    imported_names.append(stmt.module)
        return imported_names

    def interpret(self, program) -> List[str]:
        """Interpret an AST program"""
        self.output = []
        self._inject_output_capture()

        try:
            # Collect import names before processing (for compiler)
            imported_names = self._collect_imported_names(program)

            # Process imports first
            self._process_imports(program)

            # Remove import statements from program before compilation
            # (they've already been processed)
            filtered_statements = [
                stmt for stmt in program.statements if not isinstance(stmt, ImportStmt)
            ]
            filtered_program = Program(filtered_statements)

            # Compile and run with imported names and existing globals
            compiler = BytecodeCompiler()
            existing_globals = list(self.vm.globals.keys())
            extra_globals = imported_names + existing_globals
            module = compiler.compile_program(
                filtered_program, extra_globals=extra_globals
            )
            self.vm.run(module)

        except CompilerError as e:
            raise AICodeError(f"Compilation error: {e}")
        except VMError as e:
            raise AICodeError(f"Runtime error: {e}")
        except StdlibError as e:
            raise AICodeError(f"Runtime error: {e}")
        except ModuleError as e:
            raise AICodeError(f"Module error: {e}")
        except CircularImportError as e:
            raise AICodeError(f"Circular import error: {e}")

        return self.output


def interpret(program) -> List[str]:
    """Convenience function to interpret a program"""
    interpreter = Interpreter()
    return interpreter.interpret(program)
