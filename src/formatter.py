"""
AICode Formatter v2 - AST-based Code Formatter

Formats AICode source code based on AST structure for proper indentation
and consistent style.
"""

from typing import List, Optional, Dict, Any
from src.ast_nodes import (
    Program, Stmt, Expr, FnStmt, StructStmt, EnumStmt, LetStmt, 
    ConstStmt, ReturnStmt, ForStmt, WhileStmt, IfExpr, MatchExpr,
    BinaryOp, UnaryOp, CallExpr, FieldAccess, IndexExpr, ListExpr,
    TupleExpr, DictExpr, LambdaExpr, PipeExpr
)


class FormatterError(Exception):
    """Formatter error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AICodeFormatter:
    def __init__(self, indent_size: int = 2, max_line_length: int = 100):
        self.indent_size = indent_size
        self.max_line_length = max_line_length
    
    def format(self, source: str) -> str:
        from src.parser import parse
        try:
            program = parse(source)
            return self.format_program(program)
        except Exception as e:
            raise FormatterError(f"Failed to parse source: {e}")
    
    def format_program(self, program: Program) -> str:
        lines = []
        for stmt in program.statements:
            lines.extend(self.format_statement(stmt))
        return "\n".join(lines) + "\n"
    
    def format_statement(self, stmt: Stmt, indent: int = 0) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        
        if isinstance(stmt, FnStmt):
            return self.format_fn_stmt(stmt, indent)
        elif isinstance(stmt, StructStmt):
            return self.format_struct_stmt(stmt, indent)
        elif isinstance(stmt, EnumStmt):
            return self.format_enum_stmt(stmt, indent)
        elif isinstance(stmt, LetStmt):
            return self.format_let_stmt(stmt, indent)
        elif isinstance(stmt, ConstStmt):
            return self.format_const_stmt(stmt, indent)
        elif isinstance(stmt, ReturnStmt):
            return self.format_return_stmt(stmt, indent)
        elif isinstance(stmt, ForStmt):
            return self.format_for_stmt(stmt, indent)
        elif isinstance(stmt, WhileStmt):
            return self.format_while_stmt(stmt, indent)
        elif isinstance(stmt, ExprStmt):
            expr_str = self.format_expression(stmt.expr)
            return [f"{prefix}{expr_str}"]
        else:
            return [f"{prefix}# Unknown statement"]
    
    def format_fn_stmt(self, stmt: FnStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        lines = []
        
        params_str = ", ".join(self.format_param(p) for p in stmt.params)
        if stmt.return_type:
            lines.append(f"{prefix}fn {stmt.name}({params_str}) -> {stmt.return_type.name} {{")
        else:
            lines.append(f"{prefix}fn {stmt.name}({params_str}) {{")
        
        for body_stmt in stmt.body:
            body_lines = self.format_statement(body_stmt, indent + 1)
            lines.extend(body_lines)
        
        lines.append(f"{prefix}}}")
        return lines
    
    def format_param(self, param) -> str:
        if hasattr(param, 'type') and param.type:
            return f"{param.name}: {param.type.name}"
        return param.name
    
    def format_struct_stmt(self, stmt: StructStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        lines = [f"{prefix}struct {stmt.name} {{"]
        
        for field in stmt.fields:
            type_hint = f": {field.type.name}" if field.type else ""
            lines.append(f"{prefix}  {field.name}{type_hint},")
        
        lines.append(f"{prefix}}}")
        return lines
    
    def format_enum_stmt(self, stmt: EnumStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        lines = [f"{prefix}enum {stmt.name} {{"]
        
        for variant in stmt.variants:
            if variant.fields:
                fields_str = ", ".join(self.format_param(f) for f in variant.fields)
                lines.append(f"{prefix}  {variant.name}({fields_str}),")
            else:
                lines.append(f"{prefix}  {variant.name},")
        
        lines.append(f"{prefix}}}")
        return lines
    
    def format_let_stmt(self, stmt: LetStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        mut_kw = "mut " if stmt.mutable else ""
        type_hint = f": {stmt.type.name}" if stmt.type else ""
        value_str = self.format_expression(stmt.value)
        return [f"{prefix}let {mut_kw}{stmt.name}{type_hint} = {value_str}"]
    
    def format_const_stmt(self, stmt: ConstStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        value_str = self.format_expression(stmt.value)
        return [f"{prefix}const {stmt.name} = {value_str}"]
    
    def format_return_stmt(self, stmt: ReturnStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        if stmt.value:
            value_str = self.format_expression(stmt.value)
            return [f"{prefix}return {value_str}"]
        return [f"{prefix}return"]
    
    def format_for_stmt(self, stmt: ForStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        iterable_str = self.format_expression(stmt.iterable)
        lines = [f"{prefix}for {stmt.var} in {iterable_str} {{"]
        
        for body_stmt in stmt.body:
            body_lines = self.format_statement(body_stmt, indent + 1)
            lines.extend(body_lines)
        
        lines.append(f"{prefix}}}")
        return lines
    
    def format_while_stmt(self, stmt: WhileStmt, indent: int) -> List[str]:
        prefix = " " * (indent * self.indent_size)
        cond_str = self.format_expression(stmt.condition)
        lines = [f"{prefix}while {cond_str} {{"]
        
        for body_stmt in stmt.body:
            body_lines = self.format_statement(body_stmt, indent + 1)
            lines.extend(body_lines)
        
        lines.append(f"{prefix}}}")
        return lines
    
    def format_expression(self, expr: Expr) -> str:
        if isinstance(expr, BinaryOp):
            left = self.format_expression(expr.left)
            right = self.format_expression(expr.right)
            return f"({left} {expr.op} {right})"
        elif isinstance(expr, UnaryOp):
            operand = self.format_expression(expr.operand)
            if expr.op == "not":
                return f"(not {operand})"
            return f"({expr.op}{operand})"
        elif isinstance(expr, CallExpr):
            func_str = self.format_expression(expr.func)
            args_str = ", ".join(self.format_expression(a) for a in expr.args)
            return f"{func_str}({args_str})"
        elif isinstance(expr, FieldAccess):
            obj_str = self.format_expression(expr.obj)
            return f"{obj_str}.{expr.field}"
        elif isinstance(expr, IndexExpr):
            obj_str = self.format_expression(expr.obj)
            index_str = self.format_expression(expr.index)
            return f"{obj_str}[{index_str}]"
        elif isinstance(expr, ListExpr):
            elements_str = ", ".join(self.format_expression(e) for e in expr.elements)
            return f"[{elements_str}]"
        elif isinstance(expr, TupleExpr):
            elements_str = ", ".join(self.format_expression(e) for e in expr.elements)
            return f"({elements_str})"
        elif isinstance(expr, DictExpr):
            entries_str = ", ".join(
                f"{self.format_expression(k)}: {self.format_expression(v)}"
                for k, v in expr.entries
            )
            return f"{{{entries_str}}}"
        elif isinstance(expr, LambdaExpr):
            params_str = ", ".join(self.format_param(p) for p in expr.params)
            body_str = self.format_expression(expr.body)
            if expr.return_type:
                return f"lambda ({params_str}) -> {expr.return_type.name} {body_str}"
            return f"lambda ({params_str}) {body_str}"
        elif isinstance(expr, PipeExpr):
            left = self.format_expression(expr.left)
            right = self.format_expression(expr.right)
            return f"{left} |> {right}"
        elif isinstance(expr, IfExpr):
            return self.format_if_expr(expr)
        elif isinstance(expr, MatchExpr):
            return self.format_match_expr(expr)
        elif isinstance(expr, Identifier):
            return expr.name
        elif hasattr(expr, 'value'):
            return repr(expr.value)
        else:
            return "?"
    
    def format_if_expr(self, expr: IfExpr) -> str:
        cond = self.format_expression(expr.condition)
        then_branch = self.format_expression(expr.then_branch[0]) if expr.then_branch else "?"
        
        if isinstance(expr.else_branch, list):
            else_branch = self.format_expression(expr.else_branch[0]) if expr.else_branch else "?"
        elif isinstance(expr.else_branch, IfExpr):
            else_branch = self.format_if_expr(expr.else_branch)
        else:
            else_branch = "?"
        
        return f"if {cond} then {then_branch} else {else_branch}"
    
    def format_match_expr(self, expr: MatchExpr) -> str:
        expr_str = self.format_expression(expr.expr)
        arms = []
        for arm in expr.arms:
            pattern = self.format_pattern(arm.pattern)
            body = self.format_expression(arm.body)
            arms.append(f"{pattern} => {body}")
        return f"match {expr_str} {{ {', '.join(arms)} }}"
    
    def format_pattern(self, pattern) -> str:
        if hasattr(pattern, 'value'):
            return self.format_expression(pattern.value)
        elif hasattr(pattern, 'name'):
            return pattern.name
        return "?"
    
    def format_document(self, source: str) -> str:
        try:
            from src.parser import parse
            program = parse(source)
            return self.format_program(program)
        except Exception as e:
            raise FormatterError(f"Failed to format document: {e}")


def format_file(input_path: str, output_path: Optional[str] = None, in_place: bool = False) -> str:
    formatter = AICodeFormatter()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    formatted = formatter.format(source)
    
    if in_place:
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
    elif output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
    
    return formatted