"""
AICode Parser - Recursive Descent Parser
"""

from typing import List, Optional, Union
from .lexer import Token, TokenType, tokenize
from .ast_nodes import *
from .errors import ParserError, unexpected_token, expected_token, missing_delimiter


class ParseError(Exception):
    pass


class Parser:
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

    def expect(self, type: TokenType, msg: Optional[str] = None) -> Token:
        if not self.check(type):
            found = self.peek().type.name
            token = self.peek()
            if msg:
                raise ParserError("E202", msg, token.line, token.column)
            else:
                raise expected_token(type.name, found, token.line, token.column)
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def skip_newlines(self):
        """Skippt NEWLINE Tokens (aber nicht INDENT/DEDENT)"""
        while self.check(TokenType.NEWLINE):
            self.advance()

    def is_at_end(self) -> bool:
        return self.check(TokenType.EOF)

    # === Types ===

    def parse_type(self) -> Optional[Type]:
        """Parsed einen Typ"""
        if self.check(
            TokenType.IDENTIFIER,
            TokenType.BOOL_TYPE,
            TokenType.INT_TYPE,
            TokenType.FLOAT_TYPE,
            TokenType.STR_TYPE,
        ):
            base = self.advance().value or self.peek(-1).type.name.lower()

            # Generics?
            if self.match(TokenType.LT):
                args = []
                args.append(self.parse_type())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_type())
                self.expect(TokenType.GT)
                return GenericType(base, args)

            return SimpleType(base)

        # Function type
        if self.match(TokenType.LPAREN):
            param_types = []
            if not self.check(TokenType.RPAREN):
                param_types.append(self.parse_type())
                while self.match(TokenType.COMMA):
                    param_types.append(self.parse_type())
            self.expect(TokenType.RPAREN)
            self.expect(TokenType.ARROW)
            return_type = self.parse_type()
            if return_type is None:
                raise ParserError("E209", "Expected return type in function type", self.peek().line, self.peek().column)
            return FunctionType(param_types, return_type)

        return None

    # === Expressions ===

    def parse_expression(self) -> Expr:
        """Parsed eine Expression (niedrigste Präzedenz)"""
        return self.parse_pipe()

    def parse_pipe(self) -> Expr:
        """Pipe-Operation: expr | expr"""
        left = self.parse_or()

        while self.match(TokenType.PIPE):
            right = self.parse_or()
            left = PipeExpr(left, right)

        return left

    def parse_or(self) -> Expr:
        """OR-Operation: expr || expr"""
        left = self.parse_and()

        while self.match(TokenType.OR):
            right = self.parse_and()
            left = BinaryOp("||", left, right)

        return left

    def parse_and(self) -> Expr:
        """AND-Operation: expr && expr"""
        left = self.parse_equality()

        while self.match(TokenType.AND):
            right = self.parse_equality()
            left = BinaryOp("&&", left, right)

        return left

    def parse_equality(self) -> Expr:
        """Vergleiche: ==, !=, <, >, <=, >="""
        left = self.parse_additive()

        while True:
            if self.match(
                TokenType.EQEQ,
                TokenType.NEQ,
                TokenType.LT,
                TokenType.GT,
                TokenType.LTE,
                TokenType.GTE,
            ):
                op = self.peek(-1).value
                right = self.parse_additive()
                left = BinaryOp(op, left, right)
            else:
                break

        return left

    def parse_additive(self) -> Expr:
        """Addition/Subtraktion: +, -"""
        left = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.peek(-1).value
            right = self.parse_multiplicative()
            left = BinaryOp(op, left, right)

        return left

    def parse_multiplicative(self) -> Expr:
        """Multiplikation/Division: *, /, %"""
        left = self.parse_unary()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.peek(-1).value
            right = self.parse_unary()
            left = BinaryOp(op, left, right)

        return left

    def parse_unary(self) -> Expr:
        """Unäre Operatoren: !, -"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.peek(-1).value
            operand = self.parse_unary()
            return UnaryOp(op, operand)

        return self.parse_postfix()

    def parse_postfix(self) -> Expr:
        """Postfix-Operationen: .field, [index], (args)"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.DOT):
                # Field access
                field = self.expect(TokenType.IDENTIFIER).value
                expr = FieldAccess(expr, field)
            elif self.match(TokenType.LBRACKET):
                # Index access
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, index)
            elif self.match(TokenType.LPAREN):
                # Function call
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, args)
            else:
                break

        return expr

    def parse_primary(self) -> Expr:
        """Primäre Expressions"""
        # Literale
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

        # Lambda: \x: x * 2 oder fn(x): x * 2
        if self.match(TokenType.BACKSLASH):
            return self.parse_lambda_short()
        if self.check(TokenType.FN) and self.peek(1).type == TokenType.LPAREN:
            return self.parse_lambda_long()

        # Match-Expression
        if self.match(TokenType.MATCH):
            return self.parse_match()

        # If-Expression
        if self.match(TokenType.IF):
            return self.parse_if_expr()

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.peek(-1).value)

        # Gruppierte Expression
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # Liste
        if self.match(TokenType.LBRACKET):
            return self.parse_list()

        # Dict
        if self.match(TokenType.LBRACE):
            return self.parse_dict()

        raise unexpected_token(self.peek().type.name, line=self.peek().line, column=self.peek().column)

    def parse_lambda_short(self) -> LambdaExpr:
        """Kurze Lambda-Form: \\x: x * 2"""
        params = []

        # Parameter parsen
        while self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            params.append(Param(name, None))

        self.expect(TokenType.COLON)
        body = self.parse_expression()

        return LambdaExpr(params, None, body)

    def parse_lambda_long(self) -> LambdaExpr:
        """Lange Lambda-Form: fn(x): x * 2 or fn(x):\n  ...\n"""
        self.advance()  # fn

        self.expect(TokenType.LPAREN)
        params = self.parse_lambda_params()
        self.expect(TokenType.RPAREN)

        return_type = None
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()

        self.expect(TokenType.COLON)
        
        if self.check(TokenType.NEWLINE):
            self.advance()
            self.expect(TokenType.INDENT)
            body = self.parse_block()
            self.expect(TokenType.DEDENT)
        else:
            body = self.parse_expression()

        return LambdaExpr(params, return_type, body)

    def parse_lambda_params(self) -> List[Param]:
        """Parsed Parameter-Liste für Lambdas (ohne Typ-Annotationen)"""
        params = []

        if not self.check(TokenType.RPAREN):
            name = self.expect(TokenType.IDENTIFIER).value
            params.append(Param(name, None))

            while self.match(TokenType.COMMA):
                name = self.expect(TokenType.IDENTIFIER).value
                params.append(Param(name, None))

        return params

    def parse_list(self) -> ListExpr:
        """Parsed [1, 2, 3]"""
        elements = []

        if not self.check(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                elements.append(self.parse_expression())

        self.expect(TokenType.RBRACKET)
        return ListExpr(elements)

    def parse_dict(self) -> DictExpr:
        """Parsed {key: value, ...}"""
        entries = []

        if not self.check(TokenType.RBRACE):
            entries.append(self.parse_dict_entry())
            while self.match(TokenType.COMMA):
                entries.append(self.parse_dict_entry())

        self.expect(TokenType.RBRACE)
        return DictExpr(entries)

    def parse_dict_entry(self) -> DictEntry:
        """Parsed key: value (key can be identifier or string)"""
        if self.check(TokenType.IDENTIFIER):
            key = self.advance().value
        elif self.match(TokenType.STRING):
            key = self.peek(-1).value
        else:
            raise ParserError("E218", "Expected identifier or string for dict key", self.peek().line, self.peek().column)

        self.expect(TokenType.COLON)
        value = self.parse_expression()

        return DictEntry(key, value)

    def parse_match(self) -> MatchExpr:
        """Parsed match expr ..."""
        expr = self.parse_expression()

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)

        arms = []
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            arms.append(self.parse_match_arm())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        return MatchExpr(expr, arms)

    def parse_match_arm(self) -> MatchArm:
        """Parsed pattern -> expr"""
        pattern = self.parse_pattern()
        self.expect(TokenType.ARROW)
        body = self.parse_expression()
        return MatchArm(pattern, body)

    def parse_pattern(self) -> Pattern:
        """Parsed ein Pattern"""
        if self.match(TokenType.UNDERSCORE):
            return WildcardPattern()

        # Also check for _ as identifier (since lexer now treats _ as identifier)
        if self.check(TokenType.IDENTIFIER) and self.peek().value == "_":
            self.advance()
            return WildcardPattern()

        if self.match(TokenType.INT):
            return LiteralPattern(IntLiteral(self.peek(-1).value))
        if self.match(TokenType.STRING):
            return LiteralPattern(StringLiteral(self.peek(-1).value))
        if self.match(TokenType.BOOL):
            return LiteralPattern(BoolLiteral(self.peek(-1).value))

        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value

            # Constructor Pattern: Name(args)
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_pattern())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_pattern())
                self.expect(TokenType.RPAREN)
                return ConstructorPattern(name, args)

            return IdentifierPattern(name)

        raise unexpected_token(self.peek().type.name, context="in pattern", line=self.peek().line, column=self.peek().column)

    def parse_if_expr(self) -> IfExpr:
        """Parsed if expr ..."""
        condition = self.parse_expression()

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        then_branch = self.parse_block()
        self.expect(TokenType.DEDENT)

        else_branch = None
        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                self.advance()  # if
                else_branch = self.parse_if_expr()
            else:
                self.expect(TokenType.NEWLINE)
                self.expect(TokenType.INDENT)
                else_branch = self.parse_block()
                self.expect(TokenType.DEDENT)

        return IfExpr(condition, then_branch, else_branch)

    # === Statements ===

    def parse_block(self) -> List[Stmt]:
        """Parsed einen Block von Statements"""
        statements = []

        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            statements.append(self.parse_statement())

        return statements

    def parse_statement(self) -> Stmt:
        """Parsed ein Statement"""
        self.skip_newlines()

        if self.match(TokenType.LET):
            return self.parse_let()
        if self.match(TokenType.CONST):
            return self.parse_const()
        if self.match(TokenType.FN):
            return self.parse_fn()
        if self.match(TokenType.STRUCT):
            return self.parse_struct()
        if self.match(TokenType.ENUM):
            return self.parse_enum()
        if self.match(TokenType.RETURN):
            return self.parse_return()
        if self.match(TokenType.FOR):
            return self.parse_for()
        if self.match(TokenType.WHILE):
            return self.parse_while()
        if self.match(TokenType.IMPORT):
            return self.parse_import()
        if self.match(TokenType.EXPORT):
            return self.parse_export()

        # Check for assignment: identifier = expression
        if self.check(TokenType.IDENTIFIER):
            # Look ahead to see if next non-newline token is EQ
            pos = self.pos
            self.advance()  # consume identifier
            if self.check(TokenType.EQ):
                name = self.peek(-1).value
                self.advance()  # consume =
                value = self.parse_expression()
                return AssignStmt(name, value)
            else:
                # Not an assignment, reset position
                self.pos = pos

        # Expression Statement
        expr = self.parse_expression()
        return ExprStmt(expr)

    def parse_let(self) -> LetStmt:
        """Parsed let [mut] name[: type] = expr"""
        mutable = False
        if self.match(TokenType.MUT):
            mutable = True

        name = self.expect(TokenType.IDENTIFIER).value

        var_type = None
        if self.match(TokenType.COLON):
            var_type = self.parse_type()

        self.expect(TokenType.EQ)
        value = self.parse_expression()

        return LetStmt(name, var_type, value, mutable)

    def parse_const(self) -> ConstStmt:
        """Parsed const name = expr"""
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQ)
        value = self.parse_expression()
        return ConstStmt(name, value)

    def parse_fn(self) -> FnStmt:
        """Parsed fn name(params) -> type block"""
        name = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)

        return_type = None
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = self.parse_block()
        self.expect(TokenType.DEDENT)

        return FnStmt(name, params, return_type, body)

    def parse_params(self) -> List[Param]:
        """Parsed Parameter-Liste (mit optionalen Typen)"""
        params = []

        if not self.check(TokenType.RPAREN):
            name = self.expect(TokenType.IDENTIFIER).value
            param_type = None
            if self.match(TokenType.COLON):
                param_type = self.parse_type()
            params.append(Param(name, param_type))

            while self.match(TokenType.COMMA):
                name = self.expect(TokenType.IDENTIFIER).value
                param_type = None
                if self.match(TokenType.COLON):
                    param_type = self.parse_type()
                params.append(Param(name, param_type))

        return params

    def parse_struct(self) -> StructStmt:
        """Parsed struct Name ..."""
        name = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)

        fields = []
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_type = self.parse_type()
            fields.append(Param(field_name, field_type))
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        return StructStmt(name, fields)

    def parse_enum(self) -> EnumStmt:
        """Parsed enum Name ..."""
        name = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)

        variants = []
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            variant_name = self.expect(TokenType.IDENTIFIER).value

            # Optionale Felder
            fields = None
            if self.match(TokenType.LPAREN):
                fields = self.parse_params()
                self.expect(TokenType.RPAREN)

            variants.append(EnumVariant(variant_name, fields))
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        return EnumStmt(name, variants)

    def parse_return(self) -> ReturnStmt:
        """Parsed return [expr]"""
        if self.check(TokenType.NEWLINE, TokenType.DEDENT, TokenType.EOF):
            return ReturnStmt(None)
        return ReturnStmt(self.parse_expression())

    def parse_for(self) -> ForStmt:
        """Parsed for var in expr ..."""
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = self.parse_block()
        self.expect(TokenType.DEDENT)

        return ForStmt(var, iterable, body)

    def parse_while(self) -> WhileStmt:
        """Parsed while expr ..."""
        condition = self.parse_expression()

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = self.parse_block()
        self.expect(TokenType.DEDENT)

        return WhileStmt(condition, body)

    def parse_import(self) -> ImportStmt:
        """Parsed import module oder from module import name1, name2"""
        if self.check(TokenType.IDENTIFIER):
            module = self.advance().value

            # import module as alias
            alias = None
            if self.match(TokenType.AS):
                alias = self.expect(TokenType.IDENTIFIER).value

            return ImportStmt(module, None, alias)

        # from module import ...
        self.expect(TokenType.FROM)
        module = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IMPORT)

        names = [self.expect(TokenType.IDENTIFIER).value]
        while self.match(TokenType.COMMA):
            names.append(self.expect(TokenType.IDENTIFIER).value)

        return ImportStmt(module, names, None)

    def parse_export(self) -> Union[FnStmt, StructStmt, EnumStmt]:
        """Parsed export fn/struct/enum ..."""
        if self.match(TokenType.FN):
            stmt = self.parse_fn()
            stmt.exported = True
            return stmt
        if self.match(TokenType.STRUCT):
            stmt = self.parse_struct()
            stmt.exported = True
            return stmt
        if self.match(TokenType.ENUM):
            stmt = self.parse_enum()
            stmt.exported = True
            return stmt
        raise ParserError("E215", "Expected fn, struct, or enum after export", self.peek().line, self.peek().column)

    # === Program ===

    def parse(self) -> Program:
        """Parsed das gesamte Programm"""
        statements = []

        self.skip_newlines()
        while not self.is_at_end():
            statements.append(self.parse_statement())
            self.skip_newlines()

        return Program(statements)


def parse(source: str) -> Program:
    """Hilfsfunktion zum Parsen"""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
