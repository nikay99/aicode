#!/usr/bin/env python3
"""
AICode CLI - Command Line Interface for AICode Programming Language

AICode is a programming language designed specifically for LLMs, using mathematical
Unicode symbols to achieve 40-60% token reduction compared to Python.

Enhanced version with project management, build, test, and format commands
"""

import sys
import argparse
import os
import pickle
import time
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src import __version__
from src.lexer import tokenize, Token, TokenType
from src.parser import parse
from src.errors import ParserError, AICodeError
from src.interpreter import Interpreter, AICodeError
from src.compiler import BytecodeCompiler, CompilerError
from src.vm import VirtualMachine, VMError
from src.bytecode import BytecodeModule
from src.type_checker import TypeChecker, TypeError as TCTypeError
from src.package_manager import PackageManager, PackageManagerError, SemverVersion
from src.formatter import AICodeFormatter
from src.linter import Linter


# ANSI Farbcodes für Terminal
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


def colorize(text: str, color: str) -> str:
    """Färbe Text ein"""
    return f"{color}{text}{Colors.RESET}"


def read_file(filepath: str) -> str:
    """Read a file and return its contents."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"Error: Not a file: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        print(
            f"Error: Could not decode file (expected UTF-8): {filepath}",
            file=sys.stderr,
        )
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def get_source_line(filepath: str, line_num: int) -> str:
    """Liest eine bestimmte Zeile aus einer Datei"""
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            if 0 < line_num <= len(lines):
                return lines[line_num - 1].rstrip()
    except:
        pass
    return ""


def print_error(
    filepath: str,
    line: int,
    column: int,
    code: str,
    message: str,
    source_line: str = "",
):
    """Schöne Fehlerausgabe mit Farben"""
    print(file=sys.stderr)
    print(
        colorize(f"Error [{code}] at {filepath}:{line}:{column}", Colors.RED),
        file=sys.stderr,
    )
    print(colorize("   |", Colors.GRAY), file=sys.stderr)
    print(
        colorize(f"{line:2} |", Colors.GRAY),
        source_line if source_line else "...",
        file=sys.stderr,
    )

    if source_line and column > 0:
        pointer = " " * (column - 1) + "^" * min(len(source_line) - column + 1, 10)
        print(
            colorize("   |", Colors.GRAY),
            colorize(pointer, Colors.RED),
            file=sys.stderr,
        )

    print(file=sys.stderr)
    print(colorize(message, Colors.BOLD), file=sys.stderr)
    print(file=sys.stderr)
    print(colorize(f"Error [{code}] at {filepath}:{line}:{column}", Colors.RED))
    print(colorize("   |", Colors.GRAY))
    print(colorize(f"{line:2} |", Colors.GRAY), source_line if source_line else "...")

    if source_line and column > 0:
        pointer = " " * (column - 1) + "^" * min(len(source_line) - column + 1, 10)
        print(colorize("   |", Colors.GRAY), colorize(pointer, Colors.RED))

    print()
    print(colorize(message, Colors.BOLD))
    print()


def format_token(token: Token) -> str:
    """Format a token for display."""
    value_str = (
        f" = {token.value!r}"
        if token.value is not None and token.value != token.type.name
        else ""
    )
    return f"{token.line:4}:{token.column:3}  {token.type.name:15} {value_str}"


def init_project(project_name: str):
    """Erstellt ein neues Projekt-Template"""
    project_path = Path(project_name)

    if project_path.exists():
        print(colorize(f"Error: Directory '{project_name}' already exists", Colors.RED))
        sys.exit(1)

    print(colorize(f"Creating new AICode project: {project_name}", Colors.CYAN))

    # Erstelle Verzeichnisstruktur
    (project_path / "lib").mkdir(parents=True)
    (project_path / "tests").mkdir(parents=True)

    # main.aic
    main_content = """# Main entry point for {project_name}

fn main()
  println("Hello, {project_name}!")

