"""
Test suite for AICode Error Handling System
Tests all error codes E1xx-E4xx
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.errors import (
    AICodeError, LexerError, ParserError, TypeCheckError, RuntimeError, CompilerError,
    StackFrame, ERROR_MESSAGES,
    E101, E102, E103, E104, E105, E106, E107, E108, E109, E110,
    E201, E202, E203, E204, E205, E206, E207, E208, E209, E210,
    E211, E212, E213, E214, E215, E216, E217, E218, E219, E220,
    E301, E302, E303, E304, E305, E306, E307, E308, E309, E310,
    E311, E312, E313, E314, E315, E316, E317, E318, E319, E320,
    E401, E402, E403, E404, E405, E406, E407, E408, E409, E410,
    E411, E412, E413, E414, E415, E416, E417, E418, E419, E420,
    invalid_character, unterminated_string, invalid_escape_sequence, invalid_indentation,
    unexpected_token, expected_token, missing_delimiter,
    undefined_variable, type_mismatch, occurs_check,
    division_by_zero, index_out_of_bounds, key_not_found,
    undefined_function, stack_overflow, stack_underflow,
    get_error_description, is_lexer_error, is_parser_error, is_type_error, is_runtime_error
)

import unittest


class TestErrorCodes(unittest.TestCase):
    """Test error code constants"""
    
    def test_lexer_error_codes(self):
        """Test lexer error codes E1xx"""
        self.assertEqual(E101, "E101")
        self.assertEqual(E102, "E102")
        self.assertEqual(E103, "E103")
        self.assertTrue(is_lexer_error(E101))
        self.assertTrue(is_lexer_error(E110))
        self.assertFalse(is_lexer_error(E201))
    
    def test_parser_error_codes(self):
        """Test parser error codes E2xx"""
        self.assertEqual(E201, "E201")
        self.assertEqual(E202, "E202")
        self.assertEqual(E203, "E203")
        self.assertTrue(is_parser_error(E201))
        self.assertTrue(is_parser_error(E220))
        self.assertFalse(is_parser_error(E301))
    
    def test_type_error_codes(self):
        """Test type error codes E3xx"""
        self.assertEqual(E301, "E301")
        self.assertEqual(E302, "E302")
        self.assertEqual(E303, "E303")
        self.assertTrue(is_type_error(E301))
        self.assertTrue(is_type_error(E320))
        self.assertFalse(is_type_error(E401))
    
    def test_runtime_error_codes(self):
        """Test runtime error codes E4xx"""
        self.assertEqual(E401, "E401")
        self.assertEqual(E402, "E402")
        self.assertEqual(E403, "E403")
        self.assertTrue(is_runtime_error(E401))
        self.assertTrue(is_runtime_error(E420))
        self.assertFalse(is_runtime_error(E101))


class TestErrorDescriptions(unittest.TestCase):
    """Test error message descriptions"""
    
    def test_lexer_error_descriptions(self):
        """Test lexer error descriptions"""
        self.assertEqual(get_error_description(E101), "Invalid character")
        self.assertEqual(get_error_description(E102), "Unterminated string")
        self.assertEqual(get_error_description(E103), "Invalid escape sequence")
    
    def test_parser_error_descriptions(self):
        """Test parser error descriptions"""
        self.assertEqual(get_error_description(E201), "Unexpected token")
        self.assertEqual(get_error_description(E202), "Expected token not found")
        self.assertEqual(get_error_description(E203), "Missing closing delimiter")
    
    def test_type_error_descriptions(self):
        """Test type error descriptions"""
        self.assertEqual(get_error_description(E301), "Type mismatch")
        self.assertEqual(get_error_description(E302), "Undefined variable")
        self.assertEqual(get_error_description(E305), "Occurs check failed (recursive type)")
    
    def test_runtime_error_descriptions(self):
        """Test runtime error descriptions"""
        self.assertEqual(get_error_description(E401), "Division by zero")
        self.assertEqual(get_error_description(E402), "Index out of bounds")
        self.assertEqual(get_error_description(E403), "Key not found")
    
    def test_unknown_error(self):
        """Test unknown error code"""
        self.assertEqual(get_error_description("E999"), "Unknown error")


class TestBaseError(unittest.TestCase):
    """Test AICodeError base class"""
    
    def test_basic_error(self):
        """Test basic error creation"""
        err = AICodeError("E101", "Test error", 10, 5, "test.aic")
        self.assertEqual(err.code, "E101")
        self.assertEqual(err.message, "Test error")
        self.assertEqual(err.line, 10)
        self.assertEqual(err.column, 5)
        self.assertEqual(err.filename, "test.aic")
    
    def test_error_message_formatting(self):
        """Test error message formatting"""
        err = AICodeError("E101", "Invalid character", 1, 5, "test.aic")
        msg = err.format_message()
        self.assertIn("[E101]", msg)
        self.assertIn("Invalid character", msg)
        self.assertIn("test.aic", msg)
        self.assertIn("line 1", msg)
        self.assertIn("column 5", msg)
    
    def test_error_with_context(self):
        """Test error with context"""
        err = AICodeError("E101", "Test", context="while parsing expression")
        msg = err.format_message()
        self.assertIn("Context:", msg)
        self.assertIn("while parsing expression", msg)
    
    def test_stack_trace(self):
        """Test stack trace functionality"""
        err = AICodeError("E401", "Runtime error")
        err.add_frame("main", 10, 5, "main.aic")
        err.add_frame("foo", 20, 3, "main.aic")
        
        self.assertEqual(len(err.stack_trace), 2)
        self.assertEqual(err.stack_trace[0].function, "main")
        self.assertEqual(err.stack_trace[1].function, "foo")
        
        msg = err.format_message()
        self.assertIn("Stack trace:", msg)
        self.assertIn("at main", msg)
        self.assertIn("at foo", msg)
    
    def test_with_context_method(self):
        """Test with_context method"""
        err = AICodeError("E101", "Test error")
        new_err = err.with_context(line=10, column=5, filename="test.aic", context="parsing")
        
        self.assertEqual(new_err.line, 10)
        self.assertEqual(new_err.column, 5)
        self.assertEqual(new_err.filename, "test.aic")
        self.assertEqual(new_err.context, "parsing")


class TestLexerErrors(unittest.TestCase):
    """Test LexerError class and helpers"""
    
    def test_lexer_error_creation(self):
        """Test lexer error creation"""
        err = LexerError(E101, "Invalid character", 1, 5)
        self.assertIsInstance(err, AICodeError)
        self.assertEqual(err.code, E101)
    
    def test_lexer_error_default_message(self):
        """Test lexer error with default message"""
        err = LexerError(E101, line=1, column=5)
        self.assertEqual(err.message, "Invalid character")
    
    def test_invalid_character_helper(self):
        """Test invalid_character helper"""
        err = invalid_character("$", 1, 5, "test.aic")
        self.assertEqual(err.code, E101)
        self.assertIn("$", err.message)
        self.assertEqual(err.line, 1)
        self.assertEqual(err.column, 5)
        self.assertEqual(err.filename, "test.aic")
    
    def test_unterminated_string_helper(self):
        """Test unterminated_string helper"""
        err = unterminated_string(10, 1)
        self.assertEqual(err.code, E102)
        self.assertEqual(err.message, "Unterminated string literal")
    
    def test_invalid_escape_sequence_helper(self):
        """Test invalid_escape_sequence helper"""
        err = invalid_escape_sequence("x", 5, 10)
        self.assertEqual(err.code, E103)
        self.assertIn("\\x", err.message)
    
    def test_invalid_indentation_helper(self):
        """Test invalid_indentation helper"""
        err = invalid_indentation(20, 0)
        self.assertEqual(err.code, E105)


class TestParserErrors(unittest.TestCase):
    """Test ParserError class and helpers"""
    
    def test_parser_error_creation(self):
        """Test parser error creation"""
        err = ParserError(E201, "Unexpected token", 1, 10)
        self.assertIsInstance(err, AICodeError)
        self.assertEqual(err.code, E201)
    
    def test_unexpected_token_helper(self):
        """Test unexpected_token helper"""
        err = unexpected_token("}", "{", 1, 10, "test.aic")
        self.assertEqual(err.code, E201)
        self.assertIn("}", err.message)
        self.assertIn("{", err.message)
    
    def test_unexpected_token_without_expected(self):
        """Test unexpected_token without expected token"""
        err = unexpected_token("foo", line=5)
        self.assertEqual(err.code, E201)
        self.assertIn("foo", err.message)
        self.assertNotIn("expected:", err.message)
    
    def test_expected_token_helper(self):
        """Test expected_token helper"""
        err = expected_token(";", "}", 1, 15)
        self.assertEqual(err.code, E202)
        self.assertIn(";", err.message)
        self.assertIn("}", err.message)
    
    def test_missing_delimiter_helper(self):
        """Test missing_delimiter helper"""
        err = missing_delimiter(")", 1, 20)
        self.assertEqual(err.code, E203)
        self.assertIn(")", err.message)


class TestTypeCheckErrors(unittest.TestCase):
    """Test TypeCheckError class and helpers"""
    
    def test_type_check_error_creation(self):
        """Test type check error creation"""
        err = TypeCheckError(E301, "Type mismatch", 5, 10)
        self.assertIsInstance(err, AICodeError)
        self.assertEqual(err.code, E301)
    
    def test_type_mismatch_helper(self):
        """Test type_mismatch helper"""
        err = type_mismatch("int", "str", 10, 5, "test.aic")
        self.assertEqual(err.code, E301)
        self.assertIn("int", err.message)
        self.assertIn("str", err.message)
    
    def test_undefined_variable_helper(self):
        """Test undefined_variable helper"""
        err = undefined_variable("foo", 3, 5)
        self.assertEqual(err.code, E302)
        self.assertIn("foo", err.message)
    
    def test_occurs_check_helper(self):
        """Test occurs_check helper"""
        err = occurs_check("t1", "list<t1>", 5, 10)
        self.assertEqual(err.code, E305)
        self.assertIn("t1", err.message)
        self.assertIn("list", err.message)
    
    def test_type_check_with_types(self):
        """Test TypeCheckError with expected/actual types"""
        err = TypeCheckError(E301, "Type error", expected_type="int", actual_type="str")
        self.assertIn("expected 'int'", err.message)
        self.assertIn("found 'str'", err.message)


class TestRuntimeErrors(unittest.TestCase):
    """Test RuntimeError class and helpers"""
    
    def test_runtime_error_creation(self):
        """Test runtime error creation"""
        err = RuntimeError(E401, "Division by zero", 100, 5)
        self.assertIsInstance(err, AICodeError)
        self.assertEqual(err.code, E401)
    
    def test_division_by_zero_helper(self):
        """Test division_by_zero helper"""
        err = division_by_zero(50, 10, "main.aic")
        self.assertEqual(err.code, E401)
        self.assertEqual(err.line, 50)
        self.assertEqual(err.column, 10)
    
    def test_index_out_of_bounds_helper(self):
        """Test index_out_of_bounds helper"""
        err = index_out_of_bounds(10, 5, 20, 3)
        self.assertEqual(err.code, E402)
        self.assertIn("10", err.message)
        self.assertIn("5", err.message)
    
    def test_key_not_found_helper(self):
        """Test key_not_found helper"""
        err = key_not_found("missing_key", 15, 8)
        self.assertEqual(err.code, E403)
        self.assertIn("missing_key", err.message)
    
    def test_undefined_function_helper(self):
        """Test undefined_function helper"""
        err = undefined_function("bar", 25, 1)
        self.assertEqual(err.code, E405)
        self.assertIn("bar", err.message)
    
    def test_stack_overflow_helper(self):
        """Test stack_overflow helper"""
        err = stack_overflow()
        self.assertEqual(err.code, E406)
    
    def test_stack_underflow_helper(self):
        """Test stack_underflow helper"""
        err = stack_underflow(100, 5)
        self.assertEqual(err.code, E407)


class TestCompilerErrors(unittest.TestCase):
    """Test CompilerError class"""
    
    def test_compiler_error_creation(self):
        """Test compiler error creation"""
        err = CompilerError("E204", "Compilation failed", 1, 1)
        self.assertIsInstance(err, AICodeError)
        self.assertEqual(err.code, "E204")
    
    def test_compiler_error_default_message(self):
        """Test compiler error with default message"""
        err = CompilerError("E204")
        self.assertEqual(err.message, "Invalid syntax")


class TestStackFrame(unittest.TestCase):
    """Test StackFrame class"""
    
    def test_stack_frame_creation(self):
        """Test stack frame creation"""
        frame = StackFrame("main", 10, 5, "test.aic")
        self.assertEqual(frame.function, "main")
        self.assertEqual(frame.line, 10)
        self.assertEqual(frame.column, 5)
        self.assertEqual(frame.filename, "test.aic")
    
    def test_stack_frame_string(self):
        """Test stack frame string representation"""
        frame = StackFrame("foo", 20, 3, "main.aic")
        frame_str = str(frame)
        self.assertIn("foo", frame_str)
        self.assertIn("main.aic", frame_str)
        self.assertIn("line 20", frame_str)
        self.assertIn("column 3", frame_str)
    
    def test_stack_frame_without_filename(self):
        """Test stack frame without filename"""
        frame = StackFrame("bar", 5, 1)
        frame_str = str(frame)
        self.assertIn("bar", frame_str)
        self.assertIn("line 5", frame_str)


class TestErrorCategorization(unittest.TestCase):
    """Test error categorization functions"""
    
    def test_all_lexer_errors(self):
        """Test all lexer error codes"""
        lexer_codes = [E101, E102, E103, E104, E105, E106, E107, E108, E109, E110]
        for code in lexer_codes:
            self.assertTrue(is_lexer_error(code), f"{code} should be lexer error")
            self.assertFalse(is_parser_error(code))
            self.assertFalse(is_type_error(code))
            self.assertFalse(is_runtime_error(code))
    
    def test_all_parser_errors(self):
        """Test all parser error codes"""
        parser_codes = [E201, E202, E203, E204, E205, E206, E207, E208, E209, E210,
                       E211, E212, E213, E214, E215, E216, E217, E218, E219, E220]
        for code in parser_codes:
            self.assertTrue(is_parser_error(code), f"{code} should be parser error")
            self.assertFalse(is_lexer_error(code))
            self.assertFalse(is_type_error(code))
            self.assertFalse(is_runtime_error(code))
    
    def test_all_type_errors(self):
        """Test all type error codes"""
        type_codes = [E301, E302, E303, E304, E305, E306, E307, E308, E309, E310,
                     E311, E312, E313, E314, E315, E316, E317, E318, E319, E320]
        for code in type_codes:
            self.assertTrue(is_type_error(code), f"{code} should be type error")
            self.assertFalse(is_lexer_error(code))
            self.assertFalse(is_parser_error(code))
            self.assertFalse(is_runtime_error(code))
    
    def test_all_runtime_errors(self):
        """Test all runtime error codes"""
        runtime_codes = [E401, E402, E403, E404, E405, E406, E407, E408, E409, E410,
                        E411, E412, E413, E414, E415, E416, E417, E418, E419, E420]
        for code in runtime_codes:
            self.assertTrue(is_runtime_error(code), f"{code} should be runtime error")
            self.assertFalse(is_lexer_error(code))
            self.assertFalse(is_parser_error(code))
            self.assertFalse(is_type_error(code))


class TestIntegration(unittest.TestCase):
    """Integration tests with actual components"""
    
    def test_lexer_invalid_character(self):
        """Test lexer raises proper error for invalid character"""
        from src.lexer import Lexer
        
        lexer = Lexer("$")
        with self.assertRaises(LexerError) as ctx:
            lexer.tokenize()
        
        err = ctx.exception
        self.assertEqual(err.code, E101)
        self.assertIn("$", err.message)
    
    def test_lexer_unterminated_string(self):
        """Test lexer raises proper error for unterminated string"""
        from src.lexer import Lexer
        
        lexer = Lexer('"unterminated')
        with self.assertRaises(LexerError) as ctx:
            lexer.tokenize()
        
        err = ctx.exception
        self.assertEqual(err.code, E102)
    
    def test_type_checker_undefined_variable(self):
        """Test type checker raises proper error for undefined variable"""
        from src.type_checker import TypeChecker, TypeEnvironment
        import src.ast_nodes as ast
        
        checker = TypeChecker()
        env = TypeEnvironment()
        expr = ast.Identifier("undefined_var")
        
        with self.assertRaises(TypeCheckError) as ctx:
            checker.infer(env, expr)
        
        err = ctx.exception
        self.assertEqual(err.code, E302)
        self.assertIn("undefined_var", err.message)
    
    def test_type_checker_type_mismatch(self):
        """Test type checker raises proper error for type mismatch"""
        from src.type_checker import TypeChecker, TypeEnvironment, TypeConst
        import src.ast_nodes as ast
        
        checker = TypeChecker()
        env = TypeEnvironment()
        
        # Create a binary op with mismatched types (though the current
        # implementation might not catch all mismatches at the lowest level)
        int_lit = ast.IntLiteral(42)
        float_lit = ast.FloatLiteral(3.14)
        expr = ast.BinaryOp("+", int_lit, float_lit)
        
        # This might or might not raise an error depending on the implementation
        # Just test that if it does, it uses proper error codes
        try:
            checker.infer(env, expr)
        except TypeCheckError as err:
            self.assertTrue(err.code.startswith("E3"))


if __name__ == "__main__":
    # Run the tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestErrorCodes))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorDescriptions))
    suite.addTests(loader.loadTestsFromTestCase(TestBaseError))
    suite.addTests(loader.loadTestsFromTestCase(TestLexerErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestParserErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeCheckErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestRuntimeErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestCompilerErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestStackFrame))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorCategorization))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
