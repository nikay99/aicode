"""
AICode-AI AST Nodes
Minimal, compact, designed for AI generation
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any
from enum import Enum, auto


# Forward declarations
class Expr:
    pass


class Stmt:
    pass


class Type:
    pass


# === Types (for Hindley-Milner) ===


@dataclass
class TypeVar(Type):
    """Type variable for polymorphism"""

    id: int
    instance: Optional[Type] = None

    def __repr__(self):
        if self.instance is not None:
            return repr(self.instance)
        return f"t{self.id}"


@dataclass
class TypeConst(Type):
    """Concrete type"""

    name: str

    def __repr__(self):
        return self.name


@dataclass
class TypeArrow(Type):
    """Function type: arg_types -> return_type"""

    arg_types: List[Type]
    return_type: Type

    def __repr__(self):
        args = " ".join(repr(t) for t in self.arg_types)
        return f"({args} -> {self.return_type})"


@dataclass
class TypeList(Type):
    """List type"""

    elem_type: Type

    def __repr__(self):
        return f"[{self.elem_type}]"


@dataclass
class TypeDict(Type):
    """Dict type"""

    key_type: Type
    val_type: Type

    def __repr__(self):
        return f"{{{self.key_type}:{self.val_type}}}"


# Primitive types
TypeInt = TypeConst("ℤ")
TypeFloat = TypeConst("ℝ")
TypeStr = TypeConst("𝕊")
TypeBool = TypeConst("𝔹")
TypeUnit = TypeConst("()")


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
    key: Union[str, Expr]
    value: Expr


@dataclass
class DictExpr(Expr):
    entries: List[DictEntry]


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
    params: List[str]
    body: Expr


@dataclass
class IfExpr(Expr):
    condition: Expr
    then_branch: Expr
    else_branch: Expr


@dataclass
class MatchArm:
    pattern: str  # Simplified: just pattern string
    body: Expr


@dataclass
class MatchExpr(Expr):
    expr: Expr
    arms: List[MatchArm]


@dataclass
class PipeExpr(Expr):
    left: Expr
    right: Expr


# === Statements ===


@dataclass
class VarStmt(Stmt):
    """Variable declaration: 𝕍 name [: type] ≔ value"""

    name: str
    type: Optional[Type]
    value: Expr
    mutable: bool = False


@dataclass
class ConstStmt(Stmt):
    """Constant declaration: 𝔠 name ≔ value"""

    name: str
    value: Expr


@dataclass
class FuncStmt(Stmt):
    """Function declaration: λ name(params) [: return_type] body"""

    name: str
    params: List[tuple]  # (name, type)
    return_type: Optional[Type]
    body: Union[Expr, List[Stmt]]


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
class ForStmt(Stmt):
    var: str
    iterable: Expr
    body: List[Stmt]


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: List[Stmt]


# === Program ===


@dataclass
class Program:
    statements: List[Stmt]
