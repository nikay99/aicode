"""
AICode Standard Library Tests
Tests for Unicode mathematical symbol implementations
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stdlib_ai import (
    map_func,
    filter_func,
    reduce_func,
    contains_func,
    not_contains_func,
    reverse_func,
    concat_func,
    zip_func,
    strlen_func,
    substring_func,
    split_func,
    join_func,
    replace_func,
    abs_func,
    min_func,
    max_func,
    sum_func,
    range_func,
    StdlibError,
    BUILTINS,
)


class TestUnicodeListOperations(unittest.TestCase):
    """Test Unicode mathematical symbol list operations"""

    def test_forall_map_double(self):
        """∀ (map) - Apply function to all elements"""
        lst = [1, 2, 3]
        result = map_func(lambda x: x * 2, lst)
        self.assertEqual(result, [2, 4, 6])

    def test_forall_map_empty(self):
        """∀ (map) - Empty list"""
        result = map_func(lambda x: x * 2, [])
        self.assertEqual(result, [])

    def test_exists_filter_evens(self):
        """∃ (filter) - Filter elements based on predicate"""
        lst = [1, 2, 3, 4, 5, 6]
        result = filter_func(lambda x: x % 2 == 0, lst)
        self.assertEqual(result, [2, 4, 6])

    def test_exists_filter_empty(self):
        """∃ (filter) - Empty list"""
        result = filter_func(lambda x: x > 0, [])
        self.assertEqual(result, [])

    def test_sum_reduce_addition(self):
        """∑ (reduce) - Reduce list to single value"""
        lst = [1, 2, 3, 4]
        result = reduce_func(lambda acc, x: acc + x, lst, 0)
        self.assertEqual(result, 10)

    def test_sum_reduce_multiplication(self):
        """∑ (reduce) - Multiply all elements"""
        lst = [1, 2, 3, 4]
        result = reduce_func(lambda acc, x: acc * x, lst, 1)
        self.assertEqual(result, 24)

    def test_element_of_contains(self):
        """∈ (element of) - Check if element is in list"""
        lst = [1, 2, 3, 4, 5]
        self.assertTrue(contains_func(3, lst))
        self.assertFalse(contains_func(10, lst))

    def test_not_element_of(self):
        """∉ (not element of) - Check if element is NOT in list"""
        lst = [1, 2, 3, 4, 5]
        self.assertTrue(not_contains_func(10, lst))
        self.assertFalse(not_contains_func(3, lst))

    def test_reverse_list(self):
        """∋ (reverse) - Reverse a list"""
        lst = [1, 2, 3, 4, 5]
        result = reverse_func(lst)
        self.assertEqual(result, [5, 4, 3, 2, 1])

    def test_reverse_empty(self):
        """∋ (reverse) - Reverse empty list"""
        result = reverse_func([])
        self.assertEqual(result, [])

    def test_concat_lists(self):
        """⊕ (concat) - Concatenate two lists"""
        lst1 = [1, 2, 3]
        lst2 = [4, 5, 6]
        result = concat_func(lst1, lst2)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_concat_empty(self):
        """⊕ (concat) - Concatenate with empty list"""
        result = concat_func([1, 2, 3], [])
        self.assertEqual(result, [1, 2, 3])

    def test_zip_lists(self):
        """⊗ (zip) - Zip two lists together"""
        lst1 = [1, 2, 3]
        lst2 = ['a', 'b', 'c']
        result = zip_func(lst1, lst2)
        self.assertEqual(result, [(1, 'a'), (2, 'b'), (3, 'c')])

    def test_zip_unequal_length(self):
        """⊗ (zip) - Zip lists of unequal length"""
        lst1 = [1, 2, 3, 4]
        lst2 = ['a', 'b']
        result = zip_func(lst1, lst2)
        self.assertEqual(result, [(1, 'a'), (2, 'b')])

    def test_type_error_on_non_list(self):
        """Unicode functions should error on non-list inputs"""
        with self.assertRaises(StdlibError):
            map_func(lambda x: x, "not a list")
        with self.assertRaises(StdlibError):
            filter_func(lambda x: True, "not a list")
        with self.assertRaises(StdlibError):
            contains_func(1, "not a list")


class TestStringOperations(unittest.TestCase):
    """Test string operations"""

    def test_strlen(self):
        """strlen - Get string length"""
        self.assertEqual(strlen_func("hello"), 5)
        self.assertEqual(strlen_func(""), 0)

    def test_substring_with_end(self):
        """substring - Extract substring with end"""
        s = "hello world"
        self.assertEqual(substring_func(s, 0, 5), "hello")
        self.assertEqual(substring_func(s, 6, 11), "world")

    def test_substring_without_end(self):
        """substring - Extract substring from start to end"""
        s = "hello world"
        self.assertEqual(substring_func(s, 6), "world")

    def test_split_default(self):
        """split - Split string by default delimiter (space)"""
        s = "hello world test"
        result = split_func(s)
        self.assertEqual(result, ["hello", "world", "test"])

    def test_split_delimiter(self):
        """split - Split string by custom delimiter"""
        s = "a,b,c,d"
        result = split_func(s, ",")
        self.assertEqual(result, ["a", "b", "c", "d"])

    def test_join(self):
        """join - Join list into string"""
        lst = ["hello", "world", "test"]
        result = join_func(" ", lst)
        self.assertEqual(result, "hello world test")

    def test_join_empty(self):
        """join - Join empty list"""
        result = join_func(",", [])
        self.assertEqual(result, "")

    def test_replace(self):
        """replace - Replace substring"""
        s = "hello world"
        result = replace_func(s, "world", "universe")
        self.assertEqual(result, "hello universe")

    def test_replace_all_occurrences(self):
        """replace - Replace all occurrences"""
        s = "banana"
        result = replace_func(s, "a", "o")
        self.assertEqual(result, "bonono")


class TestMathOperations(unittest.TestCase):
    """Test math operations"""

    def test_abs_positive(self):
        """abs - Absolute value of positive number"""
        self.assertEqual(abs_func(5), 5)

    def test_abs_negative(self):
        """abs - Absolute value of negative number"""
        self.assertEqual(abs_func(-5), 5)

    def test_abs_float(self):
        """abs - Absolute value of float"""
        self.assertEqual(abs_func(-3.14), 3.14)

    def test_min_list(self):
        """min - Minimum of list"""
        lst = [3, 1, 4, 1, 5, 9]
        self.assertEqual(min_func(lst), 1)

    def test_max_list(self):
        """max - Maximum of list"""
        lst = [3, 1, 4, 1, 5, 9]
        self.assertEqual(max_func(lst), 9)

    def test_sum_list(self):
        """sum - Sum of list"""
        lst = [1, 2, 3, 4, 5]
        self.assertEqual(sum_func(lst), 15)

    def test_sum_empty(self):
        """sum - Sum of empty list"""
        self.assertEqual(sum_func([]), 0)

    def test_range_one_arg(self):
        """range - One argument (end)"""
        result = range_func(5)
        self.assertEqual(result, [0, 1, 2, 3, 4])

    def test_range_two_args(self):
        """range - Two arguments (start, end)"""
        result = range_func(1, 5)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_range_three_args(self):
        """range - Three arguments (start, end, step)"""
        result = range_func(0, 10, 2)
        self.assertEqual(result, [0, 2, 4, 6, 8])


class TestBuiltinsDict(unittest.TestCase):
    """Test BUILTINS dictionary"""

    def test_unicode_symbols_present(self):
        """Unicode symbols should be in BUILTINS"""
        unicode_symbols = ["∀", "∃", "∑", "∈", "∉", "∋", "⊕", "⊗"]
        for symbol in unicode_symbols:
            self.assertIn(symbol, BUILTINS)

    def test_ascii_aliases_present(self):
        """ASCII aliases should be in BUILTINS"""
        ascii_aliases = ["map", "filter", "reduce", "contains", "reverse", "concat", "zip"]
        for alias in ascii_aliases:
            self.assertIn(alias, BUILTINS)

    def test_string_functions_present(self):
        """String functions should be in BUILTINS"""
        string_funcs = ["strlen", "substring", "split", "join", "replace"]
        for func in string_funcs:
            self.assertIn(func, BUILTINS)

    def test_math_functions_present(self):
        """Math functions should be in BUILTINS"""
        math_funcs = ["abs", "min", "max", "sum", "range", "length"]
        for func in math_funcs:
            self.assertIn(func, BUILTINS)

    def test_io_functions_present(self):
        """I/O functions should be in BUILTINS"""
        io_funcs = ["print", "println", "input"]
        for func in io_funcs:
            self.assertIn(func, BUILTINS)


class TestIntegration(unittest.TestCase):
    """Integration tests using multiple functions"""

    def test_map_filter_pipeline(self):
        """Map then filter pipeline"""
        lst = [1, 2, 3, 4, 5, 6]
        # Double all numbers, then keep only even
        doubled = map_func(lambda x: x * 2, lst)
        evens = filter_func(lambda x: x % 4 == 0, doubled)
        self.assertEqual(evens, [4, 8, 12])

    def test_reduce_with_map(self):
        """Reduce the result of a map"""
        lst = [1, 2, 3, 4]
        doubled = map_func(lambda x: x * 2, lst)
        total = reduce_func(lambda acc, x: acc + x, doubled, 0)
        self.assertEqual(total, 20)

    def test_string_split_join(self):
        """Split and then join strings"""
        s = "hello,world,test"
        parts = split_func(s, ",")
        result = join_func(" ", parts)
        self.assertEqual(result, "hello world test")


if __name__ == "__main__":
    unittest.main()
