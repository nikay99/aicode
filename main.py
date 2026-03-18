#!/usr/bin/env python3
"""
AICode CLI - Command Line Interface for AICode Programming Language

AICode is a programming language designed specifically for LLMs, using mathematical
Unicode symbols to achieve 40-60% token reduction compared to Python.

Usage:
    aic run <file>       Run an AICode file
    aic repl             Start interactive REPL
    aic tokenize <file>  Tokenize and display tokens
    aic parse <file>     Parse and display AST
    aic compile <file>   Compile to bytecode and display
    aic check <file>     Type check a file without running
    aic --version        Show version
    aic --help           Show help
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src import __version__
from src.lexer import tokenize, Token, TokenType
from src.parser import parse, ParseError
from src.interpreter import Interpreter, AICodeError
from src.compiler import BytecodeCompiler, CompilerError
from src.vm import VirtualMachine, VMError
from src.bytecode import BytecodeModule
from src.type_checker import TypeChecker


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
        print(f"Error: Could not decode file (expected UTF-8): {filepath}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def format_token(token: Token) -> str:
    """Format a token for display."""
    value_str = f" = {token.value!r}" if token.value is not None and token.value != token.type.name else ""
    return f"{token.line:4}:{token.column:3}  {token.type.name:15} {value_str}"


def cmd_run(args):
    """Run an AICode file."""
    source = read_file(args.file)
    
    try:
        program = parse(source)
        interpreter = Interpreter()
        result = interpreter.interpret(program)
        
        for line in result:
            print(line)
            
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except AICodeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Internal Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


def cmd_repl(args):
    """Start the interactive REPL."""
    print(f"AICode v{__version__} REPL")
    print("Type 'exit', 'quit', or press Ctrl+D to exit")
    print("Type 'help' for REPL commands")
    print()
    
    interpreter = Interpreter()
    multiline_buffer: List[str] = []
    in_multiline = False
    
    while True:
        try:
            if in_multiline:
                prompt = "... "
            else:
                prompt = ">>> " if args.prompt == "python" else "> "
            
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
            else:
                multiline_buffer.append(line)
                if stripped.endswith("}"):
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
            except ParseError as e:
                print(f"Parse Error: {e}")
            except AICodeError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Internal Error: {e}")
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
        
        print(f"Tokens from {args.file}:")
        print("-" * 50)
        
        for token in tokens:
            print(format_token(token))
            
        print("-" * 50)
        print(f"Total tokens: {len(tokens)}")
        
    except Exception as e:
        print(f"Error tokenizing file: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_parse(args):
    """Parse a file and display AST."""
    source = read_file(args.file)
    
    try:
        program = parse(source)
        
        print(f"AST from {args.file}:")
        print("=" * 60)
        print_ast(program)
        print("=" * 60)
        
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_ast(node, indent: int = 0, prefix: str = ""):
    """Print AST node in a formatted way."""
    spacing = "  " * indent
    
    if node is None:
        print(f"{spacing}{prefix}None")
        return
    
    node_type = type(node).__name__
    
    if hasattr(node, "__dataclass_fields__"):
        print(f"{spacing}{prefix}{node_type}")
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
        print(f"{spacing}{prefix}[")
        for item in node:
            print_ast(item, indent + 1)
        print(f"{spacing}]")
    else:
        print(f"{spacing}{prefix}{repr(node)}")


def cmd_compile(args):
    """Compile a file to bytecode and display."""
    source = read_file(args.file)
    
    try:
        program = parse(source)
        
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)
        
        print(f"Bytecode from {args.file}:")
        print("=" * 60)
        
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
        
        print("=" * 60)
        print(f"Compiled {len(module.functions)} function(s)")
        
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except CompilerError as e:
        print(f"Compilation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error compiling file: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_check(args):
    """Type check a file without running."""
    source = read_file(args.file)

    try:
        program = parse(source)

        type_checker = TypeChecker()
        bindings = type_checker.check_program(program)

        if args.verbose:
            print(f"Type environment for {args.file}:")
            print("-" * 50)
            for name, scheme in bindings.items():
                print(f"  {name}: {scheme}")
            print("-" * 50)

        print(f"✓ {args.file} passed type checking")

    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except TypeError as e:
        print(f"Type Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during type checking: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="aic",
        description=f"AICode v{__version__} - A programming language optimized for LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aic run hello.aic          Run an AICode file
  aic repl                   Start interactive REPL
  aic tokenize hello.aic     Show tokens
  aic parse hello.aic        Show AST
  aic compile hello.aic      Show bytecode
  aic check hello.aic        Type check only

For more information, visit: https://github.com/aicode-ai/aicode
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output and show stack traces"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run an AICode file",
        description="Execute an AICode source file."
    )
    run_parser.add_argument(
        "file",
        help="Path to the AICode source file (.aic)"
    )
    run_parser.add_argument(
        "--arg", "-a",
        action="append",
        dest="args",
        help="Pass arguments to the script (can be used multiple times)"
    )
    
    # repl command
    repl_parser = subparsers.add_parser(
        "repl",
        help="Start interactive REPL",
        description="Start an interactive Read-Eval-Print Loop."
    )
    repl_parser.add_argument(
        "--prompt",
        choices=["simple", "python"],
        default="simple",
        help="REPL prompt style (default: simple)"
    )
    
    # tokenize command
    tok_parser = subparsers.add_parser(
        "tokenize",
        help="Tokenize and display tokens",
        description="Tokenize an AICode file and display all tokens."
    )
    tok_parser.add_argument(
        "file",
        help="Path to the AICode source file"
    )
    
    # parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse and display AST",
        description="Parse an AICode file and display the Abstract Syntax Tree."
    )
    parse_parser.add_argument(
        "file",
        help="Path to the AICode source file"
    )
    
    # compile command
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile to bytecode and display",
        description="Compile an AICode file to bytecode and display the result."
    )
    compile_parser.add_argument(
        "file",
        help="Path to the AICode source file"
    )
    compile_parser.add_argument(
        "--output", "-o",
        help="Write bytecode to file instead of displaying"
    )
    
    # check command
    check_parser = subparsers.add_parser(
        "check",
        help="Type check a file without running",
        description="Perform type checking on an AICode file without executing it."
    )
    check_parser.add_argument(
        "file",
        help="Path to the AICode source file"
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    commands = {
        "run": cmd_run,
        "repl": cmd_repl,
        "tokenize": cmd_tokenize,
        "parse": cmd_parse,
        "compile": cmd_compile,
        "check": cmd_check,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