main()
""".format(project_name=project_name)

    (project_path / "main.aic").write_text(main_content)

    # aicode.toml
    toml_content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "A new AICode project"

[dependencies]
# Add dependencies here

[build]
entry = "main.aic"
output = "build"
'''

    (project_path / "aicode.toml").write_text(toml_content)

    # Beispiel-Test
    test_content = """# Test suite for {project_name}

fn test_addition()
  let result = 2 + 2
  assert(result == 4)

test_addition()
""".format(project_name=project_name)

    (project_path / "tests" / "test_main.aic").write_text(test_content)

    print(colorize(f"✓ Created project '{project_name}'", Colors.GREEN))
    print()
    print(colorize("Project structure:", Colors.CYAN))
    print(f"  {project_name}/")
    print(f"  ├── main.aic")
    print(f"  ├── lib/")
    print(f"  ├── tests/")
    print(f"  └── aicode.toml")
    print()
    print(colorize("Get started:", Colors.CYAN))
    print(f"  cd {project_name}")
    print(f"  aic run main.aic")


def cmd_build(args):
    """Kompiliert eine Datei zu Bytecode"""
    input_path = Path(args.file)

    if not input_path.exists():
        print(colorize(f"Error: File not found: {args.file}", Colors.RED))
        sys.exit(1)

    output = args.output if args.output else input_path.stem + ".aicc"

    print(colorize(f"Building {args.file}...", Colors.CYAN))

    try:
        source = read_file(args.file)

        # Parse
        program = parse(source)
        print(colorize("  ✓ Parsed", Colors.GREEN))

        # Compile
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        print(colorize("  ✓ Compiled", Colors.GREEN))

        # Speichern
        with open(output, "wb") as f:
            pickle.dump(module, f)

        print(colorize(f"  ✓ Saved to {output}", Colors.GREEN))

        # Statistiken
        file_size = Path(output).stat().st_size
        print()
        print(colorize(f"Build successful: {file_size} bytes", Colors.GREEN))

    except ParserError as e:
        source_line = get_source_line(args.file, getattr(e, "line", 1))
        print_error(
            args.file,
            getattr(e, "line", 1),
            getattr(e, "column", 1),
            "E201",
            str(e),
            source_line,
        )
        sys.exit(1)
    except Exception as e:
        print(colorize(f"Build Error: {e}", Colors.RED))
        sys.exit(1)


def cmd_run(args):
    """Run an AICode file."""
    source = read_file(args.file)

    try:
        program = parse(source)
        interpreter = Interpreter()
        result = interpreter.interpret(program)

        for line in result:
            print(line)

    except ParserError as e:
        source_line = get_source_line(args.file, getattr(e, "line", 1))
        print_error(
            args.file,
            getattr(e, "line", 1),
            getattr(e, "column", 1),
            "E201",
            str(e),
            source_line,
        )
        sys.exit(1)
    except AICodeError as e:
        print(colorize(f"Runtime Error: {e}", Colors.RED))
        sys.exit(1)
    except Exception as e:
        print(colorize(f"Internal Error: {e}", Colors.RED))
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(2)


def cmd_repl(args):
    """Start the interactive REPL."""
    print(colorize(f"AICode v{__version__} REPL", Colors.CYAN))
    print(colorize("Type 'exit', 'quit', or press Ctrl+D to exit", Colors.GRAY))
    print(colorize("Type 'help' for REPL commands", Colors.GRAY))
    print()

    interpreter = Interpreter()
    multiline_buffer: List[str] = []
    in_multiline = False
    block_keywords = (
        "fn ",
        "if ",
        "else",
        "for ",
        "while ",
        "match ",
        "struct ",
        "enum ",
    )

    while True:
        try:
            if in_multiline:
                prompt = "... "
            else:
                prompt = (
                    ">>> " if args.prompt == "python" else colorize("> ", Colors.CYAN)
                )

            line = input(prompt)

            stripped = line.strip()

            if not in_multiline:
                if stripped in ("exit", "quit"):
                    break
                if stripped == "help":
                    print_repl_help()
                    continue
                if stripped == "clear":
                    print("\n" * 50)
                    continue
                if stripped.startswith("{") and not stripped.endswith("}"):
                    in_multiline = True
                    multiline_buffer = [line]
                    continue
                # Check if line starts a block
                if stripped.startswith(block_keywords) or stripped.endswith(":"):
                    in_multiline = True
                    multiline_buffer = [line]
                    continue
            else:
                multiline_buffer.append(line)
                # Continue until we get a non-indented, non-empty line
                if stripped and not line.startswith(" ") and not line.startswith("\t"):
                    # We have a complete block, process it
                    line = "\n".join(multiline_buffer)
                    in_multiline = False
                    multiline_buffer = []
                elif stripped.endswith("}") and stripped.startswith("{"):
                    # For brace-based multiline
                    line = "\n".join(multiline_buffer)
                    in_multiline = False
                    multiline_buffer = []
                else:
                    continue

            if not stripped:
                continue

            try:
                program = parse(line)
                result = interpreter.interpret(program)
                for output in result:
                    print(output)
            except ParserError as e:
                print(colorize(f"Parse Error: {e}", Colors.RED))
            except AICodeError as e:
                print(colorize(f"Error: {e}", Colors.RED))
            except Exception as e:
                print(colorize(f"Internal Error: {e}", Colors.RED))
                if args.verbose:
                    import traceback

                    traceback.print_exc()

        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            if in_multiline:
                print("\n(Multiline input cancelled)")
                in_multiline = False
                multiline_buffer = []
            else:
                print()
                continue


def print_repl_help():
    """Print REPL help text."""
    print("""
