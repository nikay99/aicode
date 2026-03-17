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

        # Define parameters as locals
        for i in range(arity):
            self.scope.define(f"_param_{i}")

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
                # Global variable - find index in global names
                if expr.name in self.global_names:
                    global_idx = self.global_names.index(expr.name)
                    self.builder.emit(OpCode.LOAD_GLOBAL, global_idx)
                else:
                    # New global - add it
                    self.global_names.append(expr.name)
                    self.builder.emit(OpCode.LOAD_GLOBAL, len(self.global_names) - 1)

        elif isinstance(expr, ast.ListExpr):
            # Compile elements in reverse order
            for elem in reversed(expr.elements):
                self.compile_expr(elem)
            self.builder.emit(OpCode.BUILD_LIST, len(expr.elements))

        elif isinstance(expr, ast.DictExpr):
            # Compile key-value pairs
            for entry in reversed(expr.entries):
                self.compile_expr(entry.value)
                if isinstance(entry.key, str):
                    self.builder.emit_load_const(entry.key)
                else:
                    self.compile_expr(entry.key)
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
            }

            if expr.op in opcodes:
                self.builder.emit(opcodes[expr.op])
            else:
                raise CompilerError(f"Unknown binary operator: {expr.op}")

        elif isinstance(expr, ast.UnaryOp):
            self.compile_expr(expr.operand)

            if expr.op == "-":
                self.builder.emit(OpCode.NEG)
            elif expr.op in ("!", "not"):
                self.builder.emit(OpCode.NOT)
            else:
                raise CompilerError(f"Unknown unary operator: {expr.op}")

        elif isinstance(expr, ast.CallExpr):
            # Compile arguments
            for arg in expr.args:
                self.compile_expr(arg)
            # Compile function
            self.compile_expr(expr.func)
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

            # Condition
            self.compile_expr(expr.condition)
            self.builder.emit_jump(OpCode.JUMP_IF_FALSE, else_label)

            # Then branch
            for stmt in expr.then_branch:
                self.compile_stmt(stmt)
            self.builder.emit_jump(OpCode.JUMP, end_label)

            # Else branch
            self.builder.label(else_label)
            if expr.else_branch:
                if isinstance(expr.else_branch, ast.IfExpr):
                    self.compile_expr(expr.else_branch)
                else:
                    for stmt in expr.else_branch:
                        self.compile_stmt(stmt)

            self.builder.label(end_label)

        elif isinstance(expr, ast.LambdaExpr):
            # Compile lambda as anonymous function
            lambda_compiler = FunctionCompiler("<lambda>", len(expr.params))

            # Define parameters
            for param in expr.params:
                lambda_compiler.scope.define(param.name)

            # Compile body
            lambda_compiler.compile_expr(expr.body)
            lambda_compiler.builder.emit(OpCode.RETURN_VALUE)

            # TODO: Add function to module and push reference

        elif isinstance(expr, ast.MatchExpr):
            # Compile match expression
            self.compile_expr(expr.expr)

            end_label = self.new_label()
            next_labels = []

            for i, arm in enumerate(expr.arms):
                next_label = self.new_label()
                next_labels.append(next_label)

                # Pattern matching (simplified)
                # TODO: Implement proper pattern matching

                # Body
                self.compile_expr(arm.body)
                self.builder.emit_jump(OpCode.JUMP, end_label)

                self.builder.label(next_label)

            self.builder.label(end_label)

        else:
            raise CompilerError(f"Unsupported expression: {type(expr).__name__}")

    def compile_stmt(self, stmt: ast.Stmt):
        """Compile a statement"""

        if isinstance(stmt, ast.LetStmt):
            self.compile_expr(stmt.value)
            idx = self.scope.define(stmt.name)
            self.builder.emit(OpCode.STORE_LOCAL, idx)
            self.builder.emit(OpCode.POP)  # Pop the value

        elif isinstance(stmt, ast.AssignStmt):
            self.compile_expr(stmt.value)
            idx = self.scope.resolve(stmt.name)
            if idx is not None:
                self.builder.emit(OpCode.STORE_LOCAL, idx)
            else:
                # Global variable - find or add index
                if stmt.name in self.global_names:
                    global_idx = self.global_names.index(stmt.name)
                else:
                    self.global_names.append(stmt.name)
                    global_idx = len(self.global_names) - 1
                self.builder.emit(OpCode.STORE_GLOBAL, global_idx)
            self.builder.emit(OpCode.POP)

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
            self.builder.emit(OpCode.POP)

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
        """Compile function body"""
        for stmt in body:
            self.compile_stmt(stmt)

        # Ensure function returns
        if not self.builder.code or self.builder.code[-1].opcode not in (
            OpCode.RETURN,
            OpCode.RETURN_VALUE,
        ):
            self.builder.emit(OpCode.PUSH_NULL)
            self.builder.emit(OpCode.RETURN_VALUE)

        return self.builder.build(self.name, self.arity)


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

        self.module.globals = list(self.global_vars)

        # Compile functions
        for stmt in program.statements:
            if isinstance(stmt, ast.FnStmt):
                self._compile_function(stmt)

        # Compile main function (top-level code)
        main_compiler = FunctionCompiler("__main__", 0)

        for stmt in program.statements:
            if not isinstance(stmt, ast.FnStmt):
                main_compiler.compile_stmt(stmt)

        # Add final halt
        main_compiler.builder.emit(OpCode.HALT)

        main_func = main_compiler.compile(program.statements)
        self.module.entry_point = self.module.add_function(main_func)

        return self.module

    def _compile_function(self, stmt: ast.FnStmt):
        """Compile a function definition"""
        compiler = FunctionCompiler(stmt.name, len(stmt.params))

        for param in stmt.params:
            compiler.scope.define(param.name)

        for s in stmt.body:
            compiler.compile_stmt(s)

        func = compiler.compile(stmt.body)
        self.module.add_function(func)
