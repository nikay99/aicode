"""
AICode-AI Parser
Recursive descent parser for Unicode tokens
"""

from typing import List, Optional, Union
from .lexer_ai import tokenize, Token, TokenType
from .ast_ai import *

_typevar_counter = 0


def _fresh_typevar() -> TypeVar:
    global _typevar_counter
    _typevar_counter += 1
    return TypeVar(_typevar_counter)


class ParseError(Exception):
    pass


class Parser:
    """Parser for AICode-AI Unicode syntax"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[pos]

    def advance(self) -> Token:
        token = self.peek()
        self.pos += 1
        return token

    def check(self, *types: TokenType) -> bool:
        return self.peek().type in types

    def expect(self, type: TokenType) -> Token:
        if not self.check(type):
            raise ParseError(f"E101:{self.peek().line}:{self.peek().column}")
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def skip_newlines(self):
        """Skip NEWLINE, INDENT, DEDENT tokens"""
        while self.check(TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
            self.advance()

    def is_at_end(self) -> bool:
        return self.check(TokenType.EOF)

    # === Type Parsing ===

    def parse_type(self) -> Optional[Type]:
        """Parse a type annotation"""
        if self.match(TokenType.INT_TYPE):
            return TypeInt
        elif self.match(TokenType.FLOAT_TYPE):
            return TypeFloat
        elif self.match(TokenType.STR_TYPE):
            return TypeStr
        elif self.match(TokenType.BOOL_TYPE):
            return TypeBool
        elif self.match(TokenType.LIST_TYPE):
            return TypeList(_fresh_typevar())
        elif self.match(TokenType.DICT_TYPE):
            return TypeDict(TypeStr, _fresh_typevar())
        return None

    # === Expressions ===

    def parse_expression(self) -> Expr:
        """Parse expression (lowest precedence)"""
        return self.parse_pipe()

    def parse_pipe(self) -> Expr:
        """Parse pipe: expr ▷ func"""
        left = self.parse_or()

        while self.match(TokenType.PIPE):
            right = self.parse_or()
            left = PipeExpr(left, right)

        return left

    def parse_or(self) -> Expr:
        """Parse or: expr ∨ expr"""
        left = self.parse_and()

        while self.match(TokenType.OR):
            right = self.parse_and()
            left = BinaryOp("∨", left, right)

        return left

    def parse_and(self) -> Expr:
        """Parse and: expr ∧ expr"""
        left = self.parse_equality()

        while self.match(TokenType.AND):
            right = self.parse_equality()
            left = BinaryOp("∧", left, right)

        return left

    def parse_equality(self) -> Expr:
        """Parse equality: =, ≠, <, >, ≤, ≥"""
        left = self.parse_additive()

        while True:
            if self.match(TokenType.EQ):
                right = self.parse_additive()
                left = BinaryOp("=", left, right)
            elif self.match(TokenType.NEQ):
                right = self.parse_additive()
                left = BinaryOp("≠", left, right)
            elif self.match(TokenType.LT):
                right = self.parse_additive()
                left = BinaryOp("<", left, right)
            elif self.match(TokenType.GT):
                right = self.parse_additive()
                left = BinaryOp(">", left, right)
            elif self.match(TokenType.LTE):
                right = self.parse_additive()
                left = BinaryOp("≤", left, right)
            elif self.match(TokenType.GTE):
                right = self.parse_additive()
                left = BinaryOp("≥", left, right)
            else:
                break

        return left

    def parse_additive(self) -> Expr:
        """Parse +, -"""
        left = self.parse_multiplicative()

        while True:
            if self.match(TokenType.PLUS):
                right = self.parse_multiplicative()
                left = BinaryOp("+", left, right)
            elif self.match(TokenType.MINUS):
                right = self.parse_multiplicative()
                left = BinaryOp("-", left, right)
            else:
                break

        return left

    def parse_multiplicative(self) -> Expr:
        """Parse *, /, %"""
        left = self.parse_unary()

        while True:
            if self.match(TokenType.STAR):
                right = self.parse_unary()
                left = BinaryOp("*", left, right)
            elif self.match(TokenType.SLASH):
                right = self.parse_unary()
                left = BinaryOp("/", left, right)
            elif self.match(TokenType.PERCENT):
                right = self.parse_unary()
                left = BinaryOp("%", left, right)
            else:
                break

        return left

    def parse_unary(self) -> Expr:
        """Parse unary: ¬, -"""
        if self.match(TokenType.NOT):
            operand = self.parse_unary()
            return UnaryOp("¬", operand)
        elif self.match(TokenType.MINUS):
            operand = self.parse_unary()
            return UnaryOp("-", operand)

        return self.parse_postfix()

    def parse_postfix(self) -> Expr:
        """Parse postfix: .field, [index], (args)"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LBRACKET):
                # Index access: obj[index]
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, index)
            elif self.match(TokenType.LPAREN):
                # Function call: func(args)
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, args)
            elif self.match(TokenType.DOT):
                # Field access: obj.field
                field = self.expect(TokenType.IDENTIFIER).value
                expr = FieldAccess(expr, field)
            else:
                break

        return expr

    def parse_primary(self) -> Expr:
        """Parse primary expressions"""
        # Literals
        if self.match(TokenType.INT):
            return IntLiteral(self.peek(-1).value)
        if self.match(TokenType.FLOAT):
            return FloatLiteral(self.peek(-1).value)
        if self.match(TokenType.STRING):
            return StringLiteral(self.peek(-1).value)
        if self.match(TokenType.BOOL):
            return BoolLiteral(self.peek(-1).value)
        if self.match(TokenType.NULL):
            return NullLiteral()

        # Lambda: λ(params) → body
        if self.match(TokenType.FUNC):
            return self.parse_lambda()

        # If expression: ? condition: then: else
        if self.match(TokenType.IF):
            return self.parse_if_expr()

        # Match expression: ∼ expr \n arms
        if self.match(TokenType.MATCH):
            return self.parse_match_expr()

        # List: [elements]
        if self.match(TokenType.LBRACKET):
            return self.parse_list()

        # Dict: {entries}
        if self.match(TokenType.LBRACE):
            return self.parse_dict()

        # Grouped expression: (expr)
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.peek(-1).value)

        raise ParseError(f"E102:{self.peek().line}:{self.peek().column}")

    def parse_lambda(self) -> LambdaExpr:
        """Parse lambda: λ(params) → body"""
        self.expect(TokenType.LPAREN)
        params = []

        if not self.check(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                params.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.RPAREN)

        # Optional return type
        if self.match(TokenType.ARROW):
            # Skip type for now, just consume it
            _ = self.parse_type()

        # Lambda body
        if self.match(TokenType.ARROW):
            body = self.parse_expression()
        else:
            body = self.parse_expression()

        return LambdaExpr(params, body)

    def parse_if_expr(self) -> IfExpr:
        """Parse if: ? condition: then: else"""
        condition = self.parse_expression()
        self.expect(TokenType.ELSE)  # : separates condition from then

        then_branch = self.parse_expression()
        self.expect(TokenType.ELSE)  # : separates then from else

        else_branch = self.parse_expression()

        return IfExpr(condition, then_branch, else_branch)

    def parse_match_expr(self) -> MatchExpr:
        """Parse match: ∼ expr \n arms"""
        expr = self.parse_expression()

        # Expect newline and indent for arms
        if self.match(TokenType.NEWLINE):
            self.expect(TokenType.INDENT)

        arms = []
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            # Pattern → body
            # Simplified: just parse identifier or literal as pattern
            if self.match(TokenType.INT):
                pattern = str(self.peek(-1).value)
            elif self.match(TokenType.IDENTIFIER):
                pattern = self.peek(-1).value
            else:
                raise ParseError(f"E103:{self.peek().line}:{self.peek().column}")

            self.expect(TokenType.ARROW)
            body = self.parse_expression()
            arms.append(MatchArm(pattern, body))

            self.skip_newlines()

        if self.check(TokenType.DEDENT):
            self.advance()

        return MatchExpr(expr, arms)

    def parse_list(self) -> ListExpr:
        """Parse list literal: [elements]"""
        elements = []

        if not self.check(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                elements.append(self.parse_expression())

        self.expect(TokenType.RBRACKET)
        return ListExpr(elements)

    def parse_dict(self) -> DictExpr:
        """Parse dict literal: {entries}"""
        entries = []

        if not self.check(TokenType.RBRACE):
            entries.append(self.parse_dict_entry())
            while self.match(TokenType.COMMA):
                entries.append(self.parse_dict_entry())

        self.expect(TokenType.RBRACE)
        return DictExpr(entries)

    def parse_dict_entry(self) -> DictEntry:
        """Parse dict entry: key ≔ value or key: value"""
        if self.match(TokenType.IDENTIFIER):
            key = self.peek(-1).value
        elif self.match(TokenType.STRING):
            key = self.peek(-1).value
        else:
            raise ParseError(f"E104:{self.peek().line}:{self.peek().column}")

        # Can use ≔ or : for assignment
        if not self.match(TokenType.ASSIGN, TokenType.ELSE):
            raise ParseError(f"E105:{self.peek().line}:{self.peek().column}")

        value = self.parse_expression()
        return DictEntry(key, value)

    # === Statements ===

    def parse_statement(self) -> Stmt:
        """Parse a statement"""
        self.skip_newlines()

        # Variable declaration: 𝕍 [μ] name [: type] ≔ value
        if self.match(TokenType.VAR):
            return self.parse_var_stmt()

        # Constant declaration: 𝔠 name ≔ value
        if self.match(TokenType.CONST):
            return self.parse_const_stmt()

        # Function declaration: λ name(params) [: type] body
        if self.check(TokenType.FUNC) and self.peek(1).type == TokenType.IDENTIFIER:
            return self.parse_func_stmt()

        # Return: ← value
        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()

        # For loop: ∀ var ∈ iterable body
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()

        # While loop: ⟲ condition body
        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()

        # Assignment or expression
        if self.check(TokenType.IDENTIFIER):
            return self.parse_assign_or_expr()

        # Expression statement
        expr = self.parse_expression()
        return ExprStmt(expr)

    def parse_var_stmt(self) -> VarStmt:
        """Parse variable: 𝕍 [μ] name [: type] ≔ value"""
        mutable = self.match(TokenType.MUT)  # μ
        name = self.expect(TokenType.IDENTIFIER).value

        # Optional type annotation
        var_type = None
        if self.match(TokenType.ARROW):
            var_type = self.parse_type()

        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()

        return VarStmt(name, var_type, value, mutable)

    def parse_const_stmt(self) -> ConstStmt:
        """Parse constant: 𝔠 name ≔ value"""
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return ConstStmt(name, value)

    def parse_func_stmt(self) -> FuncStmt:
        """Parse function: λ name(params) [: return_type] body"""
        self.expect(TokenType.FUNC)  # consume λ
        name = self.expect(TokenType.IDENTIFIER).value

        # Parameters
        self.expect(TokenType.LPAREN)
        params = []
        if not self.check(TokenType.RPAREN):
            param_name = self.expect(TokenType.IDENTIFIER).value
            param_type = None
            if self.match(TokenType.ARROW):
                param_type = self.parse_type()
            params.append((param_name, param_type))

            while self.match(TokenType.COMMA):
                param_name = self.expect(TokenType.IDENTIFIER).value
                param_type = None
                if self.match(TokenType.ARROW):
                    param_type = self.parse_type()
                params.append((param_name, param_type))

        self.expect(TokenType.RPAREN)

        # Optional return type
        return_type = None
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()

        # Body
        if self.match(TokenType.NEWLINE):
            self.expect(TokenType.INDENT)
            body = []
            while not self.check(TokenType.DEDENT, TokenType.EOF):
                body.append(self.parse_statement())
            if self.check(TokenType.DEDENT):
                self.advance()
        else:
            # Single expression body
            body = self.parse_expression()

        return FuncStmt(name, params, return_type, body)

    def parse_return_stmt(self) -> ReturnStmt:
        """Parse return: ← [value]"""
        if self.check(TokenType.NEWLINE, TokenType.DEDENT, TokenType.EOF):
            return ReturnStmt(None)
        value = self.parse_expression()
        return ReturnStmt(value)

    def parse_for_stmt(self) -> ForStmt:
        """Parse for: ∀ var ∈ iterable body"""
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()

        # Body
        if self.match(TokenType.NEWLINE):
            self.expect(TokenType.INDENT)
            body = []
            while not self.check(TokenType.DEDENT, TokenType.EOF):
                body.append(self.parse_statement())
            if self.check(TokenType.DEDENT):
                self.advance()
        else:
            body = [ExprStmt(self.parse_expression())]

        return ForStmt(var, iterable, body)

    def parse_while_stmt(self) -> WhileStmt:
        """Parse while: ⟲ condition body"""
        condition = self.parse_expression()

        # Body
        if self.match(TokenType.NEWLINE):
            self.expect(TokenType.INDENT)
            body = []
            while not self.check(TokenType.DEDENT, TokenType.EOF):
                body.append(self.parse_statement())
            if self.check(TokenType.DEDENT):
                self.advance()
        else:
            body = [ExprStmt(self.parse_expression())]

        return WhileStmt(condition, body)

    def parse_assign_or_expr(self) -> Stmt:
        """Parse assignment or expression"""
        name = self.expect(TokenType.IDENTIFIER).value

        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
            return AssignStmt(name, value)
        else:
            # It's a call or other expression starting with identifier
            self.pos -= 1  # Back up
            expr = self.parse_expression()
            return ExprStmt(expr)

    # === Program ===

    def parse(self) -> Program:
        """Parse full program"""
        statements = []

        while not self.is_at_end():
            self.skip_newlines()
            if self.is_at_end():
                break
            statements.append(self.parse_statement())
            self.skip_newlines()

        return Program(statements)


def parse(source: str) -> Program:
    """Helper to parse source code"""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
