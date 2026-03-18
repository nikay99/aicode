"""
Unicode Lexer Tests - Comprehensive coverage for all Unicode symbols
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.lexer_ai import tokenize, TokenType


class TestUnicodeDeclarationTokens(unittest.TestCase):
    """Test Unicode declaration tokens"""

    def test_var_token(self):
        tokens = tokenize("𝕍 x = 42")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.VAR, types)

    def test_const_token(self):
        tokens = tokenize("𝔠 PI = 3.14")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.CONST, types)

    def test_mut_token(self):
        tokens = tokenize("μ counter = 0")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.MUT, types)

    def test_func_token(self):
        tokens = tokenize("λ add(x, y)")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FUNC, types)


class TestUnicodeControlFlowTokens(unittest.TestCase):
    """Test Unicode control flow tokens"""

    def test_if_token(self):
        tokens = tokenize("? x > 0")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.IF, types)

    def test_else_token(self):
        tokens = tokenize("x : y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.ELSE, types)

    def test_match_token(self):
        tokens = tokenize("∼ x")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.MATCH, types)

    def test_for_token(self):
        tokens = tokenize("∀ x ∈ list")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FOR, types)

    def test_in_token(self):
        tokens = tokenize("x ∈ list")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.IN, types)

    def test_while_token(self):
        tokens = tokenize("⟲ condition")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.WHILE, types)

    def test_return_token(self):
        tokens = tokenize("← result")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.RETURN, types)


class TestUnicodeTypeTokens(unittest.TestCase):
    """Test Unicode type tokens"""

    def test_int_type_token(self):
        tokens = tokenize("ℤ")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.INT_TYPE, types)

    def test_float_type_token(self):
        tokens = tokenize("ℝ")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FLOAT_TYPE, types)

    def test_str_type_token(self):
        tokens = tokenize("𝕊")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.STR_TYPE, types)

    def test_bool_type_token(self):
        tokens = tokenize("𝔹")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.BOOL_TYPE, types)

    def test_list_type_token(self):
        tokens = tokenize("𝕃")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.LIST_TYPE, types)

    def test_dict_type_token(self):
        tokens = tokenize("𝔻")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.DICT_TYPE, types)


class TestUnicodeLogicTokens(unittest.TestCase):
    """Test Unicode logic tokens"""

    def test_and_token(self):
        tokens = tokenize("x ∧ y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.AND, types)

    def test_or_token(self):
        tokens = tokenize("x ∨ y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.OR, types)

    def test_not_token(self):
        tokens = tokenize("¬flag")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.NOT, types)


class TestUnicodeLiteralTokens(unittest.TestCase):
    """Test Unicode literal tokens"""

    def test_true_literal(self):
        tokens = tokenize("⊤")
        bool_token = [t for t in tokens if t.type == TokenType.BOOL][0]
        self.assertEqual(bool_token.value, True)

    def test_false_literal(self):
        tokens = tokenize("⊥")
        bool_token = [t for t in tokens if t.type == TokenType.BOOL][0]
        self.assertEqual(bool_token.value, False)

    def test_null_literal(self):
        tokens = tokenize("∅")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.NULL, types)


class TestUnicodeOperatorTokens(unittest.TestCase):
    """Test Unicode operator tokens"""

    def test_assign_token(self):
        tokens = tokenize("x ≔ 42")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.ASSIGN, types)

    def test_arrow_token(self):
        tokens = tokenize("→ int")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.ARROW, types)

    def test_pipe_token(self):
        tokens = tokenize("data ▷ transform")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.PIPE, types)

    def test_neq_token(self):
        tokens = tokenize("x ≠ y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.NEQ, types)

    def test_lte_token(self):
        tokens = tokenize("x ≤ y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.LTE, types)

    def test_gte_token(self):
        tokens = tokenize("x ≥ y")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.GTE, types)


class TestUnicodeFunctionalTokens(unittest.TestCase):
    """Test Unicode functional programming tokens"""

    def test_filter_token(self):
        tokens = tokenize("∃ list (λ x: x > 0)")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FILTER, types)

    def test_reduce_token(self):
        tokens = tokenize("∑ list (λ acc x: acc + x)")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.REDUCE, types)

    def test_compose_token(self):
        tokens = tokenize("f ∘ g")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.COMPOSE, types)


class TestUnicodeStructureTokens(unittest.TestCase):
    """Test Unicode structure tokens"""

    def test_struct_token(self):
        tokens = tokenize("Σ Point")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.STRUCT, types)

    def test_enum_token(self):
        tokens = tokenize("𝔼 Status")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.ENUM, types)


class TestUnicodeModuleTokens(unittest.TestCase):
    """Test Unicode module tokens"""

    def test_import_token(self):
        tokens = tokenize("↓ math")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.IMPORT, types)

    def test_export_token(self):
        tokens = tokenize("↑ add")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.EXPORT, types)


class TestUnicodeBrackets(unittest.TestCase):
    """Test Unicode bracket tokens"""

    def test_langle_token(self):
        tokens = tokenize("⟨ args ⟩")
        types = [t.type for t in tokens]
        self.assertIn(TokenType.LANGLE, types)
        self.assertIn(TokenType.RANGLE, types)


class TestUnicodeComplexPrograms(unittest.TestCase):
    """Test complex Unicode programs"""

    def test_factorial_unicode(self):
        source = """
