"""
AICode v2.0 Type Checker with Hindley-Milner Type Inference
"""

from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import src.ast_nodes as ast


class TypeVar:
    """Type variable for polymorphism"""

    _counter = 0

    def __init__(self):
        TypeVar._counter += 1
        self.id = TypeVar._counter
        self.instance: Optional["Type"] = None

    def __repr__(self):
        if self.instance is not None:
            return repr(self.instance)
        return f"t{self.id}"


@dataclass
class TypeConst:
    """Concrete type like int, str, bool"""

    name: str

    def __repr__(self):
        return self.name


@dataclass
class TypeArrow:
    """Function type: arg_types -> return_type"""

    arg_types: List["Type"]
    return_type: "Type"

    def __repr__(self):
        args = " ".join(repr(t) for t in self.arg_types)
        return f"({args} -> {self.return_type})"


@dataclass
class TypeList:
    """List type: list<t>"""

    elem_type: "Type"

    def __repr__(self):
        return f"list<{self.elem_type}>"


@dataclass
class TypeDict:
    """Dict type: dict<k, v>"""

    key_type: "Type"
    val_type: "Type"

    def __repr__(self):
        return f"dict<{self.key_type}, {self.val_type}>"


# Primitive types
TypeInt = TypeConst("int")
TypeFloat = TypeConst("float")
TypeStr = TypeConst("str")
TypeBool = TypeConst("bool")
TypeUnit = TypeConst("unit")

Type = Union[TypeVar, TypeConst, TypeArrow, TypeList, TypeDict]


class TypeError(Exception):
    """Type checking error"""

    pass


@dataclass
class Scheme:
    """Polymorphic type scheme with bound variables"""

    vars: List[TypeVar]
    type: Type

    def __repr__(self):
        if not self.vars:
            return repr(self.type)
        vars_str = ", ".join(f"'{v}" for v in self.vars)
        return f"forall [{vars_str}]. {self.type}"


class TypeEnvironment:
    """Type environment mapping names to type schemes"""

    def __init__(self, parent: Optional["TypeEnvironment"] = None):
        self.bindings: Dict[str, Scheme] = {}
        self.parent = parent

    def get(self, name: str) -> Optional[Scheme]:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def set(self, name: str, scheme: Scheme):
        self.bindings[name] = scheme

    def extend(self, name: str, scheme: Scheme) -> "TypeEnvironment":
        new_env = TypeEnvironment(self)
        new_env.set(name, scheme)
        return new_env


