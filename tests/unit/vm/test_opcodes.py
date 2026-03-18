"""
VM Opcodes Extended Tests - Comprehensive opcode coverage
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bytecode import OpCode, Instruction, BytecodeFunction, BytecodeModule
from src.vm import VirtualMachine, VMError


class TestStackOperations(unittest.TestCase):
    """Test stack manipulation opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_push_const(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [42])

    def test_push_null(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_NULL),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[],
                )
            ],
            constants=[],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [None])

    def test_pop(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.POP),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [])

    def test_dup(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.DUP),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [42, 42])

    def test_swap(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.SWAP),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[1, 2],
                )
            ],
            constants=[1, 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [2, 1])


class TestArithmeticOperations(unittest.TestCase):
    """Test arithmetic opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_add(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.ADD),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[10, 5],
                )
            ],
            constants=[10, 5],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [15])

    def test_sub(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.SUB),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[10, 3],
                )
            ],
            constants=[10, 3],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [7])

    def test_mul(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.MUL),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[6, 7],
                )
            ],
            constants=[6, 7],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [42])

    def test_div(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.DIV),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[10, 2],
                )
            ],
            constants=[10, 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [5.0])

    def test_mod(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.MOD),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[17, 5],
                )
            ],
            constants=[17, 5],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [2])

    def test_neg(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.NEG),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [-42])


class TestComparisonOperations(unittest.TestCase):
    """Test comparison opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_eq_true(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.EQ),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [True])

    def test_eq_false(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.EQ),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[1, 2],
                )
            ],
            constants=[1, 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [False])

    def test_lt(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.LT),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[1, 2],
                )
            ],
            constants=[1, 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [True])

    def test_gt(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.GT),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[2, 1],
                )
            ],
            constants=[2, 1],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [True])


class TestLogicalOperations(unittest.TestCase):
    """Test logical opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_not_true(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.NOT),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[True],
                )
            ],
            constants=[True],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [False])

    def test_not_false(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.NOT),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[False],
                )
            ],
            constants=[False],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [True])


class TestVariableOperations(unittest.TestCase):
    """Test variable opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_store_load_local(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.STORE_LOCAL, 0),
                        Instruction(OpCode.LOAD_LOCAL, 0),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=1,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [42])

    def test_store_load_global(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.STORE_GLOBAL, 0),
                        Instruction(OpCode.LOAD_GLOBAL, 0),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=["x"],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.globals["x"], 42)
        self.assertEqual(self.vm.stack, [42])


class TestJumpOperations(unittest.TestCase):
    """Test jump opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_jump(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.JUMP, 3),
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[1, 2],
                )
            ],
            constants=[1, 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [2])

    def test_jump_if_false_true(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),  # True
                        Instruction(OpCode.JUMP_IF_FALSE, 4),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[True, 42],
                )
            ],
            constants=[True, 42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [42])

    def test_jump_if_false_false(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),  # False
                        Instruction(OpCode.JUMP_IF_FALSE, 3),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[False, 42],
                )
            ],
            constants=[False, 42],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [])


class TestCollectionOperations(unittest.TestCase):
    """Test collection opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_build_list(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.PUSH_CONST, 2),
                        Instruction(OpCode.BUILD_LIST, 3),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[1, 2, 3],
                )
            ],
            constants=[1, 2, 3],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [[1, 2, 3]])

    def test_build_dict(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.PUSH_CONST, 2),
                        Instruction(OpCode.PUSH_CONST, 3),
                        Instruction(OpCode.BUILD_DICT, 2),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=["a", 1, "b", 2],
                )
            ],
            constants=["a", 1, "b", 2],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [{"a": 1, "b": 2}])

    def test_index_get(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PUSH_CONST, 1),
                        Instruction(OpCode.PUSH_CONST, 2),
                        Instruction(OpCode.BUILD_LIST, 3),
                        Instruction(OpCode.PUSH_CONST, 3),
                        Instruction(OpCode.INDEX_GET),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[10, 20, 30, 1],
                )
            ],
            constants=[10, 20, 30, 1],
            globals=[],
        )
        self.vm.run(module)
        self.assertEqual(self.vm.stack, [20])


class TestReturnOperations(unittest.TestCase):
    """Test return opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_return_value(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.RETURN_VALUE),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                )
            ],
            constants=[42],
            globals=[],
        )
        result = self.vm.run(module)
        self.assertEqual(result, 42)


class TestCallOperations(unittest.TestCase):
    """Test function call opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_simple_call(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.CALL, 1, 0),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[],
                ),
                BytecodeFunction(
                    name="helper",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.RETURN_VALUE),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=[42],
                ),
            ],
            constants=[42],
            globals=[],
        )
        result = self.vm.run(module)
        self.assertEqual(result, 42)


class TestPrintOperations(unittest.TestCase):
    """Test print opcodes"""

    def setUp(self):
        self.vm = VirtualMachine()

    def test_print(self):
        module = BytecodeModule(
            functions=[
                BytecodeFunction(
                    name="main",
                    code=[
                        Instruction(OpCode.PUSH_CONST, 0),
                        Instruction(OpCode.PRINT),
                        Instruction(OpCode.HALT),
                    ],
                    locals_count=0,
                    arity=0,
                    constants=["hello"],
                )
            ],
            constants=["hello"],
            globals=[],
        )
        self.vm.run(module)


if __name__ == "__main__":
    unittest.main()
