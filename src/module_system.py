"""
AICode Module System
Handles module loading, caching, namespace isolation, and import resolution
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any, List, Set
from src.parser import parse, ParseError
from src.errors import RuntimeError as AICodeRuntimeError, E413, E414


class CircularImportError(AICodeRuntimeError):
    """Circular import detected"""

    pass


class ModuleError(AICodeRuntimeError):
    """Module loading error"""

    pass


class Module:
    """Represents a loaded AICode module with isolated namespace"""

    def __init__(self, name: str, path: Optional[Path] = None):
        self.name = name
        self.path = path
        self.exports: Dict[str, Any] = {}
        self._all_names: Set[str] = set()  # All top-level names (for debugging)
        self.loaded = False
        self._vm_globals: Dict[str, Any] = {}  # Isolated namespace for module

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
        self._all_names.add(name)

    def __repr__(self) -> str:
        return f"<module '{self.name}'>"


class ModuleProxy:
    """Proxy object that provides access to module exports via attribute access"""

    def __init__(self, module: Module):
        self._module = module

    def __getattr__(self, name: str) -> Any:
        """Get an exported value from the module"""
        return self._module.get(name)

    def __repr__(self) -> str:
        return f"<module '{self._module.name}'>"

    def __dir__(self) -> List[str]:
        """Return list of exported names"""
        return list(self._module.exports.keys())


class ModuleManager:
    """Manages module loading, caching, and namespace isolation"""

    def __init__(self):
        self.modules: Dict[str, Module] = {}
        self.loading_stack: List[str] = []  # For circular import detection
        self.search_paths: List[Path] = []

        # Add standard library path (src/stdlib/)
        stdlib_path = Path(__file__).parent / "stdlib"
        if stdlib_path.exists():
            self.search_paths.append(stdlib_path)

        # Add current working directory
        self.search_paths.append(Path.cwd())

        # Add examples directory (for tests)
        examples_path = Path(__file__).parent.parent / "examples"
        if examples_path.exists():
            self.search_paths.append(examples_path)

    def add_search_path(self, path: Path):
        """Add a directory to the module search path"""
        self.search_paths.append(path)

    def find_module(
        self, name: str, base_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Find a module file by name

        Search order:
        1. Current directory (relative to base_path or cwd)
        2. Search paths (stdlib first)
        3. sys.path
        """
        # Try .aic extension in current directory
        if base_path:
            module_file = base_path / f"{name}.aic"
            if module_file.exists():
                return module_file
        else:
            module_file = Path(f"{name}.aic")
            if module_file.exists():
                return module_file

        # Try directory with __init__.aic
        if base_path:
            module_dir = base_path / name
            if module_dir.is_dir():
                init_file = module_dir / "__init__.aic"
                if init_file.exists():
                    return init_file
        else:
            module_dir = Path(name)
            if module_dir.is_dir():
                init_file = module_dir / "__init__.aic"
                if init_file.exists():
                    return init_file

        # Try search paths (stdlib)
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

        # Try sys.path as last resort
        for sys_path in sys.path:
            sys_path = Path(sys_path)
            module_file = sys_path / f"{name}.aic"
            if module_file.exists():
                return module_file

        return None

    def _collect_exports(self, program, vm_globals: Dict[str, Any]) -> Dict[str, Any]:
        """Collect exported names from module execution

        Export rules:
        - Functions/structs/enums marked with `export` are exported
        - Names NOT starting with `_` are exported by default
        - Names starting with `_` are private (unless exported)
        """
        exports = {}
        from src.ast_nodes import FnStmt, LetStmt, ConstStmt, StructStmt, EnumStmt

        for stmt in program.statements:
            if isinstance(stmt, FnStmt):
                name = stmt.name
                if stmt.exported or not name.startswith("_"):
                    if name in vm_globals:
                        exports[name] = vm_globals[name]
            elif isinstance(stmt, (LetStmt, ConstStmt)):
                name = stmt.name
                # Only export if not private (_prefix)
                if not name.startswith("_"):
                    if name in vm_globals:
                        exports[name] = vm_globals[name]
            elif isinstance(stmt, StructStmt):
                name = stmt.name
                if stmt.exported or not name.startswith("_"):
                    if name in vm_globals:
                        exports[name] = vm_globals[name]
            elif isinstance(stmt, EnumStmt):
                name = stmt.name
                if stmt.exported or not name.startswith("_"):
                    if name in vm_globals:
                        exports[name] = vm_globals[name]

        return exports

    def load_module(
        self,
        name: str,
        vm_globals: Optional[Dict[str, Any]] = None,
        base_path: Optional[Path] = None,
    ) -> Module:
        """Load a module and return it with isolated namespace

        Args:
            name: Module name to load
            vm_globals: Optional globals from parent VM (for import context)
            base_path: Optional base path for relative imports

        Returns:
            Module: Loaded module with exports

        Raises:
            CircularImportError: If circular import detected
            ModuleError: If module not found or failed to load
        """
        # Check for circular imports first (before cache)
        if name in self.loading_stack:
            cycle = " -> ".join(self.loading_stack + [name])
            raise CircularImportError(E414, f"Circular import detected: {cycle}")

        # Check cache
        if name in self.modules:
            return self.modules[name]

        # Find module file
        module_path = self.find_module(name, base_path)
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

            # Execute the module in a fresh isolated VM context
            from src.compiler import BytecodeCompiler
            from src.vm import VirtualMachine

            compiler = BytecodeCompiler()
            bytecode_module = compiler.compile_program(program)

            # Create isolated VM for this module
            vm = VirtualMachine()

            # Copy built-ins to module VM
            from src.stdlib_ai import BUILTINS

            vm.globals.update(BUILTINS)

            # Execute module in isolated context
            vm.run(bytecode_module)

            # Collect exports based on naming conventions
            module.exports = self._collect_exports(program, vm.globals)
            module._vm_globals = vm.globals.copy()
            module.loaded = True

            # Cache the module
            self.modules[name] = module

        except ParseError as e:
            raise ModuleError(E413, f"Failed to parse module '{name}': {e}")
        except CircularImportError:
            raise  # Re-raise circular import errors
        except Exception as e:
            raise ModuleError(E413, f"Failed to load module '{name}': {e}")
        finally:
            self.loading_stack.pop()

        return module

    def import_names(
        self,
        module_name: str,
        names: List[str],
        vm_globals: Dict[str, Any],
        base_path: Optional[Path] = None,
    ):
        """Import specific names from a module into globals (from X import a, b)

        Args:
            module_name: Module to import from
            names: List of names to import
            vm_globals: Global namespace to import into
            base_path: Optional base path for relative imports
        """
        module = self.load_module(module_name, vm_globals, base_path)

        for name in names:
            value = module.get(name)
            vm_globals[name] = value

    def import_module(
        self,
        module_name: str,
        vm_globals: Dict[str, Any],
        alias: Optional[str] = None,
        base_path: Optional[Path] = None,
    ):
        """Import a module as namespace

        Syntax:
        - import math              -> math.PI
        - import math as m        -> m.PI
        - import math { PI }      -> PI directly (selective import)

        Args:
            module_name: Module to import
            vm_globals: Global namespace to import into
            alias: Optional alias for the module
            base_path: Optional base path for relative imports
        """
        module = self.load_module(module_name, vm_globals, base_path)

        if alias:
            # import math as m
            vm_globals[alias] = ModuleProxy(module)
        else:
            # import math
            vm_globals[module_name] = ModuleProxy(module)

    def import_selective(
        self,
        module_name: str,
        names: List[str],
        vm_globals: Dict[str, Any],
        base_path: Optional[Path] = None,
    ):
        """Import selective names from a module

        Syntax: import math { PI, sqrt }

        Args:
            module_name: Module to import from
            names: List of names to import
            vm_globals: Global namespace to import into
            base_path: Optional base path for relative imports
        """
        module = self.load_module(module_name, vm_globals, base_path)

        for name in names:
            value = module.get(name)
            vm_globals[name] = value

    def get_module_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded module"""
        if name not in self.modules:
            return None

        module = self.modules[name]
        return {
            "name": module.name,
            "path": str(module.path) if module.path else None,
            "exports": list(module.exports.keys()),
            "loaded": module.loaded,
        }

    def clear_cache(self):
        """Clear the module cache (useful for testing)"""
        self.modules.clear()
        self.loading_stack.clear()


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


def add_search_path(path: Path):
    """Add a search path to the global module manager"""
    manager = get_module_manager()
    manager.add_search_path(path)
