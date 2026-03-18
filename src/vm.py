"""
AICode v2.0 Virtual Machine
Stack-based VM for bytecode execution
"""

from typing import List, Any, Dict, Optional
from dataclasses import dataclass, field
from src.bytecode import OpCode, BytecodeFunction, BytecodeModule, Instruction
from src.stdlib_ai import BUILTINS
from src.errors import (
    RuntimeError as AICodeRuntimeError,
    division_by_zero,
    index_out_of_bounds,
    key_not_found,
    undefined_function,
    stack_overflow,
    stack_underflow,
    E106,
    E404,
    E406,
    E407,
    E408,
    E410,
    E411,
    E412,
    E413,
    E418,
    E419,
)


class VMError(AICodeRuntimeError):
    """VM runtime error"""

    pass


@dataclass
class CallFrame:
    """A call frame for function calls"""

    function: BytecodeFunction
    ip: int = 0  # Instruction pointer
    locals: List[Any] = field(default_factory=list)

    def read_instruction(self) -> Instruction:
        """Read next instruction"""
        if self.ip >= len(self.function.code):
            raise VMError(E106, "Unexpected end of code")
        instr = self.function.code[self.ip]
        self.ip += 1
        return instr


class BytecodeFunctionWrapper:
    """Wrapper to make BytecodeFunction callable from Python"""

    def __init__(self, func: BytecodeFunction, vm: "VirtualMachine"):
        self.func = func
        self.vm = vm

    def __call__(self, *args):
        """Execute the bytecode function with given arguments"""
        # Create a new frame for the function call
        new_frame = CallFrame(self.func)
        new_frame.locals = list(args) + [None] * (self.func.locals_count - len(args))
        self.vm.frames.append(new_frame)

        # Execute until the frame returns
        while len(self.vm.frames) > 1:  # Keep going until we return to main
            try:
                self.vm._execute_instruction()
            except StopIteration:
                break

        # Return the result from the stack
        if self.vm.stack:
            return self.vm.pop()
        return None


