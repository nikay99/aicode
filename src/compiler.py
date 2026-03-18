"""
AICode v2.0 Bytecode Compiler
Compiles AST to Bytecode
"""

from typing import Dict, List, Optional
import src.ast_nodes as ast
from src.bytecode import (
    OpCode,
    Instruction,
    BytecodeFunction,
    BytecodeModule,
    BytecodeBuilder,
)


class CompilerError(Exception):
    """Compilation error"""

    pass


class LocalScope:
    """Scope for local variables"""

    def __init__(self, parent: Optional["LocalScope"] = None):
        self.variables: Dict[str, int] = {}
        self.parent = parent
        self.offset = parent.offset + len(parent.variables) if parent else 0

    def define(self, name: str) -> int:
        """Define a local variable and return its index"""
        idx = self.offset + len(self.variables)
        self.variables[name] = idx
        return idx

    def resolve(self, name: str) -> Optional[int]:
        """Resolve a variable to its index"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.resolve(name)
        return None


class FunctionCompiler:
    """Compiles a single function"""

    def __init__(self, name: str, arity: int, global_names: Optional[List[str]] = None):
        self.name = name
        self.arity = arity
        self.builder = BytecodeBuilder()
        self.scope = LocalScope()
        self.label_counter = 0
        self.global_names = global_names or []

    def new_label(self) -> str:
        """Generate a new unique label"""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def compile_expr(self, expr: ast.Expr):
        """Compile an expression"""

        if isinstance(expr, ast.IntLiteral):
            self.builder.emit_load_const(expr.value)

        elif isinstance(expr, ast.FloatLiteral):
            self.builder.emit_load_const(expr.value)

        elif isinstance(expr, ast.StringLiteral):
            self.builder.emit_load_const(expr.value)

        elif isinstance(expr, ast.BoolLiteral):
            self.builder.emit_load_const(expr.value)

        elif isinstance(expr, ast.NullLiteral):
            self.builder.emit(OpCode.PUSH_NULL)

        elif isinstance(expr, ast.Identifier):
            idx = self.scope.resolve(expr.name)
            if idx is not None:
                self.builder.emit(OpCode.LOAD_LOCAL, idx)
            else:
                if expr.name in self.global_names:
                    global_idx = self.global_names.index(expr.name)
                    self.builder.emit(OpCode.LOAD_GLOBAL, global_idx)
                else:
                    raise CompilerError(f"Undefined variable: {expr.name}")

        elif isinstance(expr, ast.ListExpr):
            for elem in expr.elements:
                self.compile_expr(elem)
            self.builder.emit(OpCode.BUILD_LIST, len(expr.elements))

        elif isinstance(expr, ast.DictExpr):
            for entry in expr.entries:
                if isinstance(entry.key, str):
                    self.builder.emit_load_const(entry.key)
                else:
                    self.compile_expr(entry.key)
                self.compile_expr(entry.value)
            self.builder.emit(OpCode.BUILD_DICT, len(expr.entries))

        elif isinstance(expr, ast.BinaryOp):
            self.compile_expr(expr.left)
            self.compile_expr(expr.right)

            opcodes = {
                "+": OpCode.ADD,
                "-": OpCode.SUB,
                "*": OpCode.MUL,
                "/": OpCode.DIV,
                "%": OpCode.MOD,
                "==": OpCode.EQ,
                "!=": OpCode.NE,
                "<": OpCode.LT,
                ">": OpCode.GT,
                "<=": OpCode.LE,
                ">=": OpCode.GE,
                "&&": OpCode.AND,
                "||": OpCode.OR,
                "and": OpCode.AND,
                "or": OpCode.OR,
                "=": OpCode.EQ,
                "≠": OpCode.NE,
                "≤": OpCode.LE,
                "≥": OpCode.GE,
                "∧": OpCode.AND,
                "∨": OpCode.OR,
            }

            if expr.op in opcodes:
                self.builder.emit(opcodes[expr.op])
            else:
                raise CompilerError(f"Unknown binary operator: {expr.op}")

        elif isinstance(expr, ast.UnaryOp):
            self.compile_expr(expr.operand)

            if expr.op == "-":
                self.builder.emit(OpCode.NEG)
            elif expr.op in ("!", "not", "¬"):
                self.builder.emit(OpCode.NOT)
            else:
                raise CompilerError(f"Unknown unary operator: {expr.op}")

        elif isinstance(expr, ast.CallExpr):
            self.compile_expr(expr.func)
            for arg in expr.args:
                self.compile_expr(arg)
            self.builder.emit(OpCode.CALL, len(expr.args))

        elif isinstance(expr, ast.FieldAccess):
            self.compile_expr(expr.obj)
            idx = self.builder.emit_const(expr.field)
            self.builder.emit(OpCode.GET_ATTR, idx)

        elif isinstance(expr, ast.IndexExpr):
            self.compile_expr(expr.obj)
            self.compile_expr(expr.index)
            self.builder.emit(OpCode.INDEX_GET)

        elif isinstance(expr, ast.IfExpr):
            else_label = self.new_label()
            end_label = self.new_label()

            self.compile_expr(expr.condition)
            self.builder.emit_jump(OpCode.JUMP_IF_FALSE, else_label)

            for stmt in expr.then_branch:
                self.compile_stmt(stmt)
            self.builder.emit(OpCode.PUSH_NULL)
            self.builder.emit_jump(OpCode.JUMP, end_label)

            self.builder.label(else_label)
            if expr.else_branch:
                if isinstance(expr.else_branch, ast.IfExpr):
                    self.compile_expr(expr.else_branch)
                else:
                    for stmt in expr.else_branch:
                        self.compile_stmt(stmt)
                    self.builder.emit(OpCode.PUSH_NULL)
            else:
                self.builder.emit(OpCode.PUSH_NULL)

            self.builder.label(end_label)

        elif isinstance(expr, ast.LambdaExpr):
            lambda_compiler = FunctionCompiler(
                "<lambda>", len(expr.params), self.global_names
            )

            for param in expr.params:
                param_name = param.name if hasattr(param, "name") else str(param)
                lambda_compiler.scope.define(param_name)

            lambda_compiler.compile_expr(expr.body)
            lambda_compiler.builder.emit(OpCode.RETURN_VALUE)

            lam_locals = lambda_compiler.scope.offset + len(
                lambda_compiler.scope.variables
            )
            lam_func = lambda_compiler.builder.build(
                "<lambda>", len(expr.params), lam_locals
            )
            self.builder.emit_load_const(lam_func)

        elif isinstance(expr, ast.MatchExpr):
            self.compile_expr(expr.expr)

            end_label = self.new_label()

            for arm in expr.arms:
                next_label = self.new_label()
                pattern = arm.pattern

                if isinstance(pattern, ast.WildcardPattern):
                    self.builder.emit(OpCode.POP)
                    self.compile_expr(arm.body)
                    self.builder.emit_jump(OpCode.JUMP, end_label)
                    self.builder.label(next_label)

                elif isinstance(pattern, ast.LiteralPattern):
                    self.builder.emit(OpCode.DUP)
                    self.compile_expr(pattern.value)
                    self.builder.emit(OpCode.EQ)
                    self.builder.emit_jump(OpCode.JUMP_IF_FALSE, next_label)
                    self.builder.emit(OpCode.POP)
                    self.compile_expr(arm.body)
                    self.builder.emit_jump(OpCode.JUMP, end_label)
                    self.builder.label(next_label)

                elif isinstance(pattern, ast.IdentifierPattern):
                    if pattern.name == "_":
                        self.builder.emit(OpCode.POP)
                        self.compile_expr(arm.body)
                        self.builder.emit_jump(OpCode.JUMP, end_label)
                        self.builder.label(next_label)
                    else:
                        idx = self.scope.define(pattern.name)
                        self.builder.emit(OpCode.STORE_LOCAL, idx)
                        self.compile_expr(arm.body)
                        self.builder.emit_jump(OpCode.JUMP, end_label)
                        self.builder.label(next_label)

                else:
                    self.builder.emit(OpCode.POP)
                    self.compile_expr(arm.body)
                    self.builder.emit_jump(OpCode.JUMP, end_label)
                    self.builder.label(next_label)

            self.builder.emit(OpCode.POP)
            self.builder.emit(OpCode.PUSH_NULL)
            self.builder.label(end_label)

        else:
            raise CompilerError(f"Unsupported expression: {type(expr).__name__}")

    def compile_stmt(self, stmt: ast.Stmt):
        """Compile a statement"""

        if isinstance(stmt, ast.LetStmt):
            self.compile_expr(stmt.value)
            idx = self.scope.define(stmt.name)
            self.builder.emit(OpCode.STORE_LOCAL, idx)

        elif isinstance(stmt, ast.AssignStmt):
            self.compile_expr(stmt.value)
            idx = self.scope.resolve(stmt.name)
            if idx is not None:
                self.builder.emit(OpCode.STORE_LOCAL, idx)
            else:
                if stmt.name in self.global_names:
                    global_idx = self.global_names.index(stmt.name)
                else:
                    self.global_names.append(stmt.name)
                    global_idx = len(self.global_names) - 1
                self.builder.emit(OpCode.STORE_GLOBAL, global_idx)

        elif isinstance(stmt, ast.ExprStmt):
            self.compile_expr(stmt.expr)
            self.builder.emit(OpCode.POP)  # Pop unused expression value

        elif isinstance(stmt, ast.ReturnStmt):
            if stmt.value:
                self.compile_expr(stmt.value)
                self.builder.emit(OpCode.RETURN_VALUE)
            else:
                self.builder.emit(OpCode.RETURN)

        elif isinstance(stmt, ast.ForStmt):
            # For loop compilation
            start_label = self.new_label()
            end_label = self.new_label()

            # Create iterator
            self.compile_expr(stmt.iterable)
            self.builder.emit(OpCode.ITER)

            # Define loop variable
            var_idx = self.scope.define(stmt.var)

            self.builder.label(start_label)

            # Get next item or exit
            self.builder.emit_jump(OpCode.ITER_NEXT, end_label)
            self.builder.emit(OpCode.STORE_LOCAL, var_idx)

            # Body
            for s in stmt.body:
                self.compile_stmt(s)

            self.builder.emit_jump(OpCode.JUMP, start_label)
            self.builder.label(end_label)

        elif isinstance(stmt, ast.WhileStmt):
            start_label = self.new_label()
            end_label = self.new_label()

            self.builder.label(start_label)

            # Condition
            self.compile_expr(stmt.condition)
            self.builder.emit_jump(OpCode.JUMP_IF_FALSE, end_label)

            # Body
            for s in stmt.body:
                self.compile_stmt(s)

            self.builder.emit_jump(OpCode.JUMP, start_label)
            self.builder.label(end_label)

        elif isinstance(stmt, ast.FnStmt):
            # Nested function - compile separately
            func_compiler = FunctionCompiler(stmt.name, len(stmt.params))

            for param in stmt.params:
                func_compiler.scope.define(param.name)

            for s in stmt.body:
                func_compiler.compile_stmt(s)

            # Ensure return
            func_compiler.builder.emit(OpCode.RETURN)

            # TODO: Add to module

        else:
            raise CompilerError(f"Unsupported statement: {type(stmt).__name__}")

    def compile(self, body: List[ast.Stmt]) -> BytecodeFunction:
        for stmt in body:
            self.compile_stmt(stmt)

        if not self.builder.code or self.builder.code[-1].opcode not in (
            OpCode.RETURN,
            OpCode.RETURN_VALUE,
        ):
            self.builder.emit(OpCode.PUSH_NULL)
            self.builder.emit(OpCode.RETURN_VALUE)

        locals_count = self.scope.offset + len(self.scope.variables)
        return self.builder.build(self.name, self.arity, locals_count)


class BytecodeCompiler:
    """Main compiler that compiles entire programs"""

    def __init__(self):
        self.module = BytecodeModule()
        self.global_vars: set = set()

    def compile_program(self, program: ast.Program) -> BytecodeModule:
        """Compile a full program to bytecode"""
        # Collect all global variables and functions
        for stmt in program.statements:
            if isinstance(stmt, ast.LetStmt):
                self.global_vars.add(stmt.name)
            elif isinstance(stmt, ast.ConstStmt):
                self.global_vars.add(stmt.name)
            elif isinstance(stmt, ast.FnStmt):
                self.global_vars.add(stmt.name)

        # Add built-in functions to globals
        builtins = [
            "print",
            "println",
            "map",
            "filter",
            "reduce",
            "length",
            "range",
            "str",
            "int",
            "float",
            "keys",
            "values",
            "Ok",
            "Err",
            "is_ok",
            "is_err",
            "unwrap",
            "unwrap_or",
        ]
        self.module.globals = builtins + list(self.global_vars)

        # Compile functions
        for stmt in program.statements:
            if isinstance(stmt, ast.FnStmt):
                self._compile_function(stmt)

        # Compile main function (top-level code)
        main_compiler = FunctionCompiler("__main__", 0, self.module.globals)

        for stmt in program.statements:
            if not isinstance(stmt, ast.FnStmt):
                main_compiler.compile_stmt(stmt)

        # Add final halt
        main_compiler.builder.emit(OpCode.HALT)

        main_locals = main_compiler.scope.offset + len(main_compiler.scope.variables)
        main_func = main_compiler.builder.build("__main__", 0, main_locals)
        self.module.entry_point = self.module.add_function(main_func)

        return self.module

    def _compile_function(self, stmt: ast.FnStmt):
        compiler = FunctionCompiler(stmt.name, len(stmt.params), self.module.globals)

        for param in stmt.params:
            compiler.scope.define(param.name)

        for s in stmt.body:
            compiler.compile_stmt(s)

        if not compiler.builder.code or compiler.builder.code[-1].opcode not in (
            OpCode.RETURN,
            OpCode.RETURN_VALUE,
        ):
            compiler.builder.emit(OpCode.PUSH_NULL)
            compiler.builder.emit(OpCode.RETURN_VALUE)

        func_locals = compiler.scope.offset + len(compiler.scope.variables)
        func = compiler.builder.build(stmt.name, len(stmt.params), func_locals)
        self.module.add_function(func)
