"""
AICode Linter v1 - Static Code Analysis

Checks for unused variables, dead code, and style violations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from enum import Enum

from src.ast_nodes import (
    Program, Stmt, Expr, FnStmt, StructStmt, EnumStmt, LetStmt,
    ConstStmt, ReturnStmt, ForStmt, WhileStmt, IfExpr, MatchExpr,
    BinaryOp, UnaryOp, CallExpr, FieldAccess, IndexExpr, Identifier,
    ImportStmt, AssignStmt, ExprStmt
)


class LintSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintError:
    code: str
    message: str
    severity: LintSeverity
    line: int
    column: int
    end_line: int
    end_column: int
    suggestion: Optional[str] = None


@dataclass
class LintResult:
    errors: List[LintError] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return any(e.severity == LintSeverity.ERROR for e in self.errors)
    
    @property
    def has_warnings(self) -> bool:
        return any(e.severity == LintSeverity.WARNING for e in self.errors)


class Linter:
    def __init__(self):
        self.errors: List[LintError] = []
        self.defined_vars: Set[str] = set()
        self.used_vars: Set[str] = set()
        self.current_scope_vars: Dict[str, Set[str]] = {"global": set()}
        self.current_scope = "global"
        self.return_statements: List[bool] = []
        self.in_loop = False
    
    def lint(self, source: str) -> LintResult:
        from src.parser import parse
        try:
            program = parse(source)
            return self.lint_program(program)
        except Exception as e:
            return LintResult([LintError(
                code="E999",
                message=f"Parse error: {e}",
                severity=LintSeverity.ERROR,
                line=1,
                column=0,
                end_line=1,
                end_column=1,
            )])
    
    def lint_program(self, program: Program) -> LintResult:
        self.errors = []
        self.defined_vars = set()
        self.used_vars = set()
        self.current_scope_vars = {"global": set()}
        self.current_scope = "global"
        self.return_statements = []
        self.in_loop = False
        
        for stmt in program.statements:
            self.lint_statement(stmt)
        
        self._check_unused_variables()
        return LintResult(self.errors)
    
    def lint_statement(self, stmt: Stmt) -> None:
        if isinstance(stmt, FnStmt):
            self._lint_fn_stmt(stmt)
        elif isinstance(stmt, StructStmt):
            self._lint_struct_stmt(stmt)
        elif isinstance(stmt, EnumStmt):
            self._lint_enum_stmt(stmt)
        elif isinstance(stmt, LetStmt):
            self._lint_let_stmt(stmt)
        elif isinstance(stmt, ConstStmt):
            self._lint_const_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._lint_return_stmt(stmt)
        elif isinstance(stmt, ForStmt):
            self._lint_for_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self._lint_while_stmt(stmt)
        elif isinstance(stmt, ExprStmt):
            self._lint_expression(stmt.expr)
        elif isinstance(stmt, AssignStmt):
            self._lint_assign_stmt(stmt)
        elif isinstance(stmt, ImportStmt):
            pass
    
    def _lint_fn_stmt(self, stmt: FnStmt) -> None:
        if stmt.name in self.current_scope_vars[self.current_scope]:
            self.errors.append(LintError(
                code="W041",
                message=f"Function '{stmt.name}' shadows existing symbol",
                severity=LintSeverity.WARNING,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        
        self.current_scope_vars[self.current_scope].add(stmt.name)
        old_scope = self.current_scope
        self.current_scope = stmt.name
        self.current_scope_vars[self.current_scope] = set()
        self.return_statements.append(False)
        
        for param in stmt.params:
            self.current_scope_vars[self.current_scope].add(param.name)
        
        has_return = False
        for body_stmt in stmt.body:
            self.lint_statement(body_stmt)
            if isinstance(body_stmt, ReturnStmt):
                has_return = True
        
        self.return_statements.pop()
        if not has_return and stmt.return_type:
            self.errors.append(LintError(
                code="W042",
                message=f"Function '{stmt.name}' may not return a value",
                severity=LintSeverity.INFO,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        
        self.current_scope = old_scope
    
    def _lint_struct_stmt(self, stmt: StructStmt) -> None:
        if stmt.name in self.current_scope_vars[self.current_scope]:
            self.errors.append(LintError(
                code="W041",
                message=f"Struct '{stmt.name}' shadows existing symbol",
                severity=LintSeverity.WARNING,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        self.current_scope_vars[self.current_scope].add(stmt.name)
    
    def _lint_enum_stmt(self, stmt: EnumStmt) -> None:
        if stmt.name in self.current_scope_vars[self.current_scope]:
            self.errors.append(LintError(
                code="W041",
                message=f"Enum '{stmt.name}' shadows existing symbol",
                severity=LintSeverity.WARNING,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        self.current_scope_vars[self.current_scope].add(stmt.name)
    
    def _lint_let_stmt(self, stmt: LetStmt) -> None:
        if stmt.name in self.current_scope_vars[self.current_scope]:
            self.errors.append(LintError(
                code="W041",
                message=f"Variable '{stmt.name}' shadows existing symbol",
                severity=LintSeverity.WARNING,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        
        self.current_scope_vars[self.current_scope].add(stmt.name)
        self.defined_vars.add(stmt.name)
        self._lint_expression(stmt.value)
    
    def _lint_const_stmt(self, stmt: ConstStmt) -> None:
        if stmt.name in self.current_scope_vars[self.current_scope]:
            self.errors.append(LintError(
                code="W041",
                message=f"Constant '{stmt.name}' shadows existing symbol",
                severity=LintSeverity.WARNING,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
        
        self.current_scope_vars[self.current_scope].add(stmt.name)
        self.defined_vars.add(stmt.name)
        self._lint_expression(stmt.value)
    
    def _lint_return_stmt(self, stmt: ReturnStmt) -> None:
        if stmt.value:
            self._lint_expression(stmt.value)
        if self.return_statements:
            self.return_statements[-1] = True
    
    def _lint_for_stmt(self, stmt: ForStmt) -> None:
        old_in_loop = self.in_loop
        self.in_loop = True
        
        if stmt.var:
            self.current_scope_vars[self.current_scope].add(stmt.var)
            self.defined_vars.add(stmt.var)
        
        self._lint_expression(stmt.iterable)
        
        for body_stmt in stmt.body:
            self.lint_statement(body_stmt)
        
        self.in_loop = old_in_loop
    
    def _lint_while_stmt(self, stmt: WhileStmt) -> None:
        old_in_loop = self.in_loop
        self.in_loop = True
        
        self._lint_expression(stmt.condition)
        
        for body_stmt in stmt.body:
            self.lint_statement(body_stmt)
        
        self.in_loop = old_in_loop
    
    def _lint_assign_stmt(self, stmt: AssignStmt) -> None:
        self._lint_expression(stmt.value)
        if stmt.name not in self.defined_vars:
            self.errors.append(LintError(
                code="E040",
                message=f"Assignment to undefined variable '{stmt.name}'",
                severity=LintSeverity.ERROR,
                line=1,
                column=0,
                end_line=1,
                end_column=len(stmt.name),
            ))
    
    def _lint_expression(self, expr: Expr) -> None:
        if isinstance(expr, BinaryOp):
            self._lint_expression(expr.left)
            self._lint_expression(expr.right)
            if expr.op in ("==", "!="):
                pass
        elif isinstance(expr, UnaryOp):
            self._lint_expression(expr.operand)
        elif isinstance(expr, CallExpr):
            self._lint_expression(expr.func)
            for arg in expr.args:
                self._lint_expression(arg)
        elif isinstance(expr, FieldAccess):
            self._lint_expression(expr.obj)
        elif isinstance(expr, IndexExpr):
            self._lint_expression(expr.obj)
            self._lint_expression(expr.index)
        elif isinstance(expr, Identifier):
            self.used_vars.add(expr.name)
        elif isinstance(expr, IfExpr):
            self._lint_expression(expr.condition)
            for s in expr.then_branch:
                self.lint_statement(s)
            if isinstance(expr.else_branch, list):
                for s in expr.else_branch:
                    self.lint_statement(s)
            elif isinstance(expr.else_branch, IfExpr):
                self._lint_expression(expr.else_branch)
        elif isinstance(expr, MatchExpr):
            self._lint_expression(expr.expr)
            for arm in expr.arms:
                self._lint_expression(arm.body)
        elif isinstance(expr, ListExpr):
            for e in expr.elements:
                self._lint_expression(e)
        elif isinstance(expr, TupleExpr):
            for e in expr.elements:
                self._lint_expression(e)
        elif isinstance(expr, LambdaExpr):
            old_scope = self.current_scope
            self.current_scope = f"lambda_{id(expr)}"
            self.current_scope_vars[self.current_scope] = set()
            
            for param in expr.params:
                self.current_scope_vars[self.current_scope].add(param.name)
            
            if isinstance(expr.body, list):
                for s in expr.body:
                    self.lint_statement(s)
            else:
                self._lint_expression(expr.body)
            
            self.current_scope = old_scope
    
    def _check_unused_variables(self) -> None:
        for var in self.defined_vars:
            if var not in self.used_vars and not var.startswith("_"):
                self.errors.append(LintError(
                    code="W043",
                    message=f"Variable '{var}' is declared but never used",
                    severity=LintSeverity.WARNING,
                    line=1,
                    column=0,
                    end_line=1,
                    end_column=len(var),
                    suggestion=f"Consider removing '{var}' or using it",
                ))
    
    def check_dead_code(self, program: Program) -> LintResult:
        self.errors = []
        statements = program.statements
        has_return = False
        current_line = 1
        
        for i, stmt in enumerate(statements):
            if has_return:
                self.errors.append(LintError(
                    code="W044",
                    message="Unreachable code after return statement",
                    severity=LintSeverity.WARNING,
                    line=current_line,
                    column=0,
                    end_line=current_line,
                    end_column=10,
                ))
            
            if isinstance(stmt, ReturnStmt):
                has_return = True
            
            current_line += 1
        
        return LintResult(self.errors)


def lint_file(filepath: str) -> LintResult:
    linter = Linter()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    result = linter.lint(source)
    
    from src.parser import parse
    try:
        program = parse(source)
        dead_code_result = linter.check_dead_code(program)
        result.errors.extend(dead_code_result.errors)
    except Exception:
        pass
    
    return result