REPL Commands:
  help     Show this help message
  clear    Clear the screen
  exit     Exit the REPL
  quit     Exit the REPL (same as exit)
  
You can enter multiline expressions by starting with '{'.
End with '}' to execute.
""")


def cmd_tokenize(args):
    """Tokenize a file and display tokens."""
    source = read_file(args.file)

    try:
        tokens = tokenize(source)

        print(colorize(f"Tokens from {args.file}:", Colors.CYAN))
        print(colorize("-" * 50, Colors.GRAY))

        for token in tokens:
            token_type = colorize(f"{token.type.name:15}", Colors.YELLOW)
            value = repr(token.value) if token.value is not None else ""
            location = colorize(f"{token.line:3}:{token.column:3}", Colors.GRAY)
            print(f"  {location}  {token_type}  {value}")

        print(colorize("-" * 50, Colors.GRAY))
        print(f"Total tokens: {len(tokens)}")

    except Exception as e:
        print(colorize(f"Error tokenizing file: {e}", Colors.RED))
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_parse(args):
    """Parse a file and display AST."""
    source = read_file(args.file)

    try:
        program = parse(source)

        print(colorize(f"AST from {args.file}:", Colors.CYAN))
        print(colorize("=" * 60, Colors.GRAY))
        print_ast(program)
        print(colorize("=" * 60, Colors.GRAY))

    except ParserError as e:
        source_line = get_source_line(args.file, getattr(e, "line", 1))
        print_error(
            args.file,
            getattr(e, "line", 1),
            getattr(e, "column", 1),
            "E201",
            str(e),
            source_line,
        )
        sys.exit(1)
    except Exception as e:
        print(colorize(f"Error parsing file: {e}", Colors.RED))
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def print_ast(node, indent: int = 0, prefix: str = ""):
    """Print AST node in a formatted way."""
    spacing = "  " * indent
    color = Colors.CYAN if indent == 0 else Colors.YELLOW

    if node is None:
        print(colorize(f"{spacing}{prefix}None", Colors.GRAY))
        return

    node_type = type(node).__name__

    if hasattr(node, "__dataclass_fields__"):
        print(colorize(f"{spacing}{prefix}{node_type}", color))
        for field_name in node.__dataclass_fields__:
            field_value = getattr(node, field_name)
            if field_name.startswith("_"):
                continue

            if field_value is None:
                print(f"{spacing}  {field_name}: None")
            elif isinstance(field_value, list):
                if field_value:
                    print(f"{spacing}  {field_name}: [")
                    for item in field_value:
                        print_ast(item, indent + 2)
                    print(f"{spacing}  ]")
                else:
                    print(f"{spacing}  {field_name}: []")
            elif hasattr(field_value, "__dataclass_fields__"):
                print(f"{spacing}  {field_name}:")
                print_ast(field_value, indent + 2)
            else:
                print(f"{spacing}  {field_name}: {repr(field_value)}")
    elif isinstance(node, (list, tuple)):
        print(colorize(f"{spacing}{prefix}[", Colors.GRAY))
        for item in node:
            print_ast(item, indent + 1)
        print(colorize(f"{spacing}]", Colors.GRAY))
    else:
        print(colorize(f"{spacing}{prefix}{repr(node)}", Colors.GREEN))


def cmd_compile(args):
    """Compile a file to bytecode and display."""
    source = read_file(args.file)

    try:
        program = parse(source)

        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)

        print(colorize(f"Bytecode from {args.file}:", Colors.CYAN))
        print(colorize("=" * 60, Colors.GRAY))

        if args.verbose:
            print("\nConstants:")
            for i, const in enumerate(module.constants):
                print(f"  [{i}] {repr(const)}")

            print("\nGlobal Names:")
            for i, name in enumerate(module.globals):
                print(f"  [{i}] {name}")

        print("\nFunctions:")
        for func in module.functions:
            print(f"\n  Function: {func.name}")
            print(f"  Arity: {func.arity}")
            print(f"  Locals: {func.locals_count}")
            print(f"  Code:")
            for i, instr in enumerate(func.code):
                print(f"    {i:4}: {instr}")

        print(colorize("=" * 60, Colors.GRAY))
        print(f"Compiled {len(module.functions)} function(s)")

    except ParserError as e:
        print(colorize(f"Parse Error: {e}", Colors.RED))
        sys.exit(1)
    except CompilerError as e:
        print(colorize(f"Compilation Error: {e}", Colors.RED))
        sys.exit(1)
    except Exception as e:
        print(colorize(f"Error compiling file: {e}", Colors.RED))
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_check(args):
    """Type check a file without running."""
    source = read_file(args.file)

    def do_check():
        try:
            program = parse(source)

            type_checker = TypeChecker()
            bindings = type_checker.check_program(program)

            if args.verbose:
                print(colorize(f"Type environment for {args.file}:", Colors.CYAN))
                print(colorize("-" * 50, Colors.GRAY))
                for name, scheme in bindings.items():
                    print(f"  {name}: {scheme}")
                print(colorize("-" * 50, Colors.GRAY))

            print(colorize(f"✓ {args.file} passed type checking", Colors.GREEN))
            return True

        except ParserError as e:
            source_line = get_source_line(args.file, getattr(e, "line", 1))
            print_error(
                args.file,
                getattr(e, "line", 1),
                getattr(e, "column", 1),
                "E201",
                str(e),
                source_line,
            )
            return False
        except TCTypeError as e:
            print(colorize(f"✗ Type Error: {e}", Colors.RED))
            return False

    if args.watch:
        print(colorize(f"Watching {args.file} for changes...", Colors.CYAN))
        print(colorize("Press Ctrl+C to stop", Colors.GRAY))
        print()

        last_mtime = 0
        try:
            while True:
                current_mtime = Path(args.file).stat().st_mtime
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    print(
                        colorize(
                            f"[{time.strftime('%H:%M:%S')}] Checking...", Colors.GRAY
                        )
                    )
                    do_check()
                    print()
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print(colorize("Stopped watching", Colors.CYAN))
    else:
        success = do_check()
        sys.exit(0 if success else 1)


def cmd_test(args):
    """Führt Tests aus"""
    test_dir = Path("tests")
    if not test_dir.exists():
        print(colorize("Error: No tests/ directory found", Colors.RED))
        sys.exit(1)

    print(colorize("Running tests...", Colors.CYAN))
    print()

    # Suche Test-Dateien
    if args.pattern:
        test_files = list(test_dir.glob(f"*{args.pattern}*.aic"))
    else:
        test_files = list(test_dir.glob("*.aic"))

    if not test_files:
        print(colorize("No test files found", Colors.YELLOW))
        return

    passed = 0
    failed = 0

    for test_file in sorted(test_files):
        print(colorize(f"Running {test_file}...", Colors.CYAN), end=" ")

        try:
            source = read_file(str(test_file))
            program = parse(source)
            interpreter = Interpreter()
            interpreter.interpret(program)
            print(colorize("✓ PASS", Colors.GREEN))
            passed += 1
        except Exception as e:
            print(colorize("✗ FAIL", Colors.RED))
            if args.verbose:
                print(colorize(f"    Error: {e}", Colors.RED))
            failed += 1

    print()
    total = passed + failed
    if failed == 0:
        print(colorize(f"All {total} tests passed!", Colors.GREEN))
    else:
        print(colorize(f"{passed}/{total} tests passed", Colors.YELLOW))
        print(colorize(f"{failed} tests failed", Colors.RED))


def cmd_format(args):
    """Formatiert eine AICode-Datei"""
    try:
        source = read_file(args.file)

        # Parse um zu validieren
        program = parse(source)

        # Einfache Formatierung
        lines = source.split("\n")
        formatted_lines = []
        indent_level = 0
        indent_size = 2

        for line in lines:
            stripped = line.strip()

            # Reduziere Einrückung für bestimmte Schlüsselwörter am Zeilenanfang
            if stripped.startswith(("else", "elif", "catch", "}")):
                indent_level = max(0, indent_level - 1)

            # Füge Einrückung hinzu
            if stripped:
                formatted_lines.append(" " * (indent_level * indent_size) + stripped)
            else:
                formatted_lines.append("")

            # Erhöhe Einrückung für bestimmte Schlüsselwörter
            if stripped.endswith((":", "{", "(")) or stripped.startswith(
                ("fn", "if", "else", "for", "while", "match", "struct", "enum")
            ):
                if not stripped.endswith(")"):
                    indent_level += 1

            # Reduziere bei schließenden Klammern
            if stripped.endswith(")") or stripped.startswith("}"):
                indent_level = max(0, indent_level - 1)

        formatted = "\n".join(formatted_lines)

        if args.in_place:
            with open(args.file, "w") as f:
                f.write(formatted)
            print(colorize(f"✓ Formatted {args.file}", Colors.GREEN))
        else:
            print(formatted)

    except ParserError as e:
        print(colorize(f"Parse Error (cannot format): {e}", Colors.RED))
        sys.exit(1)


def cmd_install(args):
    """Install a package from local registry or file."""
    pkg_manager = PackageManager()
    
    if args.package:
        name = args.package
        version = args.version or "*"
        
        if args.from_file:
            source = Path(args.from_file)
            if not source.exists():
                print(colorize(f"Error: File not found: {args.from_file}", Colors.RED))
                sys.exit(1)
            pkg_manager.install_package(name, version, source)
            print(colorize(f"✓ Installed {name}@{version} from {args.from_file}", Colors.GREEN))
        else:
            if pkg_manager.registry_index.exists():
                try:
                    import json
                    index = json.loads(pkg_manager.registry_index.read_text())
                    if name in index:
                        for ver, path in sorted(index[name].items()):
                            v = SemverVersion(ver)
                            from src.package_manager import parse_version_constraint
                            if parse_version_constraint(version, v):
                                pkg_manager.install_package(name, ver, Path(path))
                                print(colorize(f"✓ Installed {name}@{ver}", Colors.GREEN))
                                break
                        else:
                            print(colorize(f"No matching version found for {name}@{version}", Colors.YELLOW))
                    else:
                        print(colorize(f"Package {name} not found in registry", Colors.RED))
                        sys.exit(1)
                except Exception as e:
                    print(colorize(f"Error reading registry: {e}", Colors.RED))
                    sys.exit(1)
            else:
                print(colorize("No packages installed yet. Registry is empty.", Colors.YELLOW))
                sys.exit(1)
    else:
        if Path("aicode.toml").exists():
            print(colorize("Installing dependencies from aicode.toml...", Colors.CYAN))
            pkg_manager.install_from_aicode_toml(Path("aicode.toml"))
            print(colorize("✓ All dependencies installed", Colors.GREEN))
        else:
            print(colorize("Error: No package specified and no aicode.toml found", Colors.RED))
            sys.exit(1)


def cmd_list_packages(args):
    """List installed packages."""
    pkg_manager = PackageManager()
    packages = pkg_manager.list_packages()
    
    if not packages:
        print(colorize("No packages installed.", Colors.YELLOW))
        return
    
    print(colorize("Installed packages:", Colors.CYAN))
    print(colorize("-" * 50, Colors.GRAY))
    for pkg in sorted(packages, key=lambda p: p.name):
        print(f"  {pkg.name}@{pkg.version}")
        if pkg.description:
            print(f"    {pkg.description}")


def cmd_remove(args):
    """Remove an installed package."""
    pkg_manager = PackageManager()
    name = args.package
    
    if not pkg_manager.is_installed(name):
        print(colorize(f"Package {name} is not installed", Colors.YELLOW))
        sys.exit(1)
    
    pkg_manager.remove_package(name)
    print(colorize(f"✓ Removed {name}", Colors.GREEN))


def cmd_lsp(args):
    """Start the AICode Language Server Protocol server."""
    from lsp.server import LSPServer
    
    print(colorize("Starting AICode LSP server...", Colors.CYAN))
    server = LSPServer()
    server.start()


def cmd_lint(args):
    """Lint an AICode file."""
    from src.linter import lint_file
    result = lint_file(args.file)
    
    if not result.errors:
        print(colorize(f"✓ No issues found in {args.file}", Colors.GREEN))
        return
    
    error_count = 0
    warning_count = 0
    
    for error in result.errors:
        if error.severity.value == "error":
            error_count += 1
            prefix = colorize("Error", Colors.RED)
        else:
            warning_count += 1
            prefix = colorize("Warning", Colors.YELLOW)
        
        print(f"{prefix} [{error.code}] at {args.file}:{error.line}:{error.column}")
        print(f"  {error.message}")
        if error.suggestion:
            print(f"  Suggestion: {error.suggestion}")
        print()
    
    print(colorize(f"Found {error_count} error(s), {warning_count} warning(s)", 
                   Colors.YELLOW if warning_count > 0 else Colors.GREEN))


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="aic",
        description=f"AICode v{__version__} - A programming language optimized for LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aic init myproject          Create new project
  aic run hello.aic           Run an AICode file
  aic build hello.aic -o out  Compile to bytecode
  aic test                    Run all tests
  aic check hello.aic         Type check a file
  aic check hello.aic --watch Watch mode for type checking
  aic format hello.aic        Format a file
  aic repl                    Start interactive REPL
  aic tokenize hello.aic      Show tokens
  aic parse hello.aic         Show AST
  aic compile hello.aic       Show bytecode

For more information, visit: https://github.com/aicode-ai/aicode
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output and show stack traces",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Create a new AICode project",
        description="Create a new project with standard directory structure.",
    )
    init_parser.add_argument("project_name", help="Name of the new project")

    # run command
    run_parser = subparsers.add_parser(
        "run", help="Run an AICode file", description="Execute an AICode source file."
    )
    run_parser.add_argument("file", help="Path to the AICode source file (.aic)")
    run_parser.add_argument(
        "--arg",
        "-a",
        action="append",
        dest="args",
        help="Pass arguments to the script (can be used multiple times)",
    )

    # repl command
    repl_parser = subparsers.add_parser(
        "repl",
        help="Start interactive REPL",
        description="Start an interactive Read-Eval-Print Loop.",
    )
    repl_parser.add_argument(
        "--prompt",
        choices=["simple", "python"],
        default="simple",
        help="REPL prompt style (default: simple)",
    )

    # tokenize command
    tok_parser = subparsers.add_parser(
        "tokenize",
        help="Tokenize and display tokens",
        description="Tokenize an AICode file and display all tokens.",
    )
    tok_parser.add_argument("file", help="Path to the AICode source file")

    # parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse and display AST",
        description="Parse an AICode file and display the Abstract Syntax Tree.",
    )
    parse_parser.add_argument("file", help="Path to the AICode source file")

    # compile command
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile to bytecode and display",
        description="Compile an AICode file to bytecode and display the result.",
    )
    compile_parser.add_argument("file", help="Path to the AICode source file")
    compile_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output including constants and globals",
    )

    # build command
    build_parser = subparsers.add_parser(
        "build",
        help="Compile to bytecode file",
        description="Compile an AICode file to bytecode and save as .aicc file.",
    )
    build_parser.add_argument("file", help="Path to the AICode source file")
    build_parser.add_argument(
        "-o", "--output", help="Output file (default: <input>.aicc)"
    )

    # check command
    check_parser = subparsers.add_parser(
        "check",
        help="Type check a file without running",
        description="Perform type checking on an AICode file without executing it.",
    )
    check_parser.add_argument("file", help="Path to the AICode source file")
    check_parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch mode - auto-reload on file changes",
    )

    # test command
    test_parser = subparsers.add_parser(
        "test", help="Run tests", description="Run all tests in the tests/ directory."
    )
    test_parser.add_argument(
        "pattern", nargs="?", help="Optional pattern to filter test files"
    )

    # format command
    format_parser = subparsers.add_parser(
        "format",
        help="Format an AICode file",
        description="Format an AICode file with consistent indentation.",
    )
    format_parser.add_argument("file", help="Path to the AICode source file")
    format_parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Format in place (modify the file directly)",
    )

    # install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install a package",
        description="Install a package from registry or local file.",
    )
    install_parser.add_argument("package", nargs="?", help="Package name to install")
    install_parser.add_argument(
        "--version", "-v", help="Version to install (default: latest)"
    )
    install_parser.add_argument(
        "--from-file", "-f", help="Install from local file or directory"
    )

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List installed packages",
        description="List all installed packages.",
    )

    # remove command
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an installed package",
        description="Remove an installed package.",
    )
    remove_parser.add_argument("package", help="Name of the package to remove")

    # lsp command
    lsp_parser = subparsers.add_parser(
        "lsp",
        help="Start the AICode Language Server",
        description="Start the LSP server for IDE integration.",
    )

    # lint command
    lint_parser = subparsers.add_parser(
        "lint",
        help="Lint an AICode file",
        description="Check for unused variables, dead code, and style issues.",
    )
    lint_parser.add_argument("file", help="Path to the AICode source file")

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "init": init_project,
        "run": cmd_run,
        "repl": cmd_repl,
        "tokenize": cmd_tokenize,
        "parse": cmd_parse,
        "compile": cmd_compile,
        "build": cmd_build,
        "check": cmd_check,
        "test": cmd_test,
        "format": cmd_format,
        "install": cmd_install,
        "list": cmd_list_packages,
        "remove": cmd_remove,
        "lsp": cmd_lsp,
        "lint": cmd_lint,
    }

    if args.command in commands:
        if args.command == "init":
            commands[args.command](args.project_name)
        else:
            commands[args.command](args)
    else:
        print(colorize(f"Unknown command: {args.command}", Colors.RED), file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
