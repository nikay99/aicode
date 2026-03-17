"""
AICode AST Nodes - Abstrakte Syntaxbaum-Knoten
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum, auto


# Forward declarations für Type Hints
class Expr:
    pass


class Stmt:
    pass


class Type:
    pass


# === Expressions ===


@dataclass
class IntLiteral(Expr):
    value: int


@dataclass
class FloatLiteral(Expr):
    value: float


@dataclass
class StringLiteral(Expr):
    value: str


@dataclass
class BoolLiteral(Expr):
    value: bool


@dataclass
class NullLiteral(Expr):
    pass


@dataclass
class Identifier(Expr):
    name: str


@dataclass
class ListExpr(Expr):
    elements: List[Expr]


@dataclass
class DictEntry:
    key: Union[str, Expr]  # String key oder Expression
    value: Expr


@dataclass
class DictExpr(Expr):
    entries: List[DictEntry]


@dataclass
class TupleExpr(Expr):
    elements: List[Expr]


@dataclass
class FieldAccess(Expr):
    obj: Expr
    field: str


@dataclass
class IndexExpr(Expr):
    obj: Expr
    index: Expr


@dataclass
class CallExpr(Expr):
    func: Expr
    args: List[Expr]


@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass
class LambdaExpr(Expr):
    params: List["Param"]
    return_type: Optional[Type]
    body: Union[Expr, List["Stmt"]]


@dataclass
class IfExpr(Expr):
    condition: Expr
    then_branch: List[Stmt]
    else_branch: Optional[Union[List[Stmt], "IfExpr"]]


@dataclass
class MatchArm:
    pattern: "Pattern"
    body: Expr


@dataclass
class MatchExpr(Expr):
    expr: Expr
    arms: List[MatchArm]


@dataclass
class PipeExpr(Expr):
    left: Expr
    right: Expr


# === Patterns ===


@dataclass
class Pattern:
    pass


@dataclass
class LiteralPattern(Pattern):
    value: Expr


@dataclass
class IdentifierPattern(Pattern):
    name: str


@dataclass
class ConstructorPattern(Pattern):
    name: str
    args: List[Pattern]


@dataclass
class WildcardPattern(Pattern):
    pass


# === Types ===


@dataclass
class SimpleType(Type):
    name: str


@dataclass
class GenericType(Type):
    base: str
    args: List[Type]


@dataclass
class FunctionType(Type):
    param_types: List[Type]
    return_type: Type


# === Statements ===


@dataclass
class Param:
    name: str
    type: Optional[Type]


@dataclass
class LetStmt(Stmt):
    name: str
    type: Optional[Type]
    value: Expr
    mutable: bool = False


@dataclass
class ConstStmt(Stmt):
    name: str
    value: Expr


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class AssignStmt(Stmt):
    name: str
    value: Expr


@dataclass
class FnStmt(Stmt):
    name: str
    params: List[Param]
    return_type: Optional[Type]
    body: List[Stmt]
    exported: bool = False


@dataclass
class StructStmt(Stmt):
    name: str
    fields: List[Param]
    exported: bool = False


@dataclass
class EnumVariant:
    name: str
    fields: Optional[List[Param]]


@dataclass
class EnumStmt(Stmt):
    name: str
    variants: List[EnumVariant]
    exported: bool = False


@dataclass
class ForStmt(Stmt):
    var: str
    iterable: Expr
    body: List[Stmt]


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: List[Stmt]


@dataclass
class ImportStmt(Stmt):
    module: str
    names: Optional[List[str]]
    alias: Optional[str]


# === Program ===


@dataclass
class Program:
    statements: List[Stmt]
