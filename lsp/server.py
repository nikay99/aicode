"""
AICode Language Server Protocol (LSP) Server

Implements JSON-RPC based LSP server with stdio transport.
"""

import json
import sys
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from .handlers import LSPHandlers


class LSPServer:
    def __init__(self):
        self.handlers = LSPHandlers()
        self.running = False
        self.capabilities = {
            "textDocumentSync": 1,
            "completionProvider": {
                "resolveProvider": False,
                "triggerCharacters": [".", ":"],
            },
            "hoverProvider": True,
            "definitionProvider": True,
            "diagnosticsProvider": True,
        }
    
    def start(self) -> None:
        self.running = True
        while self.running:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                message = json.loads(line.strip())
                self._handle_message(message)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                self._send_error(-32600, str(e))
    
    def stop(self) -> None:
        self.running = False
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params", {})
        
        if method == "initialize":
            self._handle_initialize(msg_id, params)
        elif method == "shutdown":
            self._handle_shutdown(msg_id)
        elif method == "exit":
            self.stop()
            sys.exit(0)
        elif method == "textDocument/didOpen":
            self._handle_text_document_did_open(params)
        elif method == "textDocument/didChange":
            self._handle_text_document_did_change(params)
        elif method == "textDocument/didClose":
            self._handle_text_document_did_close(params)
        elif method == "textDocument/completion":
            self._handle_completion(msg_id, params)
        elif method == "textDocument/hover":
            self._handle_hover(msg_id, params)
        elif method == "textDocument/definition":
            self._handle_definition(msg_id, params)
        else:
            if msg_id is not None:
                self._send_response(msg_id, {"status": "not_implemented"})
    
    def _handle_initialize(self, msg_id: Any, params: Dict[str, Any]) -> None:
        result = {
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "aic-lsp",
                "version": "0.4.0",
            },
        }
        self._send_response(msg_id, result)
    
    def _handle_shutdown(self, msg_id: Any) -> None:
        self._send_response(msg_id, {"status": "ok"})
    
    def _handle_text_document_did_open(self, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri")
        text = text_doc.get("text", "")
        
        if uri and text is not None:
            self.handlers.open_document(uri, text)
            self._publish_diagnostics(uri)
    
    def _handle_text_document_did_change(self, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri")
        
        if uri and uri in self.handlers.documents:
            content_changes = params.get("contentChanges", [])
            for change in content_changes:
                if "text" in change:
                    self.handlers.update_document(uri, change["text"])
            self._publish_diagnostics(uri)
    
    def _handle_text_document_did_close(self, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri")
        
        if uri:
            self.handlers.close_document(uri)
    
    def _handle_completion(self, msg_id: Any, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        position = params.get("position", {})
        uri = text_doc.get("uri")
        line = position.get("line", 0)
        column = position.get("character", 0)
        
        prefix = ""
        if uri in self.handlers.documents:
            doc_lines = self.handlers.documents[uri].split('\n')
            if line < len(doc_lines):
                line_text = doc_lines[line]
                prefix = self._get_word_at_position(line_text, column)
        
        result = self.handlers.completion(uri, line, column, prefix)
        self._send_response(msg_id, result)
    
    def _handle_hover(self, msg_id: Any, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        position = params.get("position", {})
        uri = text_doc.get("uri")
        line = position.get("line", 0)
        column = position.get("character", 0)
        
        result = self.handlers.hover(uri, line, column)
        self._send_response(msg_id, result if result else {"contents": ""})
    
    def _handle_definition(self, msg_id: Any, params: Dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        position = params.get("position", {})
        uri = text_doc.get("uri")
        line = position.get("line", 0)
        column = position.get("character", 0)
        
        result = self.handlers.definition(uri, line, column)
        self._send_response(msg_id, result if result else None)
    
    def _publish_diagnostics(self, uri: str) -> None:
        diagnostics = self.handlers.diagnostics(uri)
        notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics,
            },
        }
        self._send_notification(notification)
    
    def _get_word_at_position(self, line: str, column: int) -> str:
        start = column
        end = column
        while start > 0 and line[start - 1].isalnum():
            start -= 1
        while end < len(line) and line[end].isalnum():
            end += 1
        return line[start:end]
    
    def _send_response(self, msg_id: Any, result: Any) -> None:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result,
        }
        self._send(response)
    
    def _send_error(self, code: int, message: str) -> None:
        error = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": code,
                "message": message,
            },
        }
        self._send(error)
    
    def _send_notification(self, notification: Dict[str, Any]) -> None:
        self._send(notification)
    
    def _send(self, message: Dict[str, Any]) -> None:
        line = json.dumps(message)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


def main():
    server = LSPServer()
    server.start()


if __name__ == "__main__":
    main()