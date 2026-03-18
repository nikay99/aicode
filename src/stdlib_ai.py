"""
AICode v2.0 Standard Library
Unicode mathematical symbol implementations
"""

from typing import Any, List, Callable, Optional, Union
from functools import reduce as py_reduce

# Forward reference for BytecodeFunction
_bytecode_function_type = None


def _set_bytecode_function_type(t):
    """Set the BytecodeFunction type (called by VM)"""
    global _bytecode_function_type
    _bytecode_function_type = t


def _is_bytecode_function(obj):
    """Check if object is a BytecodeFunction"""
    return _bytecode_function_type is not None and isinstance(
        obj, _bytecode_function_type
    )


class StdlibError(Exception):
    """Standard library error"""

    pass


# =============================================================================
# List Operations
# =============================================================================


def map_func(lst: List[Any], func: Callable[[Any], Any]) -> List[Any]:
    """∀ (forall) - Map function over list"""
    if not isinstance(lst, list):
        raise StdlibError(f"∀ expects a list, got {type(lst)}")
    return [func(item) for item in lst]


def filter_func(lst: List[Any], pred: Callable[[Any], bool]) -> List[Any]:
    """∃ (exists) - Filter elements based on predicate"""
    if not isinstance(lst, list):
        raise StdlibError(f"∃ expects a list, got {type(lst)}")
    return [item for item in lst if pred(item)]


def reduce_func(lst: List[Any], func: Callable[[Any, Any], Any], initial: Any) -> Any:
    """∑ (sum) - Reduce list to single value"""
    if not isinstance(lst, list):
        raise StdlibError(f"∑ expects a list, got {type(lst)}")
    result = initial
    for item in lst:
        result = func(result, item)
    return result


def contains_func(item: Any, lst: List[Any]) -> bool:
    """∈ (element of) - Check if element is in list"""
    if not isinstance(lst, list):
        raise StdlibError(f"∈ expects a list, got {type(lst)}")
    return item in lst


def not_contains_func(item: Any, lst: List[Any]) -> bool:
    """∉ (not element of) - Check if element is not in list"""
    if not isinstance(lst, list):
        raise StdlibError(f"∉ expects a list, got {type(lst)}")
    return item not in lst


# =============================================================================
# Result Type for Error Handling
# =============================================================================


class Ok:
    """Ok result variant"""

    def __init__(self, value):
        self.value = value
        self.is_ok = True
        self.is_err = False

    def __repr__(self):
        return f"Ok({self.value!r})"


class Err:
    """Err result variant"""

    def __init__(self, error):
        self.error = error
        self.is_ok = False
        self.is_err = True

    def __repr__(self):
        return f"Err({self.error!r})"


def is_ok_func(result) -> bool:
    """Check if result is Ok"""
    return hasattr(result, "is_ok") and result.is_ok


def is_err_func(result) -> bool:
    """Check if result is Err"""
    return hasattr(result, "is_err") and result.is_err


def unwrap_func(result):
    """Unwrap Ok value or raise error"""
    if is_ok_func(result):
        return result.value
    raise StdlibError(f"Cannot unwrap Err: {result}")


def unwrap_or_func(result, default):
    """Unwrap Ok value or return default"""
    if is_ok_func(result):
        return result.value
    return default


def reverse_func(lst: List[Any]) -> List[Any]:
    """∋ (contains) - Reverse a list"""
    if not isinstance(lst, list):
        raise StdlibError(f"∋ expects a list, got {type(lst)}")
    return lst[::-1]


def concat_func(lst1: List[Any], lst2: List[Any]) -> List[Any]:
    """⊕ (oplus) - Concatenate two lists"""
    if not isinstance(lst1, list):
        raise StdlibError(f"⊕ first argument must be a list, got {type(lst1)}")
    if not isinstance(lst2, list):
        raise StdlibError(f"⊕ second argument must be a list, got {type(lst2)}")
    return lst1 + lst2


def zip_func(lst1: List[Any], lst2: List[Any]) -> List[tuple]:
    """⊗ (otimes) - Zip two lists together"""
    if not isinstance(lst1, list):
        raise StdlibError(f"⊗ first argument must be a list, got {type(lst1)}")
    if not isinstance(lst2, list):
        raise StdlibError(f"⊗ second argument must be a list, got {type(lst2)}")
    return list(zip(lst1, lst2))


# =============================================================================
# String Operations
# =============================================================================


def strlen_func(s: str) -> int:
    """strlen - Get string length"""
    if not isinstance(s, str):
        raise StdlibError(f"strlen expects a string, got {type(s)}")
    return len(s)


