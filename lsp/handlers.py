"""
LSP Request Handlers for AICode

Handles LSP requests like completion, hover, and definition.
"""

import re
from typing import Dict, List, Optional, Any

from src.parser import parse
from src.type_checker import TypeChecker
from .symbol_table import SymbolTable, Symbol, SymbolKind


class LSPHandlers:
    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.symbol_tables: Dict[str, SymbolTable] = {}
        self.type_checker = TypeChecker()
    
    def open_document(self, uri: str, text: str) -> None:
        self.documents[uri] = text
        self._update_symbol_table(uri, text)
    
    def close_document(self, uri: str) -> None:
        if uri in self.documents:
            del self.documents[uri]
        if uri in self.symbol_tables:
            del self.symbol_tables[uri]
    
    def update_document(self, uri: str, text: str) -> None:
        self.documents[uri] = text
        self._update_symbol_table(uri, text)
    
    def _update_symbol_table(self, uri: str, text: str) -> None:
        try:
            program = parse(text)
            from lsp.symbol_table import build_symbol_table
            self.symbol_tables[uri] = build_symbol_table(program)
        except Exception:
            self.symbol_tables[uri] = SymbolTable()
    
    def completion(self, uri: str, line: int, column: int, prefix: str = "") -> Dict[str, Any]:
        table = self.symbol_tables.get(uri, SymbolTable())
        symbols = table.get_completions(prefix)
        
        items = []
        for sym in symbols:
            kind = self._symbol_kind_to_lsp(sym.kind)
            item = {
                "label": sym.name,
                "kind": kind,
                "detail": sym.type_hint or "",
                "documentation": sym.docstring or "",
            }
            items.append(item)
        
        return {"isIncomplete": False, "items": items}
    
    def hover(self, uri: str, line: int, column: int) -> Optional[Dict[str, Any]]:
        table = self.symbol_tables.get(uri, SymbolTable())
        symbol = table.get_symbol_at(line + 1, column + 1)
        
        if symbol:
            contents = {
                "kind": "markdown",
                "value": f"**{symbol.kind.value}** `{symbol.name}`"
            }
            if symbol.type_hint:
                contents["value"] += f"\n\nType: `{symbol.type_hint}`"
            if symbol.docstring:
                contents["value"] += f"\n\n{symbol.docstring}"
            
            return {
                "contents": contents,
                "range": {
                    "start": {"line": symbol.line - 1, "character": symbol.column},
                    "end": {"line": symbol.end_line - 1, "character": symbol.end_column},
                }
            }
        return None
    
    def definition(self, uri: str, line: int, column: int) -> Optional[Dict[str, Any]]:
        table = self.symbol_tables.get(uri, SymbolTable())
        symbol = table.get_symbol_at(line + 1, column + 1)
        
        if symbol:
            return {
                "uri": uri,
                "range": {
                    "start": {"line": symbol.line - 1, "character": symbol.column},
                    "end": {"line": symbol.end_line - 1, "character": symbol.end_column},
                }
            }
        return None
    
    def diagnostics(self, uri: str) -> List[Dict[str, Any]]:
        if uri not in self.documents:
            return []
        
        diagnostics = []
        text = self.documents[uri]
        lines = text.split('\n')
        
        try:
            program = parse(text)
        except Exception as e:
            if hasattr(e, 'line') and hasattr(e, 'column'):
                diag = {
                    "range": {
                        "start": {"line": e.line - 1, "character": e.column},
                        "end": {"line": e.line - 1, "character": e.column + 10},
                    },
                    "severity": 1,
                    "message": str(e),
                    "source": "aic-parser",
                }
                diagnostics.append(diag)
            return diagnostics
        
        try:
            self.type_checker.check_program(program)
        except Exception as e:
            if hasattr(e, 'line') and hasattr(e, 'column'):
                diag = {
                    "range": {
                        "start": {"line": e.line - 1, "character": e.column},
                        "end": {"line": e.line - 1, "character": e.column + 10},
                    },
                    "severity": 1,
                    "message": str(e),
                    "source": "aic-type-checker",
                }
                diagnostics.append(diag)
        
        return diagnostics
    
    def _symbol_kind_to_lsp(self, kind: SymbolKind) -> int:
        mapping = {
            SymbolKind.FUNCTION: 3,
            SymbolKind.VARIABLE: 6,
            SymbolKind.CONSTANT: 6,
            SymbolKind.TYPE: 7,
            SymbolKind.STRUCT: 23,
            SymbolKind.ENUM: 23,
            SymbolKind.PARAMETER: 6,
            SymbolKind.MODULE: 9,
        }
        return mapping.get(kind, 1)
    
    def get_snippets(self) -> List[Dict[str, Any]]:
        return [
            {
                "label": "fn",
                "kind": 15,
                "insertText": "fn ${1:name}(${2:args}) {\n\t$0\n}",
                "insertTextFormat": 2,
                "documentation": "Insert a function definition",
            },
            {
                "label": "struct",
                "kind": 15,
                "insertText": "struct ${1:Name} {\n\t$0\n}",
                "insertTextFormat": 2,
                "documentation": "Insert a struct definition",
            },
            {
                "label": "enum",
                "kind": 15,
                "insertText": "enum ${1:Name} {\n\t${2:Variant1},\n\t${3:Variant2}\n}",
                "insertTextFormat": 2,
                "documentation": "Insert an enum definition",
            },
            {
                "label": "for",
                "kind": 15,
                "insertText": "for ${1:item} in ${2:iterable} {\n\t$0\n}",
                "insertTextFormat": 2,
                "documentation": "Insert a for loop",
            },
            {
                "label": "if",
                "kind": 15,
                "insertText": "if ${1:condition} {\n\t$0\n}",
                "insertTextFormat": 2,
                "documentation": "Insert an if statement",
            },
            {
                "label": "match",
                "kind": 15,
                "insertText": "match ${1:expr} {\n\t${2:pattern} => ${3:value},\n}",
                "insertTextFormat": 2,
                "documentation": "Insert a match expression",
            },
        ]