class VirtualMachine:
    """Stack-based virtual machine"""

    def __init__(self):
        self.stack: List[Any] = []
        self.frames: List[CallFrame] = []
        self.globals: Dict[str, Any] = {}
        self.module: Optional[BytecodeModule] = None

        # Setup built-in functions
        self._setup_builtins()

    def _setup_builtins(self):
        """Setup built-in functions"""
        # Register all functions from stdlib_ai
        self.globals.update(BUILTINS)

    def push(self, value: Any):
        """Push value onto stack"""
        self.stack.append(value)

    def pop(self) -> Any:
        """Pop value from stack"""
        if not self.stack:
            raise stack_underflow()
        return self.stack.pop()

    def peek(self, offset: int = 0) -> Any:
        """Peek at stack without popping"""
        if len(self.stack) <= offset:
            raise stack_underflow()
        return self.stack[-(offset + 1)]

    def current_frame(self) -> CallFrame:
        """Get current call frame"""
        if not self.frames:
            raise RuntimeError(E419, "No call frame")
        return self.frames[-1]

    def run(self, module: BytecodeModule):
        """Run a bytecode module"""
        self.module = module

        # Initialize globals
        for name in module.globals:
            if name not in self.globals:
                self.globals[name] = None

        # Store function references in globals for user-defined functions and lambdas
        # First, create a mapping of function names to their indices
        func_indices = {}
        for i, func in enumerate(module.functions):
            if func.name != "__main__":
                func_indices[func.name] = i

        # Now store functions in globals by matching names
        for i, func in enumerate(module.functions):
            if func.name != "__main__":
                if func.name in self.globals:
                    self.globals[func.name] = func

        # Handle lambdas specially - match __lambda_X__ globals to <lambda> functions
        lambda_count = 0
        for global_name in module.globals:
            if global_name.startswith("__lambda_"):
                # Find the corresponding lambda function
                for func in module.functions:
                    if func.name == "<lambda>":
                        self.globals[global_name] = func
                        break

        # Register user-defined functions by name
        for func in module.functions:
            if func.name != "__main__":
                self.globals[func.name] = func

        # Start with entry point
        entry_func = module.functions[module.entry_point]
        frame = CallFrame(entry_func)
        frame.locals = [None] * entry_func.locals_count
        self.frames.append(frame)

        while self.frames:
            try:
                self._execute_instruction()
            except StopIteration:
                break

    def _execute_instruction(self):
        """Execute single instruction"""
        frame = self.current_frame()
        instr = frame.read_instruction()

        opcode = instr.opcode
        operand = instr.operand

        if opcode == OpCode.PUSH_CONST:
            self.push(frame.function.constants[operand])

        elif opcode == OpCode.PUSH_NULL:
            self.push(None)

        elif opcode == OpCode.POP:
            self.pop()

        elif opcode == OpCode.DUP:
            self.push(self.peek())

        elif opcode == OpCode.SWAP:
            a = self.pop()
            b = self.pop()
            self.push(a)
            self.push(b)

        elif opcode == OpCode.LOAD_LOCAL:
            frame = self.current_frame()
            self.push(frame.locals[operand])

        elif opcode == OpCode.STORE_LOCAL:
            frame = self.current_frame()
            value = self.pop()
            # Extend locals if needed
            while len(frame.locals) <= operand:
                frame.locals.append(None)
            frame.locals[operand] = value

        elif opcode == OpCode.LOAD_GLOBAL:
            if self.module is None:
                raise RuntimeError(E413, "No module loaded")
            name = self.module.globals[operand] if isinstance(operand, int) else operand
            if name in self.globals:
                self.push(self.globals[name])
            else:
                raise undefined_function(name)

        elif opcode == OpCode.STORE_GLOBAL:
            if self.module is None:
                raise RuntimeError(E413, "No module loaded")
            name = self.module.globals[operand] if isinstance(operand, int) else operand
            value = self.pop()
            self.globals[name] = value

        elif opcode == OpCode.ADD:
            b = self.pop()
            a = self.pop()
            self.push(a + b)

        elif opcode == OpCode.SUB:
            b = self.pop()
            a = self.pop()
            self.push(a - b)

        elif opcode == OpCode.MUL:
            b = self.pop()
            a = self.pop()
            self.push(a * b)

        elif opcode == OpCode.DIV:
            b = self.pop()
            a = self.pop()
            self.push(a / b)

        elif opcode == OpCode.MOD:
            b = self.pop()
            a = self.pop()
            self.push(a % b)

        elif opcode == OpCode.NEG:
            a = self.pop()
            self.push(-a)

        elif opcode == OpCode.EQ:
            b = self.pop()
            a = self.pop()
            self.push(a == b)

        elif opcode == OpCode.NE:
            b = self.pop()
            a = self.pop()
            self.push(a != b)

        elif opcode == OpCode.LT:
            b = self.pop()
            a = self.pop()
            self.push(a < b)

        elif opcode == OpCode.GT:
            b = self.pop()
            a = self.pop()
            self.push(a > b)

        elif opcode == OpCode.LE:
            b = self.pop()
            a = self.pop()
            self.push(a <= b)

        elif opcode == OpCode.GE:
            b = self.pop()
            a = self.pop()
            self.push(a >= b)

        elif opcode == OpCode.NOT:
            a = self.pop()
            self.push(not a)

        elif opcode == OpCode.AND:
            b = self.pop()
            a = self.pop()
            self.push(a and b)

        elif opcode == OpCode.OR:
            b = self.pop()
            a = self.pop()
            self.push(a or b)

        elif opcode == OpCode.JUMP:
            frame = self.current_frame()
            frame.ip += operand

        elif opcode == OpCode.JUMP_IF_FALSE:
            frame = self.current_frame()
            condition = self.pop()
            if not condition:
                frame.ip += operand

        elif opcode == OpCode.JUMP_IF_TRUE:
            frame = self.current_frame()
            condition = self.pop()
            if condition:
                frame.ip += operand

        elif opcode == OpCode.CALL:
            argc = operand
            # Stack: func was pushed first, then args
            # Pop args in reverse order (last arg first), then func
            args = [self.pop() for _ in range(argc)]
            args.reverse()
            func = self.pop()

            # Resolve integer index to BytecodeFunction (user-defined functions stored by index)
            if isinstance(func, int) and self.module is not None:
                func = self.module.functions[func]

            if callable(func):
                # Built-in or Python function
                # Wrap any BytecodeFunction arguments so they're callable
                wrapped_args = []
                for arg in args:
                    if isinstance(arg, BytecodeFunction):
                        wrapped_args.append(BytecodeFunctionWrapper(arg, self))
                    else:
                        wrapped_args.append(arg)
                result = func(*wrapped_args)
                self.push(result)
            elif isinstance(func, BytecodeFunction):
                # AICode function — push frame; result is pushed when RETURN_VALUE executes
                new_frame = CallFrame(func)
                extra = max(0, func.locals_count - len(args))
                new_frame.locals = list(args) + [None] * extra
                self.frames.append(new_frame)
            else:
                raise RuntimeError(E410, f"Cannot call {type(func)}")

        elif opcode == OpCode.RETURN:
            self.frames.pop()

        elif opcode == OpCode.RETURN_VALUE:
            result = self.pop()
            self.frames.pop()
            if self.frames:
                self.push(result)

        elif opcode == OpCode.BUILD_LIST:
            count = operand
            elements = [self.pop() for _ in range(count)]
            elements.reverse()
            self.push(elements)

        elif opcode == OpCode.BUILD_DICT:
            count = operand
            items = {}
            for _ in range(count):
                value = self.pop()
                key = self.pop()
                items[key] = value
            self.push(items)

        elif opcode == OpCode.INDEX_GET:
            index = self.pop()
            obj = self.pop()
            if isinstance(obj, list):
                self.push(obj[index])
            elif isinstance(obj, dict):
                self.push(obj[index])
            else:
                raise RuntimeError(E408, f"Cannot index {type(obj)}")

        elif opcode == OpCode.GET_ATTR:
            obj = self.pop()
            attr = frame.function.constants[operand]
            if isinstance(obj, dict):
                self.push(obj.get(attr))
            else:
                self.push(getattr(obj, attr, None))

        elif opcode == OpCode.INDEX_SET:
            value = self.pop()
            index = self.pop()
            obj = self.pop()
            if isinstance(obj, (list, dict)):
                obj[index] = value
            else:
                raise VMError(f"Cannot index-assign {type(obj)}")

        elif opcode == OpCode.SET_ATTR:
            value = self.pop()
            obj = self.pop()
            attr = frame.function.constants[operand]
            if isinstance(obj, dict):
                obj[attr] = value
            else:
                setattr(obj, attr, value)

        elif opcode == OpCode.ITER:
            obj = self.pop()
            if isinstance(obj, list):
                self.push(iter(obj))
            elif isinstance(obj, dict):
                self.push(iter(obj.items()))
            elif isinstance(obj, str):
                self.push(iter(obj))
            elif hasattr(obj, "__iter__"):
                self.push(iter(obj))
            else:
                raise RuntimeError(E408, f"Cannot iterate over {type(obj)}")

        elif opcode == OpCode.ITER_NEXT:
            # Peek the iterator from the stack (don't pop - it stays for next iteration)
            iterator = self.peek()
            try:
                value = next(iterator)
                # Push the value
                if isinstance(value, tuple) and len(value) == 2:
                    # Dictionary items come as (key, value) pairs
                    self.push(value[0])
                    self.push(value[1])
                else:
                    self.push(value)
                # Success - don't jump
            except StopIteration:
                # No more items - jump to end (iterator will be popped by bytecode's POP)
                frame = self.current_frame()
                frame.ip += operand

        elif opcode == OpCode.PRINT:
            value = self.pop()
            print(value, end="")

        elif opcode == OpCode.PRINTLN:
            value = self.pop()
            print(value)

        elif opcode == OpCode.NOP:
            pass

        elif opcode == OpCode.HALT:
            raise StopIteration()

        else:
            raise RuntimeError(E418, f"Unknown opcode: {opcode}")
