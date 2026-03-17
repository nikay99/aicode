#!/usr/bin/env python3
"""
AICode CLI - Kommandozeilen-Interface
"""

import sys
import argparse
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent))

import src.lexer as lexer
import src.parser as parser
import src.interpreter as interpreter

tokenize = lexer.tokenize
parse = parser.parse
ParseError = parser.ParseError
interpret = interpreter.interpret
Interpreter = interpreter.Interpreter
AICodeError = interpreter.AICodeError


def run_file(filepath: str):
    """Führt eine .aic Datei aus"""
    try:
        with open(filepath, "r") as f:
            source = f.read()

        interpreter = Interpreter()
        program = parse(source)
        result = interpreter.interpret(program)

        # Gib alle Ausgaben aus
        for line in result:
            print(line)

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AICodeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_repl():
    """Startet die REPL"""
    print("AICode v0.1.0 REPL")
    print("Type 'exit' or press Ctrl+D to quit")
    print()

    interpreter = Interpreter()

    while True:
        try:
            line = input("> ")
            if line.strip() == "exit":
                break

            if not line.strip():
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

        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue


def tokenize_file(filepath: str):
    """Zeigt alle Tokens einer Datei"""
    try:
        with open(filepath, "r") as f:
            source = f.read()

        tokens = tokenize(source)
        for token in tokens:
            print(f"{token.line:3}:{token.column:3}  {token}")

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def parse_file(filepath: str):
    """Parst eine Datei und zeigt den AST"""
    try:
        with open(filepath, "r") as f:
            source = f.read()

        program = parse(source)
        print_ast(program)

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_ast(node, indent=0):
    """Gibt den AST formatiert aus"""
    prefix = "  " * indent

    if hasattr(node, "__dict__"):
        print(f"{prefix}{type(node).__name__}")
        for key, value in node.__dict__.items():
            if isinstance(value, list):
                if value:
                    print(f"{prefix}  {key}:")
                    for item in value:
                        print_ast(item, indent + 2)
            elif hasattr(value, "__dict__"):
                print(f"{prefix}  {key}:")
                print_ast(value, indent + 2)
            else:
                print(f"{prefix}  {key}: {value}")
    else:
        print(f"{prefix}{repr(node)}")


def main():
    parser = argparse.ArgumentParser(
        prog="aic", description="AICode - KI-optimierte Programmiersprache"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # run command
    run_parser = subparsers.add_parser("run", help="Run an AICode file")
    run_parser.add_argument("file", help="AICode source file")

    # repl command
    subparsers.add_parser("repl", help="Start interactive REPL")

    # tokenize command
    tok_parser = subparsers.add_parser("tokenize", help="Tokenize a file")
    tok_parser.add_argument("file", help="AICode source file")

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse and show AST")
    parse_parser.add_argument("file", help="AICode source file")

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file)
    elif args.command == "repl":
        run_repl()
    elif args.command == "tokenize":
        tokenize_file(args.file)
    elif args.command == "parse":
        parse_file(args.file)
    else:
        # Default: REPL
        run_repl()


if __name__ == "__main__":
    main()
