"""
AICode Module System
Handles module loading, caching, and import resolution
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any, List
from src.parser import parse, ParseError
from src.errors import RuntimeError as AICodeRuntimeError, E413, E414


class ModuleError(AICodeRuntimeError):
    """Module loading error"""

    pass


class Module:
    """Represents a loaded AICode module"""

    def __init__(self, name: str, path: Optional[Path] = None):
        self.name = name
        self.path = path
        self.exports: Dict[str, Any] = {}
        self.loaded = False

    def get(self, name: str) -> Any:
        """Get an exported value from the module"""
        if name not in self.exports:
            raise ModuleError(
                E413, f"'{name}' is not exported from module '{self.name}'"
            )
        return self.exports[name]

    def export(self, name: str, value: Any):
        """Export a value from the module"""
        self.exports[name] = value


class ModuleProxy:
    """Proxy object that provides access to module exports via attribute access"""

    def __init__(self, module: Module):
        self._module = module

    def __getattr__(self, name: str) -> Any:
        """Get an exported value from the module"""
        return self._module.get(name)

    def __repr__(self) -> str:
        return f"<module '{self._module.name}'>"


class ModuleManager:
    """Manages module loading and caching"""

    def __init__(self):
        self.modules: Dict[str, Module] = {}
        self.loading_stack: List[str] = []  # For circular import detection
        self.search_paths: List[Path] = []

        # Add standard library path
        stdlib_path = Path(__file__).parent / "stdlib"
        if stdlib_path.exists():
            self.search_paths.append(stdlib_path)

    def add_search_path(self, path: Path):
        """Add a directory to the module search path"""
        self.search_paths.append(path)

    def find_module(self, name: str) -> Optional[Path]:
        """Find a module file by name"""
        # Try .aic extension
        for search_path in self.search_paths:
            module_file = search_path / f"{name}.aic"
            if module_file.exists():
                return module_file

            # Try directory with __init__.aic
            module_dir = search_path / name
            if module_dir.is_dir():
                init_file = module_dir / "__init__.aic"
                if init_file.exists():
                    return init_file

        # Try current directory
        module_file = Path(f"{name}.aic")
        if module_file.exists():
            return module_file

        return None

    def load_module(self, name: str, vm_globals: Dict[str, Any]) -> Module:
        """Load a module and return it"""
        # Check cache
        if name in self.modules:
            return self.modules[name]

        # Check for circular imports
        if name in self.loading_stack:
            raise ModuleError(
                E414,
                f"Circular import detected: {' -> '.join(self.loading_stack)} -> {name}",
            )

        # Find module file
        module_path = self.find_module(name)
        if module_path is None:
            raise ModuleError(E413, f"Module not found: '{name}'")

        # Create module and add to loading stack
        module = Module(name, module_path)
        self.loading_stack.append(name)

        try:
            # Read and parse the module
            with open(module_path, "r", encoding="utf-8") as f:
                source = f.read()

            program = parse(source)

            # Execute the module in a fresh VM context
            from src.interpreter import Interpreter

            interpreter = Interpreter()

            # Create a separate VM for module execution to avoid polluting main VM
            from src.compiler import BytecodeCompiler
            from src.vm import VirtualMachine

            compiler = BytecodeCompiler()
            bytecode_module = compiler.compile_program(program)

            vm = VirtualMachine()

            # Copy built-ins to module VM
            from src.stdlib_ai import BUILTINS

            vm.globals.update(BUILTINS)

            # Execute module
            vm.run(bytecode_module)

            # Collect exports - all top-level definitions are exported by default
            # In the future, we could support explicit export statements
            for stmt in program.statements:
                # Check if statement has a name attribute (LetStmt, ConstStmt, FnStmt)
                stmt_type = type(stmt).__name__
                if stmt_type in ("LetStmt", "ConstStmt", "FnStmt"):
                    var_name = stmt.name
                    if var_name in vm.globals:
                        module.export(var_name, vm.globals[var_name])

            module.loaded = True
            self.modules[name] = module

        except ParseError as e:
            raise ModuleError(E413, f"Failed to parse module '{name}': {e}")
        except Exception as e:
            raise ModuleError(E413, f"Failed to load module '{name}': {e}")
        finally:
            self.loading_stack.pop()

        return module

    def import_names(
        self, module_name: str, names: List[str], vm_globals: Dict[str, Any]
    ):
        """Import specific names from a module into globals"""
        module = self.load_module(module_name, vm_globals)

        for name in names:
            value = module.get(name)
            vm_globals[name] = value

    def import_all(
        self, module_name: str, vm_globals: Dict[str, Any], alias: Optional[str] = None
    ):
        """Import all exports from a module"""
        module = self.load_module(module_name, vm_globals)

        if alias:
            # Import as namespace: import math as m
            vm_globals[alias] = ModuleProxy(module)
        else:
            # Import all exports into global namespace, but also provide module proxy
            # for qualified access like test_math.PI
            vm_globals[module_name] = ModuleProxy(module)
            # Also import all individual exports
            for name, value in module.exports.items():
                vm_globals[name] = value


# Global module manager instance
_module_manager: Optional[ModuleManager] = None


def get_module_manager() -> ModuleManager:
    """Get or create the global module manager"""
    global _module_manager
    if _module_manager is None:
        _module_manager = ModuleManager()
    return _module_manager


def reset_module_manager():
    """Reset the global module manager (useful for testing)"""
    global _module_manager
    _module_manager = None
