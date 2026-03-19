"""
Symbol Table Builder for AICode LSP

Extracts symbols (functions, variables, types) from AST for LSP features.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

from src.ast_nodes import (
    Program, FnStmt, StructStmt, EnumStmt, LetStmt, ConstStmt,
    ImportStmt, Identifier, Param
)


class SymbolKind(Enum):
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    STRUCT = "struct"
    ENUM = "enum"
    PARAMETER = "parameter"
    MODULE = "module"


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    line: int = 1
    column: int = 0
    end_line: int = 1
    end_column: int = 0
    type_hint: Optional[str] = None
    docstring: Optional[str] = None
    scope: str = "global"
    children: List['Symbol'] = field(default_factory=list)


class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, List[Symbol]] = {}
        self.scopes: Dict[str, Set[str]] = {"global": set()}
        self.current_scope = "global"
        self._imports: List[ImportStmt] = []
    
    def enter_scope(self, name: str) -> None:
        self.current_scope = name
        if name not in self.scopes:
            self.scopes[name] = set()
    
    def exit_scope(self) -> None:
        self.current_scope = "global"
    
    def add_symbol(self, symbol: Symbol) -> None:
        symbol.scope = self.current_scope
        if symbol.name not in self.symbols:
            self.symbols[symbol.name] = []
        self.symbols[symbol.name].append(symbol)
        self.scopes[self.current_scope].add(symbol.name)
    
    def add_function(self, fn: FnStmt, line: int = 1, column: int = 0) -> Symbol:
        params = []
        for p in fn.params:
            param_symbol = Symbol(
                name=p.name,
                kind=SymbolKind.PARAMETER,
                line=line,
                column=column,
                end_line=line,
                end_column=column + len(p.name),
                type_hint=p.type.name if p.type else None,
            )
            params.append(param_symbol)
        
        symbol = Symbol(
            name=fn.name,
            kind=SymbolKind.FUNCTION,
            line=line,
            column=column,
            end_line=line,
            end_column=column + len(fn.name),
            type_hint=fn.return_type.name if fn.return_type else None,
            children=params,
        )
        self.add_symbol(symbol)
        return symbol
    
    def add_struct(self, struct: StructStmt, line: int = 1, column: int = 0) -> Symbol:
        fields = []
        for f in struct.fields:
            field_symbol = Symbol(
                name=f.name,
                kind=SymbolKind.VARIABLE,
                line=line,
                column=column,
                end_line=line,
                end_column=column + len(f.name),
                type_hint=f.type.name if f.type else None,
            )
            fields.append(field_symbol)
        
        symbol = Symbol(
            name=struct.name,
            kind=SymbolKind.STRUCT,
            line=line,
            column=column,
            end_line=line,
            end_column=column + len(struct.name),
            children=fields,
        )
        self.add_symbol(symbol)
        return symbol
    
    def add_enum(self, enum: EnumStmt, line: int = 1, column: int = 0) -> Symbol:
        variants = []
        for v in enum.variants:
            variant_symbol = Symbol(
                name=v.name,
                kind=SymbolKind.TYPE,
                line=line,
                column=column,
                end_line=line,
                end_column=column + len(v.name),
            )
            variants.append(variant_symbol)
        
        symbol = Symbol(
            name=enum.name,
            kind=SymbolKind.ENUM,
            line=line,
            column=column,
            end_line=line,
            end_column=column + len(enum.name),
            children=variants,
        )
        self.add_symbol(symbol)
        return symbol
    
    def add_variable(self, stmt: LetStmt, line: int = 1, column: int = 0) -> Symbol:
        symbol = Symbol(
            name=stmt.name,
            kind=SymbolKind.VARIABLE,
            line=line,
            column=column,
            end_line=line,
            end_column=column + len(stmt.name),
            type_hint=stmt.type.name if stmt.type else None,
        )
        self.add_symbol(symbol)
        return symbol
    
    def add_constant(self, stmt: ConstStmt, line: int = 1, column: int = 0) -> Symbol:
        symbol = Symbol(
            name=stmt.name,
            kind=SymbolKind.CONSTANT,
            line=line,
            column=column,
            end_line=line,
            end_column=column + len(stmt.name),
        )
        self.add_symbol(symbol)
        return symbol
    
    def get_symbol_at(self, line: int, column: int) -> Optional[Symbol]:
        for name, symbols in self.symbols.items():
            for sym in symbols:
                if sym.line == 0:
                    continue
                if (sym.line < line < sym.end_line or
                    (sym.line == line <= column <= sym.end_column) or
                    (sym.line <= line <= sym.end_line and
                     sym.column <= column <= sym.end_column)):
                    return sym
        return None
    
    def get_symbols_in_scope(self, scope: str = None) -> List[Symbol]:
        if scope is None:
            scope = self.current_scope
        result = []
        for name in self.scopes.get(scope, set()):
            result.extend(self.symbols.get(name, []))
        return result
    
    def get_completions(self, prefix: str = "", scope: str = None) -> List[Symbol]:
        results = []
        scopes_to_check = ["global"]
        if scope:
            scopes_to_check.insert(0, scope)
        
        for s in scopes_to_check:
            for name in self.scopes.get(s, set()):
                if name.startswith(prefix):
                    results.extend(self.symbols.get(name, []))
        
        return results
    
    def resolve_symbol(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name][0]
        for scope_name, symbols in self.scopes.items():
            if name in symbols and name in self.symbols:
                return self.symbols[name][0]
        return None


def build_symbol_table(program: Program) -> SymbolTable:
    table = SymbolTable()
    
    def process_statement(stmt, scope="global", line=1, column=0):
        if isinstance(stmt, FnStmt):
            sym = table.add_function(stmt, line, column)
            table.enter_scope(stmt.name)
            for i, p in enumerate(stmt.params):
                if isinstance(p, Param):
                    table.add_symbol(Symbol(
                        name=p.name,
                        kind=SymbolKind.PARAMETER,
                        line=line,
                        column=column,
                        end_line=line,
                        end_column=column + len(p.name),
                        type_hint=p.type.name if p.type else None,
                    ))
            body_line = line + 1
            for body_stmt in stmt.body:
                process_statement(body_stmt, stmt.name, body_line, 0)
                body_line += 1
            table.exit_scope()
        
        elif isinstance(stmt, StructStmt):
            table.add_struct(stmt, line, column)
        
        elif isinstance(stmt, EnumStmt):
            table.add_enum(stmt, line, column)
        
        elif isinstance(stmt, LetStmt):
            table.add_variable(stmt, line, column)
        
        elif isinstance(stmt, ConstStmt):
            table.add_constant(stmt, line, column)
        
        elif isinstance(stmt, ImportStmt):
            table._imports.append(stmt)
    
    for i, stmt in enumerate(program.statements):
        process_statement(stmt, "global", i + 1, 0)
    
    return table