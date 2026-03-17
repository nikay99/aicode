"""
Comprehensive Lexer Tests
Tests for 100% coverage of src/lexer.py
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer import Lexer, TokenType, tokenize, Token
from src.errors import LexerError


class TestLexerBasic(unittest.TestCase):
    """Test basic tokenization"""
    
    def test_empty_source(self):
        """Test tokenizing empty source"""
        tokens = tokenize("")
        self.assertEqual(tokens[-1].type, TokenType.EOF)
    
    def test_whitespace_only(self):
        """Test tokenizing whitespace only"""
        tokens = tokenize("   \t\n  ")
        self.assertEqual(tokens[-1].type, TokenType.EOF)
    
    def test_comment_only(self):
        """Test tokenizing comment only"""
        tokens = tokenize("# This is a comment")
        self.assertEqual(tokens[-1].type, TokenType.EOF)
    
    def test_newlines(self):
        """Test newlines are tokenized"""
        tokens = tokenize("\n\n\n")
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        self.assertEqual(len(newlines), 3)


class TestLexerLiterals(unittest.TestCase):
    """Test literal tokenization"""
    
    def test_integers(self):
        """Test integer literals"""
        tokens = tokenize("42")
        int_tokens = [t for t in tokens if t.type == TokenType.INT]
        self.assertEqual(len(int_tokens), 1)
        self.assertEqual(int_tokens[0].value, 42)
    
    def test_zero(self):
        """Test zero"""
        tokens = tokenize("0")
        self.assertEqual(tokens[0].value, 0)
    
    def test_large_integer(self):
        """Test large integer"""
        tokens = tokenize("999999999")
        self.assertEqual(tokens[0].value, 999999999)
    
    def test_floats(self):
        """Test float literals"""
        tokens = tokenize("3.14")
        float_tokens = [t for t in tokens if t.type == TokenType.FLOAT]
        self.assertEqual(len(float_tokens), 1)
        self.assertEqual(float_tokens[0].value, 3.14)
    
    def test_float_leading_zero(self):
        """Test float with leading zero"""
        tokens = tokenize("0.5")
        self.assertEqual(tokens[0].value, 0.5)
    
    def test_strings(self):
        """Test string literals"""
        tokens = tokenize('"hello world"')
        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        self.assertEqual(len(string_tokens), 1)
        self.assertEqual(string_tokens[0].value, "hello world")
    
    def test_empty_string(self):
        """Test empty string"""
        tokens = tokenize('""')
        self.assertEqual(tokens[0].value, "")
    
    def test_string_with_spaces(self):
        """Test string with leading/trailing spaces"""
        tokens = tokenize('"  hello  "')
        self.assertEqual(tokens[0].value, "  hello  ")
    
    def test_string_escapes(self):
        """Test string escape sequences"""
        tokens = tokenize('"hello\\nworld"')
        self.assertEqual(tokens[0].value, "hello\nworld")
    
    def test_string_escape_tab(self):
        """Test tab escape"""
        tokens = tokenize('"hello\\tworld"')
        self.assertEqual(tokens[0].value, "hello\tworld")
    
    def test_string_escape_backslash(self):
        """Test backslash escape"""
        tokens = tokenize('"path\\\\to\\\\file"')
        self.assertEqual(tokens[0].value, "path\\to\\file")
    
    def test_string_escape_quote(self):
        """Test quote escape"""
        tokens = tokenize('"say \\"hello\\""')
        self.assertEqual(tokens[0].value, 'say "hello"')
    
    def test_string_unknown_escape(self):
        """Test unknown escape sequence (passes through)"""
        tokens = tokenize('"hello\\xworld"')
        self.assertEqual(tokens[0].value, "helloxworld")
    
    def test_unterminated_string(self):
        """Test unterminated string raises error"""
        with self.assertRaises(LexerError) as ctx:
            tokenize('"hello')
        self.assertIn("Unterminated", str(ctx.exception))
    
    def test_booleans(self):
        """Test boolean literals"""
        tokens_true = tokenize("true")
        tokens_false = tokenize("false")
        self.assertEqual(tokens_true[0].value, True)
        self.assertEqual(tokens_false[0].value, False)
    
    def test_null(self):
        """Test null literal"""
        tokens = tokenize("null")
        self.assertEqual(tokens[0].type, TokenType.NULL)


class TestLexerIdentifiers(unittest.TestCase):
    """Test identifier tokenization"""
    
    def test_simple_identifier(self):
        """Test simple identifier"""
        tokens = tokenize("x")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "x")
    
    def test_underscore_identifier(self):
        """Test identifier starting with underscore"""
        tokens = tokenize("_private")
        self.assertEqual(tokens[0].value, "_private")
    
    def test_mixed_case_identifier(self):
        """Test mixed case identifier"""
        tokens = tokenize("myVariable")
        self.assertEqual(tokens[0].value, "myVariable")
    
    def test_alphanumeric_identifier(self):
        """Test alphanumeric identifier"""
        tokens = tokenize("var123")
        self.assertEqual(tokens[0].value, "var123")
    
    def test_snake_case_identifier(self):
        """Test snake_case identifier"""
        tokens = tokenize("snake_case_var")
        self.assertEqual(tokens[0].value, "snake_case_var")
    
    def test_underscore_only(self):
        """Test underscore as standalone token"""
        tokens = tokenize("_")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "_")


class TestLexerKeywords(unittest.TestCase):
    """Test keyword tokenization"""
    
    def test_all_keywords(self):
        """Test all keywords are recognized"""
        keywords = {
            "let": TokenType.LET,
            "const": TokenType.CONST,
            "mut": TokenType.MUT,
            "fn": TokenType.FN,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "match": TokenType.MATCH,
            "for": TokenType.FOR,
            "in": TokenType.IN,
            "while": TokenType.WHILE,
            "return": TokenType.RETURN,
            "struct": TokenType.STRUCT,
            "enum": TokenType.ENUM,
            "import": TokenType.IMPORT,
            "export": TokenType.EXPORT,
            "from": TokenType.FROM,
            "as": TokenType.AS,
        }
        
        for keyword, expected_type in keywords.items():
            tokens = tokenize(keyword)
            self.assertEqual(tokens[0].type, expected_type, f"Keyword '{keyword}' failed")
    
    def test_type_keywords(self):
        """Test type keywords"""
        type_keywords = {
            "bool": TokenType.BOOL_TYPE,
            "int": TokenType.INT_TYPE,
            "float": TokenType.FLOAT_TYPE,
            "str": TokenType.STR_TYPE,
        }
        
        for keyword, expected_type in type_keywords.items():
            tokens = tokenize(keyword)
            self.assertEqual(tokens[0].type, expected_type, f"Type '{keyword}' failed")
    
    def test_logical_operators(self):
        """Test logical operators as keywords"""
        tokens_and = tokenize("and")
        tokens_or = tokenize("or")
        tokens_not = tokenize("not")
        
        self.assertEqual(tokens_and[0].type, TokenType.AND)
        self.assertEqual(tokens_or[0].type, TokenType.OR)
        self.assertEqual(tokens_not[0].type, TokenType.NOT)


class TestLexerOperators(unittest.TestCase):
    """Test operator tokenization"""
    
    def test_arithmetic_operators(self):
        """Test arithmetic operators"""
        operators = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
        }
        
        for op, expected_type in operators.items():
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, expected_type, f"Operator '{op}' failed")
    
    def test_comparison_operators(self):
        """Test comparison operators"""
        operators = {
            "==": TokenType.EQEQ,
            "!=": TokenType.NEQ,
            "<<": TokenType.LT,
            ">": TokenType.GT,
            "<=": TokenType.LTE,
            ">=": TokenType.GTE,
        }
        
        for op, expected_type in operators.items():
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, expected_type, f"Operator '{op}' failed")
    
    def test_assignment_operator(self):
        """Test assignment operator"""
        tokens = tokenize("=")
        self.assertEqual(tokens[0].type, TokenType.EQ)
    
    def test_arrow_operator(self):
        """Test arrow operator"""
        tokens = tokenize("->")
        self.assertEqual(tokens[0].type, TokenType.ARROW)
    
    def test_pipe_operator(self):
        """Test pipe operator"""
        tokens = tokenize("|>")
        self.assertEqual(tokens[0].type, TokenType.PIPE)
    
    def test_qmark(self):
        """Test question mark"""
        tokens = tokenize("?")
        self.assertEqual(tokens[0].type, TokenType.QMARK)


class TestLexerDelimiters(unittest.TestCase):
    """Test delimiter tokenization"""
    
    def test_parentheses(self):
        """Test parentheses"""
        tokens = tokenize("()")
        self.assertEqual(tokens[0].type, TokenType.LPAREN)
        self.assertEqual(tokens[1].type, TokenType.RPAREN)
    
    def test_brackets(self):
        """Test square brackets"""
        tokens = tokenize("[]")
        self.assertEqual(tokens[0].type, TokenType.LBRACKET)
        self.assertEqual(tokens[1].type, TokenType.RBRACKET)
    
    def test_braces(self):
        """Test curly braces"""
        tokens = tokenize("{}")
        self.assertEqual(tokens[0].type, TokenType.LBRACE)
        self.assertEqual(tokens[1].type, TokenType.RBRACE)
    
    def test_colon(self):
        """Test colon"""
        tokens = tokenize(":")
        self.assertEqual(tokens[0].type, TokenType.COLON)
    
    def test_comma(self):
        """Test comma"""
        tokens = tokenize(",")
        self.assertEqual(tokens[0].type, TokenType.COMMA)
    
    def test_dot(self):
        """Test dot"""
        tokens = tokenize(".")
        self.assertEqual(tokens[0].type, TokenType.DOT)
    
    def test_backslash(self):
        """Test backslash"""
        tokens = tokenize("\\")
        self.assertEqual(tokens[0].type, TokenType.BACKSLASH)


class TestLexerIndentation(unittest.TestCase):
    """Test indentation handling"""
    
    def test_indent(self):
        """Test basic indentation"""
        source = """fn test()
  x = 1