λ factorial(n)
  ? n ≤ 1
    ← 1
  :
    ← n * factorial(n - 1)
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FUNC, types)
        self.assertIn(TokenType.IF, types)
        self.assertIn(TokenType.ELSE, types)
        self.assertIn(TokenType.RETURN, types)
        self.assertIn(TokenType.LTE, types)

    def test_list_comprehension_unicode(self):
        source = """
∀ x ∈ [1, 2, 3, 4, 5]
  println(x)
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FOR, types)
        self.assertIn(TokenType.IN, types)

    def test_filter_reduce_unicode(self):
        source = """
𝔠 numbers = [1, 2, 3, 4, 5]
𝔠 evens = ∃ numbers (λ x: x % 2 = 0)
𝔠 total = ∑ numbers (λ acc x: acc + x) 0
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.CONST, types)
        self.assertIn(TokenType.FILTER, types)
        self.assertIn(TokenType.REDUCE, types)
        self.assertIn(TokenType.FUNC, types)

    def test_pattern_match_unicode(self):
        source = """
∼ x
  1 → "one"
  2 → "two"
  _ → "other"
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.MATCH, types)
        self.assertIn(TokenType.ARROW, types)

    def test_struct_definition_unicode(self):
        source = """
Σ Point
  x: ℝ
  y: ℝ
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.STRUCT, types)
        self.assertIn(TokenType.FLOAT_TYPE, types)

    def test_lambda_unicode(self):
        source = "λ x y: x + y"
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FUNC, types)

    def test_while_loop_unicode(self):
        source = """
μ i = 0
⟲ i < 10
  println(i)
  i ≔ i + 1
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.MUT, types)
        self.assertIn(TokenType.WHILE, types)
        self.assertIn(TokenType.ASSIGN, types)

    def test_boolean_unicode(self):
        source = """
𝔠 flag = ⊤
𝔠 inverted = ¬flag
"""
        tokens = tokenize(source)
        bool_tokens = [t for t in tokens if t.type == TokenType.BOOL]
        self.assertEqual(len(bool_tokens), 1)
        self.assertEqual(bool_tokens[0].value, True)

    def test_type_annotations_unicode(self):
        source = "𝕍 x: ℤ = 42"
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.VAR, types)
        self.assertIn(TokenType.INT_TYPE, types)

    def test_function_with_types_unicode(self):
        source = """
λ add(x: ℤ, y: ℤ) → ℤ
  ← x + y
"""
        tokens = tokenize(source)
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FUNC, types)
        self.assertIn(TokenType.INT_TYPE, types)
        self.assertIn(TokenType.ARROW, types)
        self.assertIn(TokenType.RETURN, types)


class TestGreekLetters(unittest.TestCase):
    """Test Greek letter identifiers"""

    def test_alpha_identifier(self):
        tokens = tokenize("α")
        id_token = [t for t in tokens if t.type == TokenType.IDENTIFIER][0]
        self.assertEqual(id_token.value, "α")

    def test_beta_identifier(self):
        tokens = tokenize("β")
        id_token = [t for t in tokens if t.type == TokenType.IDENTIFIER][0]
        self.assertEqual(id_token.value, "β")

    def test_greek_lambda(self):
        tokens = tokenize("λ α β: α + β")
        id_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        values = [t.value for t in id_tokens]
        self.assertIn("α", values)
        self.assertIn("β", values)

    def test_subscript_identifiers(self):
        tokens = tokenize("x₁ x₂")
        id_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(id_tokens), 2)


class TestUnicodeAllTokens(unittest.TestCase):
    """Test all Unicode tokens exist in mapping"""

    def test_all_unicode_tokens_mapped(self):
        from src.lexer_ai import UNICODE_TOKENS

        unicode_chars = [
            "𝕍",
            "𝔠",
            "μ",
            "λ",
            "?",
            ":",
            "∼",
            "∀",
            "∈",
            "⟲",
            "←",
            "ℤ",
            "ℝ",
            "𝕊",
            "𝔹",
            "𝕃",
            "𝔻",
            "Σ",
            "𝔼",
            "↓",
            "↑",
            "∧",
            "∨",
            "¬",
            "⊤",
            "⊥",
            "∅",
            "≔",
            "→",
            "▷",
            "≠",
            "≤",
            "≥",
            "∃",
            "∑",
            "∘",
            "⟨",
            "⟩",
        ]
        for char in unicode_chars:
            self.assertIn(
                char, UNICODE_TOKENS, f"Unicode character {char!r} not in mapping"
            )


class TestUnicodePositionTracking(unittest.TestCase):
    """Test position tracking for Unicode tokens"""

    def test_token_positions(self):
        source = "𝕍 x = 42"
        tokens = tokenize(source)
        var_token = [t for t in tokens if t.type == TokenType.VAR][0]
        self.assertEqual(var_token.line, 1)
        self.assertEqual(var_token.column, 1)

    def test_multiline_unicode_positions(self):
        source = "𝕍 x = 42\n𝔠 y = 100"
        tokens = tokenize(source)
        const_token = [t for t in tokens if t.type == TokenType.CONST][0]
        self.assertEqual(const_token.line, 2)


if __name__ == "__main__":
    unittest.main()
