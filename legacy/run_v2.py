"""
AICode v2.0 Runner - Compile and Execute
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lexer import tokenize
from src.parser import parse
from src.type_checker import type_check, TypeChecker
from src.compiler import BytecodeCompiler
from src.vm import VirtualMachine
from src.bytecode import BytecodeModule


def run_with_types(source: str, verbose: bool = False):
    """Parse, type check, compile and run source code"""

    # Parse
    if verbose:
        print("=== Parsing ===")
    program = parse(source)
    if verbose:
        print("✓ Parsed successfully")

    # Type check
    if verbose:
        print("\n=== Type Checking ===")
    checker = TypeChecker()
    bindings = checker.check_program(program)
    if verbose:
        print("✓ Type checking passed")
        print("\nInferred types:")
        for name, typ in bindings.items():
            print(f"  {name}: {typ}")

    # Compile
    if verbose:
        print("\n=== Compiling ===")
    compiler = BytecodeCompiler()
    module = compiler.compile_program(program)
    if verbose:
        print("✓ Compilation successful")
        print("\n" + module.disassemble())

    # Execute
    if verbose:
        print("=== Executing ===")
    vm = VirtualMachine()
    try:
        vm.run(module)
        print("✓ Execution completed")
    except Exception as e:
        print(f"✗ Runtime error: {e}")
        raise


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="AICode v2.0 - Type-checked Bytecode Compiler"
    )
    parser.add_argument("file", nargs="?", help="AICode source file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--type-only", action="store_true", help="Only type check, do not run"
    )
    parser.add_argument("--disassemble", action="store_true", help="Show bytecode")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            source = f.read()

        # Parse
        program = parse(source)

        # Type check
        checker = TypeChecker()
        bindings = checker.check_program(program)

        if args.verbose or args.type_only:
            print("Inferred types:")
            for name, typ in sorted(bindings.items()):
                print(f"  {name}: {typ}")

        if args.type_only:
            return

        # Compile
        compiler = BytecodeCompiler()
        module = compiler.compile_program(program)

        if args.disassemble:
            print(module.disassemble())
            return

        # Run
        vm = VirtualMachine()
        vm.run(module)
    else:
        # REPL
        print("AICode v2.0 REPL (Type-checked Bytecode Compiler)")
        print("Type 'exit' to quit")
        print()

        env = {}

        while True:
            try:
                line = input("> ")
                if line.strip() == "exit":
                    break

                if not line.strip():
                    continue

                try:
                    # Parse
                    program = parse(line)

                    # Type check
                    checker = TypeChecker()
                    bindings = checker.check_program(program)

                    # Compile
                    compiler = BytecodeCompiler()
                    module = compiler.compile_program(program)

                    # Run
                    vm = VirtualMachine()
                    vm.run(module)

                except Exception as e:
                    print(f"Error: {e}")

            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue


if __name__ == "__main__":
    main()
