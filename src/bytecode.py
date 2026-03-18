"""
AICode v2.0 Bytecode Format and Instructions
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any, Union, Dict, Tuple


class OpCode(Enum):
    """Bytecode opcodes"""

    # Stack operations
    PUSH_CONST = auto()  # PUSH_CONST idx - push constant[idx] onto stack
    PUSH_NULL = auto()  # PUSH_NULL - push null
    POP = auto()  # POP - pop top of stack
    DUP = auto()  # DUP - duplicate top of stack
    SWAP = auto()  # SWAP - swap top two stack items

    # Variable operations
    LOAD_LOCAL = auto()  # LOAD_LOCAL idx - load local variable
    STORE_LOCAL = auto()  # STORE_LOCAL idx - store to local variable
    LOAD_GLOBAL = auto()  # LOAD_GLOBAL idx - load global variable
    STORE_GLOBAL = auto()  # STORE_GLOBAL idx - store to global variable

    # Arithmetic
    ADD = auto()  # ADD - pop two, push sum
    SUB = auto()  # SUB - pop two, push difference
    MUL = auto()  # MUL - pop two, push product
    DIV = auto()  # DIV - pop two, push quotient
    MOD = auto()  # MOD - pop two, push remainder
    NEG = auto()  # NEG - negate top of stack

    # Comparison
    EQ = auto()  # EQ - equal
    NE = auto()  # NE - not equal
    LT = auto()  # LT - less than
    GT = auto()  # GT - greater than
    LE = auto()  # LE - less or equal
    GE = auto()  # GE - greater or equal

    # Logical
    NOT = auto()  # NOT - logical not
    AND = auto()  # AND - logical and
    OR = auto()  # OR - logical or

    # Control flow
    JUMP = auto()  # JUMP offset - unconditional jump
    JUMP_IF_FALSE = auto()  # JUMP_IF_FALSE offset - jump if top is false
    JUMP_IF_TRUE = auto()  # JUMP_IF_TRUE offset - jump if top is true
    CALL = auto()  # CALL argc - call function with argc args
    RETURN = auto()  # RETURN - return from function
    RETURN_VALUE = auto()  # RETURN_VALUE - return top of stack

    # Collection operations
    BUILD_LIST = auto()  # BUILD_LIST count - build list from count items
    BUILD_DICT = auto()  # BUILD_DICT count - build dict from count pairs
    INDEX_GET = auto()  # INDEX_GET - get item at index
    INDEX_SET = auto()  # INDEX_SET - set item at index
    GET_ATTR = auto()  # GET_ATTR idx - get attribute by name index
    SET_ATTR = auto()  # SET_ATTR idx - set attribute by name index

    # Iteration
    ITER = auto()  # ITER - make iterator from collection
    ITER_NEXT = auto()  # ITER_NEXT offset - get next or jump

    # Miscellaneous
    PRINT = auto()  # PRINT - print top of stack
    PRINTLN = auto()  # PRINTLN - print with newline
    NOP = auto()  # NOP - no operation
    HALT = auto()  # HALT - stop execution


@dataclass
class Instruction:
    """A single bytecode instruction"""

    opcode: OpCode
    operand: int = 0  # Optional operand (index, offset, count, etc.)

    def __repr__(self):
        if self.operand:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name


@dataclass
class BytecodeFunction:
    """A compiled function"""

    name: str
    arity: int
    code: List[Instruction]
    constants: List[Any]
    locals_count: int

    def disassemble(self) -> str:
        """Disassemble function to readable format"""
        lines = [
            f"Function {self.name} (arity={self.arity}, locals={self.locals_count}):"
        ]
        for i, instr in enumerate(self.code):
            lines.append(f"  {i:4d}: {instr}")
        return "\n".join(lines)


class BytecodeModule:
    """A compiled module with multiple functions"""

    def __init__(self):
        self.functions: List[BytecodeFunction] = []
        self.globals: List[str] = []  # Global variable names
        self.constants: List[Any] = []  # Module-level constants
        self.entry_point: int = 0  # Index of main function

    def add_function(self, func: BytecodeFunction) -> int:
        """Add a function and return its index"""
        idx = len(self.functions)
        self.functions.append(func)
        return idx

    def disassemble(self) -> str:
        """Disassemble entire module"""
        lines = ["=== Bytecode Module ===", ""]
        lines.append(f"Globals: {self.globals}")
        lines.append(f"Constants: {self.constants}")
        lines.append("")

        for i, func in enumerate(self.functions):
            lines.append(f"--- Function {i} ---")
            lines.append(func.disassemble())
            lines.append("")

        return "\n".join(lines)


class BytecodeBuilder:
    """Helper for building bytecode"""

    def __init__(self):
        self.code: List[Instruction] = []
        self.constants: List[Any] = []
        self.locals: Dict[str, int] = {}
        self.labels: Dict[str, int] = {}
        self.fixups: List[Tuple[int, str]] = []  # (code_index, label_name)

    def emit(self, opcode: OpCode, operand: int = 0):
        """Emit an instruction"""
        self.code.append(Instruction(opcode, operand))

    def emit_const(self, value: Any) -> int:
        """Add a constant and return its index"""
        # Check if constant already exists
        try:
            return self.constants.index(value)
        except ValueError:
            idx = len(self.constants)
            self.constants.append(value)
            return idx

    def emit_load_const(self, value: Any):
        """Emit PUSH_CONST with value"""
        idx = self.emit_const(value)
        self.emit(OpCode.PUSH_CONST, idx)

    def get_local(self, name: str) -> int:
        """Get or create local variable index"""
        if name not in self.locals:
            self.locals[name] = len(self.locals)
        return self.locals[name]

    def label(self, name: str):
        """Mark current position as label"""
        self.labels[name] = len(self.code)

    def emit_jump(self, opcode: OpCode, label: str):
        """Emit jump instruction with label (to be fixed up later)"""
        idx = len(self.code)
        self.emit(opcode, 0)  # Placeholder
        self.fixups.append((idx, label))

    def resolve_labels(self):
        """Resolve all label references"""
        for code_idx, label_name in self.fixups:
            if label_name not in self.labels:
                raise ValueError(f"Undefined label: {label_name}")
            offset = self.labels[label_name] - code_idx - 1
            self.code[code_idx].operand = offset

    def build(
        self, name: str = "main", arity: int = 0, locals_count: int = None
    ) -> BytecodeFunction:
        self.resolve_labels()
        actual_locals = locals_count if locals_count is not None else len(self.locals)
        return BytecodeFunction(
            name=name,
            arity=arity,
            code=self.code,
            constants=self.constants,
            locals_count=actual_locals,
        )