class TypeChecker:
    """Hindley-Milner Type Checker"""

    def __init__(self):
        self.env = self._setup_builtins()
        self.constraints: List[Tuple[Type, Type]] = []

    def _setup_builtins(self) -> TypeEnvironment:
        """Setup built-in function types"""
        env = TypeEnvironment()

        # print: forall a. a -> unit
        a = TypeVar()
        env.set("print", Scheme([a], TypeArrow([a], TypeUnit)))
        env.set("println", Scheme([a], TypeArrow([a], TypeUnit)))

        # Arithmetic: int -> int -> int
        env.set("+", Scheme([], TypeArrow([TypeInt, TypeInt], TypeInt)))
        env.set("-", Scheme([], TypeArrow([TypeInt, TypeInt], TypeInt)))
        env.set("*", Scheme([], TypeArrow([TypeInt, TypeInt], TypeInt)))
        env.set("/", Scheme([], TypeArrow([TypeInt, TypeInt], TypeFloat)))
        env.set("%", Scheme([], TypeArrow([TypeInt, TypeInt], TypeInt)))

        # Comparisons: forall a. a -> a -> bool
        a = TypeVar()
        env.set("==", Scheme([a], TypeArrow([a, a], TypeBool)))
        env.set("!=", Scheme([a], TypeArrow([a, a], TypeBool)))
        a = TypeVar()
        env.set("<", Scheme([a], TypeArrow([a, a], TypeBool)))
        a = TypeVar()
        env.set(">", Scheme([a], TypeArrow([a, a], TypeBool)))

        # Logical: bool -> bool -> bool
        env.set("and", Scheme([], TypeArrow([TypeBool, TypeBool], TypeBool)))
        env.set("or", Scheme([], TypeArrow([TypeBool, TypeBool], TypeBool)))
        env.set("not", Scheme([], TypeArrow([TypeBool], TypeBool)))

        # List operations
        a = TypeVar()
        env.set("length", Scheme([a], TypeArrow([TypeList(a)], TypeInt)))

        a = TypeVar()
        b = TypeVar()
        # map: (a -> b) -> list<a> -> list<b>
        env.set(
            "map",
            Scheme([a, b], TypeArrow([TypeArrow([a], b), TypeList(a)], TypeList(b))),
        )

        a = TypeVar()
        # filter: (a -> bool) -> list<a> -> list<a>
        env.set(
            "filter",
            Scheme(
                [a], TypeArrow([TypeArrow([a], TypeBool), TypeList(a)], TypeList(a))
            ),
        )

        a = TypeVar()
        # range: int -> int -> list<int>
        env.set("range", Scheme([], TypeArrow([TypeInt, TypeInt], TypeList(TypeInt))))

        return env

    def fresh_var(self) -> TypeVar:
        """Create a fresh type variable"""
        return TypeVar()

    def generalize(self, env: TypeEnvironment, t: Type) -> Scheme:
        """Generalize a type to a scheme by abstracting over free vars not in env"""
        env_free = self._free_vars_env(env)
        type_free = self._free_vars(t)
        vars_to_generalize = type_free - env_free
        return Scheme(list(vars_to_generalize), t)

    def instantiate(self, scheme: Scheme) -> Type:
        """Instantiate a scheme by replacing bound vars with fresh vars"""
        subst: Dict[TypeVar, Type] = {var: self.fresh_var() for var in scheme.vars}
        return self._apply_subst(subst, scheme.type)

    def _free_vars(self, t: Type) -> Set[TypeVar]:
        """Get free type variables in a type"""
        if isinstance(t, TypeVar):
            if t.instance is not None:
                return self._free_vars(t.instance)
            return {t}
        elif isinstance(t, TypeConst):
            return set()
        elif isinstance(t, TypeArrow):
            free = set()
            for arg in t.arg_types:
                free |= self._free_vars(arg)
            free |= self._free_vars(t.return_type)
            return free
        elif isinstance(t, TypeList):
            return self._free_vars(t.elem_type)
        elif isinstance(t, TypeDict):
            return self._free_vars(t.key_type) | self._free_vars(t.val_type)
        return set()

    def _free_vars_env(self, env: TypeEnvironment) -> Set[TypeVar]:
        """Get free type variables in environment"""
        free = set()
        for scheme in env.bindings.values():
            free |= self._free_vars(scheme.type) - set(scheme.vars)
        if env.parent:
            free |= self._free_vars_env(env.parent)
        return free

    def _apply_subst(self, subst: Dict[TypeVar, Type], t: Type) -> Type:
        """Apply substitution to a type"""
        if isinstance(t, TypeVar):
            if t in subst:
                return subst[t]
            if t.instance is not None:
                return self._apply_subst(subst, t.instance)
            return t
        elif isinstance(t, TypeConst):
            return t
        elif isinstance(t, TypeArrow):
            new_args = [self._apply_subst(subst, arg) for arg in t.arg_types]
            new_ret = self._apply_subst(subst, t.return_type)
            return TypeArrow(new_args, new_ret)
        elif isinstance(t, TypeList):
            return TypeList(self._apply_subst(subst, t.elem_type))
        elif isinstance(t, TypeDict):
            return TypeDict(
                self._apply_subst(subst, t.key_type),
                self._apply_subst(subst, t.val_type),
            )
        return t

    def unify(self, t1: Type, t2: Type):
        """Unify two types, updating type variables"""
        t1 = self._prune(t1)
        t2 = self._prune(t2)

        if isinstance(t1, TypeVar):
            if t1 != t2:
                if self._occurs_in(t1, t2):
                    raise TypeError(f"Occurs check failed: {t1} in {t2}")
                t1.instance = t2
        elif isinstance(t2, TypeVar):
            self.unify(t2, t1)
        elif isinstance(t1, TypeConst) and isinstance(t2, TypeConst):
            if t1.name != t2.name:
                raise TypeError(f"Cannot unify {t1} with {t2}")
        elif isinstance(t1, TypeArrow) and isinstance(t2, TypeArrow):
            if len(t1.arg_types) != len(t2.arg_types):
                raise TypeError(
                    f"Function arity mismatch: {len(t1.arg_types)} vs {len(t2.arg_types)}"
                )
            for a1, a2 in zip(t1.arg_types, t2.arg_types):
                self.unify(a1, a2)
            self.unify(t1.return_type, t2.return_type)
        elif isinstance(t1, TypeList) and isinstance(t2, TypeList):
            self.unify(t1.elem_type, t2.elem_type)
        elif isinstance(t1, TypeDict) and isinstance(t2, TypeDict):
            self.unify(t1.key_type, t2.key_type)
            self.unify(t1.val_type, t2.val_type)
        else:
            raise TypeError(f"Cannot unify {t1} with {t2}")

    def _prune(self, t: Type) -> Type:
        """Follow type variable links"""
        if isinstance(t, TypeVar) and t.instance is not None:
            t.instance = self._prune(t.instance)
            return t.instance
        return t

    def _occurs_in(self, var: TypeVar, t: Type) -> bool:
        """Check if var occurs in t (occurs check)"""
        t = self._prune(t)
        if isinstance(t, TypeVar):
            return t == var
        elif isinstance(t, TypeConst):
            return False
        elif isinstance(t, TypeArrow):
            return any(
                self._occurs_in(var, arg) for arg in t.arg_types
            ) or self._occurs_in(var, t.return_type)
        elif isinstance(t, TypeList):
            return self._occurs_in(var, t.elem_type)
        elif isinstance(t, TypeDict):
            return self._occurs_in(var, t.key_type) or self._occurs_in(var, t.val_type)
        return False

    def infer(self, env: TypeEnvironment, expr: ast.Expr) -> Type:
        """Infer the type of an expression"""

        if isinstance(expr, ast.IntLiteral):
            return TypeInt

        elif isinstance(expr, ast.FloatLiteral):
            return TypeFloat

        elif isinstance(expr, ast.StringLiteral):
            return TypeStr

        elif isinstance(expr, ast.BoolLiteral):
            return TypeBool

        elif isinstance(expr, ast.NullLiteral):
            # Null can be any type (we'll use a fresh var)
            return self.fresh_var()

        elif isinstance(expr, ast.Identifier):
            scheme = env.get(expr.name)
            if scheme is None:
                raise TypeError(f"Unbound variable: {expr.name}")
            return self.instantiate(scheme)

        elif isinstance(expr, ast.BinaryOp):
            t1 = self.infer(env, expr.left)
            t2 = self.infer(env, expr.right)

            if expr.op in ["+", "-", "*", "%"]:
                self.unify(t1, TypeInt)
                self.unify(t2, TypeInt)
                return TypeInt
            elif expr.op == "/":
                self.unify(t1, TypeInt)
                self.unify(t2, TypeInt)
                return TypeFloat
            elif expr.op in ["==", "!=", "<", ">", "<=", ">="]:
                self.unify(t1, t2)  # Must be same type
                return TypeBool
            elif expr.op in ["&&", "||", "and", "or"]:
                self.unify(t1, TypeBool)
                self.unify(t2, TypeBool)
                return TypeBool
            else:
                raise TypeError(f"Unknown operator: {expr.op}")

        elif isinstance(expr, ast.UnaryOp):
            t = self.infer(env, expr.operand)
            if expr.op == "-":
                self.unify(t, TypeInt)
                return TypeInt
            elif expr.op in ["!", "not"]:
                self.unify(t, TypeBool)
                return TypeBool
            else:
                raise TypeError(f"Unknown unary operator: {expr.op}")

        elif isinstance(expr, ast.ListExpr):
            if not expr.elements:
                return TypeList(self.fresh_var())
            elem_type = self.infer(env, expr.elements[0])
            for elem in expr.elements[1:]:
                t = self.infer(env, elem)
                self.unify(elem_type, t)
            return TypeList(elem_type)

        elif isinstance(expr, ast.DictExpr):
            if not expr.entries:
                return TypeDict(self.fresh_var(), self.fresh_var())

            first = expr.entries[0]
            key_type = (
                TypeStr if isinstance(first.key, str) else self.infer(env, first.key)
            )
            val_type = self.infer(env, first.value)

            for entry in expr.entries[1:]:
                if isinstance(entry.key, str):
                    self.unify(key_type, TypeStr)
                else:
                    kt = self.infer(env, entry.key)
                    self.unify(key_type, kt)
                vt = self.infer(env, entry.value)
                self.unify(val_type, vt)

            return TypeDict(key_type, val_type)

        elif isinstance(expr, ast.CallExpr):
            func_type = self.infer(env, expr.func)
            arg_types = [self.infer(env, arg) for arg in expr.args]

            # Create expected function type
            ret_type = self.fresh_var()
            expected = TypeArrow(arg_types, ret_type)

            self.unify(func_type, expected)
            return ret_type

        elif isinstance(expr, ast.FieldAccess):
            obj_type = self.infer(env, expr.obj)
            # Field access on dict
            if isinstance(obj_type, TypeDict):
                return obj_type.val_type
            else:
                # Unknown - create fresh var
                return self.fresh_var()

        elif isinstance(expr, ast.IndexExpr):
            obj_type = self.infer(env, expr.obj)
            index_type = self.infer(env, expr.index)

            if isinstance(obj_type, TypeList):
                self.unify(index_type, TypeInt)
                return obj_type.elem_type
            elif isinstance(obj_type, TypeDict):
                self.unify(index_type, obj_type.key_type)
                return obj_type.val_type
            else:
                return self.fresh_var()

        elif isinstance(expr, ast.LambdaExpr):
            # Create type variables for parameters
            param_types = []
            new_env = env
            for param in expr.params:
                if param.type:
                    # Use explicit type annotation
                    t = self._parse_type_annotation(param.type)
                else:
                    t = self.fresh_var()
                param_types.append(t)
                new_env = new_env.extend(param.name, Scheme([], t))

            body_type = self.infer(new_env, expr.body)
            return TypeArrow(param_types, body_type)

        elif isinstance(expr, ast.IfExpr):
            cond_type = self.infer(env, expr.condition)
            self.unify(cond_type, TypeBool)

            then_type = None
            for stmt in expr.then_branch:
                if isinstance(stmt, ast.ExprStmt):
                    then_type = self.infer(env, stmt.expr)

            if expr.else_branch:
                if isinstance(expr.else_branch, ast.IfExpr):
                    else_type = self.infer(env, expr.else_branch)
                else:
                    else_type = None
                    for stmt in expr.else_branch:
                        if isinstance(stmt, ast.ExprStmt):
                            else_type = self.infer(env, stmt.expr)

                if then_type and else_type:
                    self.unify(then_type, else_type)

            return then_type or self.fresh_var()

        elif isinstance(expr, ast.MatchExpr):
            expr_type = self.infer(env, expr.expr)
            result_type = self.fresh_var()

            for arm in expr.arms:
                # TODO: Pattern type checking
                body_type = self.infer(env, arm.body)
                self.unify(result_type, body_type)

            return result_type

        elif isinstance(expr, ast.PipeExpr):
            # Pipe: left |> right means right(left)
            left_type = self.infer(env, expr.left)

            if isinstance(expr.right, ast.CallExpr):
                # Get function type
                func_type = self.infer(env, expr.right.func)
                arg_types = [left_type] + [
                    self.infer(env, arg) for arg in expr.right.args
                ]
                ret_type = self.fresh_var()
                expected = TypeArrow(arg_types, ret_type)
                self.unify(func_type, expected)
                return ret_type
            else:
                # Simple function call
                func_type = self.infer(env, expr.right)
                ret_type = self.fresh_var()
                expected = TypeArrow([left_type], ret_type)
                self.unify(func_type, expected)
                return ret_type
        else:
            raise TypeError(f"Unsupported expression type: {type(expr).__name__}")

    def _parse_type_annotation(self, type_node: ast.Type) -> Type:
        """Parse a type annotation from AST"""
        if isinstance(type_node, ast.SimpleType):
            if type_node.name == "int":
                return TypeInt
            elif type_node.name == "float":
                return TypeFloat
            elif type_node.name == "str":
                return TypeStr
            elif type_node.name == "bool":
                return TypeBool
            else:
                return TypeConst(type_node.name)
        elif isinstance(type_node, ast.GenericType):
            if type_node.base == "list":
                elem_type = self._parse_type_annotation(type_node.args[0])
                return TypeList(elem_type)
            elif type_node.base == "dict":
                key_type = self._parse_type_annotation(type_node.args[0])
                val_type = self._parse_type_annotation(type_node.args[1])
                return TypeDict(key_type, val_type)
        return self.fresh_var()

    def check_statement(self, env: TypeEnvironment, stmt: ast.Stmt) -> TypeEnvironment:
        """Check a statement and return updated environment"""

        if isinstance(stmt, ast.LetStmt):
            value_type = self.infer(env, stmt.value)

            if stmt.type:
                # Check against explicit type annotation
                annotated = self._parse_type_annotation(stmt.type)
                self.unify(value_type, annotated)

            scheme = self.generalize(env, value_type)
            return env.extend(stmt.name, scheme)

        elif isinstance(stmt, ast.ConstStmt):
            value_type = self.infer(env, stmt.value)
            scheme = self.generalize(env, value_type)
            return env.extend(stmt.name, scheme)

        elif isinstance(stmt, ast.FnStmt):
            # For recursive functions, we need to add the function to env first
            func_var = self.fresh_var()
            env_with_fn = env.extend(stmt.name, Scheme([], func_var))

            # Infer parameter types
            param_types = []
            body_env = env_with_fn
            for param in stmt.params:
                if param.type:
                    t = self._parse_type_annotation(param.type)
                else:
                    t = self.fresh_var()
                param_types.append(t)
                body_env = body_env.extend(param.name, Scheme([], t))

            # Infer return type from body
            # For simplicity, we look at the return statements
            ret_type = self.fresh_var()
            if stmt.return_type:
                ret_type = self._parse_type_annotation(stmt.return_type)

            func_type = TypeArrow(param_types, ret_type)
            self.unify(func_var, func_type)

            # Type check the body
            for s in stmt.body:
                if isinstance(s, ast.ReturnStmt):
                    if s.value:
                        t = self.infer(body_env, s.value)
                        self.unify(t, ret_type)
                else:
                    body_env = self.check_statement(body_env, s)

            scheme = self.generalize(env, func_type)
            return env.extend(stmt.name, scheme)

        elif isinstance(stmt, ast.ExprStmt):
            self.infer(env, stmt.expr)
            return env

        elif isinstance(stmt, ast.ReturnStmt):
            # Return is handled in function checking
            return env

        elif isinstance(stmt, ast.AssignStmt):
            # Assignment
            value_type = self.infer(env, stmt.value)
            var_scheme = env.get(stmt.name)
            if var_scheme is None:
                raise TypeError(f"Undefined variable: {stmt.name}")
            var_type = self.instantiate(var_scheme)
            self.unify(var_type, value_type)
            return env

        elif isinstance(stmt, ast.ForStmt):
            # Infer iterable type
            iter_type = self.infer(env, stmt.iterable)

            if isinstance(iter_type, TypeList):
                elem_type = iter_type.elem_type
            elif isinstance(iter_type, TypeDict):
                elem_type = iter_type.key_type
            else:
                elem_type = self.fresh_var()

            body_env = env.extend(stmt.var, Scheme([], elem_type))
            for s in stmt.body:
                body_env = self.check_statement(body_env, s)
            return env

        elif isinstance(stmt, ast.WhileStmt):
            cond_type = self.infer(env, stmt.condition)
            self.unify(cond_type, TypeBool)
            body_env = TypeEnvironment(env)
            for s in stmt.body:
                body_env = self.check_statement(body_env, s)
            return env

        elif isinstance(stmt, ast.StructStmt):
            # Struct types
            field_types = []
            for field in stmt.fields:
                if field.type:
                    t = self._parse_type_annotation(field.type)
                else:
                    t = self.fresh_var()
                field_types.append((field.name, t))

            # Create struct type
            struct_type = TypeDict(TypeStr, TypeStr)  # Simplified
            return env.extend(stmt.name, Scheme([], struct_type))

        return env

    def check_program(self, program: ast.Program) -> Dict[str, Scheme]:
        """Type check a full program"""
        env = self.env
        for stmt in program.statements:
            env = self.check_statement(env, stmt)
        return env.bindings


def type_check(program: ast.Program) -> Dict[str, str]:
    """Type check a program and return the type environment as strings"""
    checker = TypeChecker()
    bindings = checker.check_program(program)
    return {name: str(scheme) for name, scheme in bindings.items()}