"""
        tokens = tokenize(source)
        indent_found = any(t.type == TokenType.INDENT for t in tokens)
        dedent_found = any(t.type == TokenType.DEDENT for t in tokens)
        self.assertTrue(indent_found)
        self.assertTrue(dedent_found)
    
    def test_multiple_indents(self):
        """Test multiple indentation levels"""
        source = """fn outer()
  if true
    x = 1
"""
        tokens = tokenize(source)
        indents = [t for t in tokens if t.type == TokenType.INDENT]
        dedents = [t for t in tokens if t.type == TokenType.DEDENT]
        self.assertGreaterEqual(len(indents), 2)
        self.assertGreaterEqual(len(dedents), 2)
    
    def test_tab_indentation(self):
        """Test tab indentation (counts as 4 spaces)"""
        source = "fn test():\n\tx = 1"
        tokens = tokenize(source)
        # Should handle tab as indentation
        self.assertTrue(any(t.type == TokenType.INDENT for t in tokens))
    
    def test_invalid_dedent(self):
        """Test invalid dedent raises error"""
        source = """fn test()
  x = 1
 x = 2
"""
        with self.assertRaises(LexerError):
            tokenize(source)


class TestLexerComplex(unittest.TestCase):
    """Test complex tokenization scenarios"""
    
    def test_full_program(self):
        """Test tokenizing a full program"""
        source = '''fn factorial(n: int) -> int
  if n <= 1
    return 1
  else
    return n * factorial(n - 1)

let result = factorial(5)
println(result)
'''
        tokens = tokenize(source)
        # Should not raise any errors
        self.assertTrue(len(tokens) > 0)
        self.assertEqual(tokens[-1].type, TokenType.EOF)
    
    def test_mixed_content(self):
        """Test mixed content"""
        source = 'let x = 42  # This is a comment\n'
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.LET, types)
        self.assertIn(TokenType.IDENTIFIER, types)
        self.assertIn(TokenType.INT, types)
    
    def test_multiple_tokens_per_line(self):
        """Test multiple tokens on one line"""
        source = "let x = 1 + 2 * 3"
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertEqual(types.count(TokenType.INT), 3)
        self.assertIn(TokenType.PLUS, types)
        self.assertIn(TokenType.STAR, types)
    
    def test_consecutive_newlines(self):
        """Test consecutive newlines"""
        source = "\n\n\n"
        tokens = tokenize(source)
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        self.assertEqual(len(newlines), 3)


class TestLexerErrorHandling(unittest.TestCase):
    """Test lexer error handling"""
    
    def test_unexpected_character(self):
        """Test unexpected character raises error"""
        with self.assertRaises(LexerError) as ctx:
            tokenize("$")
        self.assertIn("Invalid character", str(ctx.exception))
    
    def test_error_shows_position(self):
        """Test error shows line and column"""
        with self.assertRaises(LexerError) as ctx:
            tokenize("line 1\nline 2\n$")
        error_msg = str(ctx.exception)
        self.assertIn("line", error_msg.lower())


class TestLexerPositions(unittest.TestCase):
    """Test token position tracking"""
    
    def test_line_tracking(self):
        """Test line number tracking"""
        source = "a\nb\nc"
        tokens = tokenize(source)
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(identifiers[0].line, 1)
        self.assertEqual(identifiers[1].line, 2)
        self.assertEqual(identifiers[2].line, 3)
    
    def test_column_tracking(self):
        """Test column tracking"""
        source = "  hello"
        tokens = tokenize(source)
        hello_token = [t for t in tokens if t.type == TokenType.IDENTIFIER][0]
        self.assertEqual(hello_token.column, 3)


class TestLexerEdgeCases(unittest.TestCase):
    """Test edge cases"""
    
    def test_very_long_identifier(self):
        """Test very long identifier"""
        long_name = "a" * 1000
        tokens = tokenize(long_name)
        self.assertEqual(tokens[0].value, long_name)
    
    def test_multiple_decimals(self):
        """Test multiple decimal points (should stop at first)"""
        tokens = tokenize("3.14.15")
        # Should tokenize 3.14 as float, then .15 would be dot + float
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
    
    def test_number_followed_by_identifier(self):
        """Test number immediately followed by identifier"""
        tokens = tokenize("42abc")
        # Should be int 42 followed by identifier abc
        self.assertEqual(tokens[0].type, TokenType.INT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
    
    def test_negative_number(self):
        """Test negative number"""
        tokens = tokenize("-42")
        self.assertEqual(tokens[0].type, TokenType.MINUS)
        self.assertEqual(tokens[1].type, TokenType.INT)


if __name__ == "__main__":
    unittest.main()