def substring_func(s: str, start: int, end: Optional[int] = None) -> str:
    """substring - Extract substring"""
    if not isinstance(s, str):
        raise StdlibError(f"substring expects a string, got {type(s)}")
    if end is None:
        return s[start:]
    return s[start:end]


def split_func(s: str, delimiter: str = " ") -> List[str]:
    """split - Split string by delimiter"""
    if not isinstance(s, str):
        raise StdlibError(f"split expects a string, got {type(s)}")
    return s.split(delimiter)


def join_func(delimiter: str, lst: List[str]) -> str:
    """join - Join list into string"""
    if not isinstance(delimiter, str):
        raise StdlibError(f"join expects delimiter as string, got {type(delimiter)}")
    if not isinstance(lst, list):
        raise StdlibError(f"join expects a list, got {type(lst)}")
    return delimiter.join(str(item) for item in lst)


def replace_func(s: str, old: str, new: str) -> str:
    """replace - Replace substring"""
    if not isinstance(s, str):
        raise StdlibError(f"replace expects a string, got {type(s)}")
    return s.replace(old, new)


def chr_func(code: int) -> str:
    """chr - Convert Unicode code point to character"""
    if not isinstance(code, int):
        raise StdlibError(f"chr expects an integer, got {type(code)}")
    return chr(code)


def ord_func(c: str) -> int:
    """ord - Get Unicode code point of character"""
    if not isinstance(c, str) or len(c) != 1:
        raise StdlibError(f"ord expects a single character string, got {c!r}")
    return ord(c)


# =============================================================================
# Math Operations
# =============================================================================


def abs_func(x: Union[int, float]) -> Union[int, float]:
    """abs - Absolute value"""
    if not isinstance(x, (int, float)):
        raise StdlibError(f"abs expects a number, got {type(x)}")
    return abs(x)


def min_func(lst: List[Any]) -> Any:
    """min - Minimum of list"""
    if not isinstance(lst, list):
        raise StdlibError(f"min expects a list, got {type(lst)}")
    if not lst:
        raise StdlibError("min cannot find minimum of empty list")
    return min(lst)


def max_func(lst: List[Any]) -> Any:
    """max - Maximum of list"""
    if not isinstance(lst, list):
        raise StdlibError(f"max expects a list, got {type(lst)}")
    if not lst:
        raise StdlibError("max cannot find maximum of empty list")
    return max(lst)


def sum_func(lst: List[Union[int, float]]) -> Union[int, float]:
    """sum - Sum of list"""
    if not isinstance(lst, list):
        raise StdlibError(f"sum expects a list, got {type(lst)}")
    return sum(lst)


def range_func(*args) -> List[int]:
    """range - Generate range of numbers"""
    if len(args) == 1:
        return list(range(args[0]))
    elif len(args) == 2:
        return list(range(args[0], args[1]))
    elif len(args) == 3:
        return list(range(args[0], args[1], args[2]))
    raise StdlibError("range() takes 1-3 arguments")


# =============================================================================
# I/O Operations
# =============================================================================


def print_func(*args) -> None:
    """print - Print without newline"""
    print(*args, end="")


def println_func(*args) -> None:
    """println - Print with newline"""
    print(*args)


def input_func(prompt: str = "") -> str:
    """input - Read user input"""
    return input(prompt)


# =============================================================================
# Dictionary of all builtins for easy registration
# =============================================================================

BUILTINS = {
    # Unicode mathematical symbols
    "∀": map_func,
    "∃": filter_func,
    "∑": reduce_func,
    "∈": contains_func,
    "∉": not_contains_func,
    "∋": reverse_func,
    "⊕": concat_func,
    "⊗": zip_func,
    # String operations
    "strlen": strlen_func,
    "substring": substring_func,
    "split": split_func,
    "join": join_func,
    "replace": replace_func,
    "chr": chr_func,
    "ord": ord_func,
    # Math operations
    "abs": abs_func,
    "min": min_func,
    "max": max_func,
    "sum": sum_func,
    "range": range_func,
    "length": len,
    # I/O operations
    "print": print_func,
    "println": println_func,
    "input": input_func,
    # ASCII aliases for convenience
    "map": map_func,
    "filter": filter_func,
    "reduce": reduce_func,
    "contains": contains_func,
    "not_contains": not_contains_func,
    "reverse": reverse_func,
    "concat": concat_func,
    "zip": zip_func,
    # Result type
    "Ok": Ok,
    "Err": Err,
    "is_ok": is_ok_func,
    "is_err": is_err_func,
    "unwrap": unwrap_func,
    "unwrap_or": unwrap_or_func,
}
