"""
AICode Interpreter - Führt den AST aus
"""

from typing import Any, Dict, List, Optional, Callable
from .ast_nodes import *


class AICodeError(Exception):
    pass


class ReturnValue(Exception):
    """Exception für Return-Statements"""

    def __init__(self, value: Any):
        self.value = value


class Environment:
    """Scope für Variablen"""

    def __init__(self, parent: Optional["Environment"] = None):
        self.variables: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        self.variables[name] = value

    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise AICodeError(f"Undefined variable: '{name}'")

    def set(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise AICodeError(f"Undefined variable: '{name}'")


class AICodeFunction:
    """Benutzerdefinierte Funktion"""

    def __init__(self, declaration: FnStmt, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        env = Environment(self.closure)

        for param, arg in zip(self.declaration.params, args):
            env.define(param.name, arg)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnValue as ret:
            return ret.value

        return None

    def __repr__(self):
        return f"<fn {self.declaration.name}>"


class AICodeLambda:
    """Lambda-Funktion"""

    def __init__(self, declaration: LambdaExpr, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        env = Environment(self.closure)

        for param, arg in zip(self.declaration.params, args):
            env.define(param.name, arg)

        # Save and restore environment
        previous = interpreter.environment
        try:
            interpreter.environment = env
            return interpreter.evaluate(self.declaration.body)
        finally:
            interpreter.environment = previous

    def __repr__(self):
        return "<lambda>"


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.output = []
        self._setup_stdlib()

    def _setup_stdlib(self):
        """Richtet die Standardbibliothek ein"""
        # I/O
        self.globals.define("print", self._builtin_print)
        self.globals.define("println", self._builtin_println)

        # Listen-Operationen
        self.globals.define("map", self._builtin_map)
        self.globals.define("filter", self._builtin_filter)
        self.globals.define("reduce", self._builtin_reduce)
        self.globals.define("length", self._builtin_length)
        self.globals.define("range", self._builtin_range)

        # String-Operationen
        self.globals.define("str", self._builtin_str)
        self.globals.define("int", self._builtin_int)
        self.globals.define("float", self._builtin_float)

        # Dict-Operationen
        self.globals.define("keys", self._builtin_keys)
        self.globals.define("values", self._builtin_values)

        # Result type
        self.globals.define("Ok", self._builtin_ok)
        self.globals.define("Err", self._builtin_err)
        self.globals.define("is_ok", self._builtin_is_ok)
        self.globals.define("is_err", self._builtin_is_err)
        self.globals.define("unwrap", self._builtin_unwrap)
        self.globals.define("unwrap_or", self._builtin_unwrap_or)

    def _builtin_print(self, *args):
        output = " ".join(str(arg) for arg in args)
        self.output.append(output)
        return None

    def _builtin_println(self, *args):
        output = " ".join(str(arg) for arg in args)
        self.output.append(output)
        return None

    def _builtin_map(self, lst: List, func) -> List:
        return [self._call_function(func, [item]) for item in lst]

    def _builtin_filter(self, lst: List, func) -> List:
        return [item for item in lst if self._call_function(func, [item])]

    def _builtin_reduce(self, lst: List, func, initial: Any) -> Any:
        result = initial
        for item in lst:
            result = self._call_function(func, [result, item])
        return result

    def _call_function(self, func, args: List[Any]) -> Any:
        """Ruft eine Funktion auf (Python oder AICode)"""
        if isinstance(func, AICodeLambda):
            return func.call(self, args)
        elif callable(func):
            return func(*args)
        else:
            raise AICodeError(f"Cannot call {type(func)}")

    def _builtin_length(self, obj) -> int:
        return len(obj)

    def _builtin_range(self, *args) -> List[int]:
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        raise AICodeError("range() takes 1-3 arguments")

    def _builtin_str(self, obj) -> str:
        return str(obj)

    def _builtin_int(self, obj) -> int:
        if isinstance(obj, str):
            return int(obj)
        if isinstance(obj, float):
            return int(obj)
        if isinstance(obj, bool):
            return 1 if obj else 0
        raise AICodeError(f"Cannot convert {type(obj)} to int")

    def _builtin_float(self, obj) -> float:
        if isinstance(obj, str):
            return float(obj)
        if isinstance(obj, int):
            return float(obj)
        raise AICodeError(f"Cannot convert {type(obj)} to float")

    def _builtin_keys(self, d: Dict) -> List:
        return list(d.keys())

    def _builtin_values(self, d: Dict) -> List:
        return list(d.values())

    # === Result Type Methods ===
    def _builtin_ok(self, value):
        """Creates an Ok result: Ok(value)"""
        return {"_result": "ok", "_value": value}

    def _builtin_err(self, error):
        """Creates an Err result: Err(error)"""
        return {"_result": "err", "_error": error}

    def _builtin_is_ok(self, result):
        """Checks if result is Ok"""
        return isinstance(result, dict) and result.get("_result") == "ok"

    def _builtin_is_err(self, result):
        """Checks if result is Err"""
        return isinstance(result, dict) and result.get("_result") == "err"

    def _builtin_unwrap(self, result):
        """Unwraps Ok value or panics on Err"""
        if isinstance(result, dict) and result.get("_result") == "ok":
            return result["_value"]
        raise AICodeError(f"Called unwrap on Err: {result.get('_error', result)}")

    def _builtin_unwrap_or(self, result, default):
        """Unwraps Ok value or returns default"""
        if isinstance(result, dict) and result.get("_result") == "ok":
            return result["_value"]
        return default

    def interpret(self, program: Program) -> Any:
        """Interpretiert ein komplettes Programm"""
        for stmt in program.statements:
            self.execute(stmt)
        return self.output

    def execute(self, stmt: Stmt) -> Any:
        """Führt ein Statement aus"""
        method_name = f"visit_{type(stmt).__name__}"
        method = getattr(self, method_name, self._unknown_stmt)
        return method(stmt)

    def _unknown_stmt(self, stmt: Stmt):
        raise AICodeError(f"Unknown statement type: {type(stmt).__name__}")

    def evaluate(self, expr: Expr) -> Any:
        """Evaluiert einen Expression"""
        method_name = f"visit_{type(expr).__name__}"
        method = getattr(self, method_name, self._unknown_expr)
        return method(expr)

    def _unknown_expr(self, expr: Expr):
        raise AICodeError(f"Unknown expression type: {type(expr).__name__}")

    def execute_block(self, statements: List[Stmt], environment: Environment):
        """Führt einen Block von Statements aus"""
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    # === Statement Visitors ===

    def visit_LetStmt(self, stmt: LetStmt):
        value = self.evaluate(stmt.value)
        self.environment.define(stmt.name, value)
        return None

    def visit_ConstStmt(self, stmt: ConstStmt):
        value = self.evaluate(stmt.value)
        self.environment.define(stmt.name, value)
        return None

    def visit_ReturnStmt(self, stmt: ReturnStmt):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise ReturnValue(value)

    def visit_ExprStmt(self, stmt: ExprStmt):
        return self.evaluate(stmt.expr)

    def visit_AssignStmt(self, stmt: AssignStmt):
        value = self.evaluate(stmt.value)
        self.environment.set(stmt.name, value)
        return None

    def visit_FnStmt(self, stmt: FnStmt):
        func = AICodeFunction(stmt, self.environment)
        self.environment.define(stmt.name, func)
        return None

    def visit_StructStmt(self, stmt: StructStmt):
        # Struct als Factory-Funktion definieren
        field_names = [f.name for f in stmt.fields]

        def struct_factory(*args):
            if len(args) != len(field_names):
                raise AICodeError(
                    f"{stmt.name} expects {len(field_names)} arguments, got {len(args)}"
                )
            instance = {}
            for i, name in enumerate(field_names):
                instance[name] = args[i]
            return instance

        struct_factory.__name__ = stmt.name
        self.environment.define(stmt.name, struct_factory)
        return None

    def visit_EnumStmt(self, stmt: EnumStmt):
        # Enum als Klasse mit Varianten definieren
        enum_class = type(stmt.name, (), {})
        for variant in stmt.variants:
            if variant.fields:
                # Enum mit Daten
                def make_variant(*args, fields=variant.fields, name=variant.name):
                    if len(args) != len(fields):
                        raise AICodeError(f"{name} expects {len(fields)} arguments")
                    instance = {"_variant": name}
                    for field, arg in zip(fields, args):
                        instance[field.name] = arg
                    return instance

                make_variant.__name__ = variant.name
                setattr(enum_class, variant.name, make_variant)
            else:
                # Simple Enum
                setattr(enum_class, variant.name, {"_variant": variant.name})

        self.environment.define(stmt.name, enum_class)
        return None

    def visit_ForStmt(self, stmt: ForStmt):
        iterable = self.evaluate(stmt.iterable)

        if isinstance(iterable, list):
            items = iterable
        elif isinstance(iterable, range):
            items = list(iterable)
        elif isinstance(iterable, dict):
            items = iterable.keys()
        else:
            raise AICodeError(f"Cannot iterate over {type(iterable)}")

        for item in items:
            self.environment.define(stmt.var, item)
            self.execute_block(stmt.body, Environment(self.environment))

        return None

    def visit_WhileStmt(self, stmt: WhileStmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute_block(stmt.body, Environment(self.environment))
        return None

    def visit_ImportStmt(self, stmt: ImportStmt):
        # TODO: Implementieren
        pass

    # === Expression Visitors ===

    def visit_IntLiteral(self, expr: IntLiteral):
        return expr.value

    def visit_FloatLiteral(self, expr: FloatLiteral):
        return expr.value

    def visit_StringLiteral(self, expr: StringLiteral):
        return expr.value

    def visit_BoolLiteral(self, expr: BoolLiteral):
        return expr.value

    def visit_NullLiteral(self, expr: NullLiteral):
        return None

    def visit_Identifier(self, expr: Identifier):
        return self.environment.get(expr.name)

    def visit_ListExpr(self, expr: ListExpr):
        return [self.evaluate(e) for e in expr.elements]

    def visit_DictExpr(self, expr: DictExpr):
        result = {}
        for entry in expr.entries:
            key = entry.key if isinstance(entry.key, str) else self.evaluate(entry.key)
            result[key] = self.evaluate(entry.value)
        return result

    def visit_TupleExpr(self, expr: TupleExpr):
        return tuple(self.evaluate(e) for e in expr.elements)

    def visit_FieldAccess(self, expr: FieldAccess):
        obj = self.evaluate(expr.obj)

        if isinstance(obj, dict):
            if expr.field in obj:
                return obj[expr.field]
            raise AICodeError(f"Field '{expr.field}' not found")
        elif hasattr(obj, expr.field):
            return getattr(obj, expr.field)
        else:
            raise AICodeError(f"Cannot access field '{expr.field}' on {type(obj)}")

    def visit_IndexExpr(self, expr: IndexExpr):
        obj = self.evaluate(expr.obj)
        index = self.evaluate(expr.index)

        if isinstance(obj, list):
            if not isinstance(index, int):
                raise AICodeError("List index must be integer")
            if index < 0 or index >= len(obj):
                raise AICodeError("Index out of bounds")
            return obj[index]
        elif isinstance(obj, dict):
            if index not in obj:
                raise AICodeError(f"Key '{index}' not found")
            return obj[index]
        elif isinstance(obj, str):
            if not isinstance(index, int):
                raise AICodeError("String index must be integer")
            return obj[index]
        else:
            raise AICodeError(f"Cannot index {type(obj)}")

    def visit_CallExpr(self, expr: CallExpr):
        func = self.evaluate(expr.func)
        args = [self.evaluate(arg) for arg in expr.args]

        if isinstance(func, AICodeFunction):
            return func.call(self, args)
        elif isinstance(func, AICodeLambda):
            return func.call(self, args)
        elif callable(func):
            return func(*args)
        else:
            raise AICodeError(f"Cannot call {type(func)}")

    def visit_BinaryOp(self, expr: BinaryOp):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.op == "+":
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            return left + right
        elif expr.op == "-":
            return left - right
        elif expr.op == "*":
            return left * right
        elif expr.op == "/":
            return left / right
        elif expr.op == "%":
            return left % right
        elif expr.op == "==":
            return left == right
        elif expr.op == "!=":
            return left != right
        elif expr.op == "<":
            return left < right
        elif expr.op == ">":
            return left > right
        elif expr.op == "<=":
            return left <= right
        elif expr.op == ">=":
            return left >= right
        elif expr.op in ("&&", "and"):
            return left and right
        elif expr.op in ("||", "or"):
            return left or right
        else:
            raise AICodeError(f"Unknown operator: {expr.op}")

    def visit_UnaryOp(self, expr: UnaryOp):
        operand = self.evaluate(expr.operand)

        if expr.op == "-":
            return -operand
        elif expr.op in ("!", "not"):
            return not self.is_truthy(operand)
        else:
            raise AICodeError(f"Unknown unary operator: {expr.op}")

    def visit_LambdaExpr(self, expr: LambdaExpr):
        return AICodeLambda(expr, self.environment)

    def visit_IfExpr(self, expr: IfExpr):
        if self.is_truthy(self.evaluate(expr.condition)):
            return self.execute_block(expr.then_branch, Environment(self.environment))
        elif expr.else_branch:
            if isinstance(expr.else_branch, IfExpr):
                return self.evaluate(expr.else_branch)
            else:
                return self.execute_block(
                    expr.else_branch, Environment(self.environment)
                )
        return None

    def visit_MatchExpr(self, expr: MatchExpr):
        value = self.evaluate(expr.expr)

        for arm in expr.arms:
            if self._match_pattern(arm.pattern, value):
                return self.evaluate(arm.body)

        raise AICodeError("Non-exhaustive match expression")

    def _match_pattern(self, pattern: Pattern, value: Any) -> bool:
        if isinstance(pattern, WildcardPattern):
            return True
        elif isinstance(pattern, LiteralPattern):
            return self.evaluate(pattern.value) == value
        elif isinstance(pattern, IdentifierPattern):
            self.environment.define(pattern.name, value)
            return True
        elif isinstance(pattern, ConstructorPattern):
            if isinstance(value, dict) and value.get("_variant") == pattern.name:
                # Match enum variant fields
                for i, p in enumerate(pattern.args):
                    field_name = f"field_{i}"  # Simplified
                    # TODO: Match nested patterns
                return True
            return False
        return False

    def visit_PipeExpr(self, expr: PipeExpr):
        """Verarbeitet pipe-Operation: left |> right"""
        left = self.evaluate(expr.left)

        # right kann eine Funktion oder ein CallExpr sein
        if isinstance(expr.right, CallExpr):
            # Füge left als erstes Argument hinzu
            func = self.evaluate(expr.right.func)
            args = [left] + [self.evaluate(arg) for arg in expr.right.args]

            if isinstance(func, AICodeFunction):
                return func.call(self, args)
            elif isinstance(func, AICodeLambda):
                return func.call(self, args)
            elif callable(func):
                return func(*args)
        elif isinstance(expr.right, Identifier):
            # Pipe zu einer Funktion: x | func  ->  func(x)
            func = self.environment.get(expr.right.name)
            if callable(func):
                return func(left)

        raise AICodeError(f"Invalid pipe expression")

    def is_truthy(self, value: Any) -> bool:
        """Prüft ob ein Wert truthy ist"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, (list, dict, str)):
            return len(value) > 0
        return True


def interpret(source: str) -> Any:
    """Hilfsfunktion zum Interpretieren"""
    from .parser import parse

    program = parse(source)
    interpreter = Interpreter()
    return interpreter.interpret(program)
