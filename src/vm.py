"""
AICode v2.0 Virtual Machine
Stack-based VM for bytecode execution
"""

from typing import List, Any, Dict, Optional
from dataclasses import dataclass, field
from src.bytecode import OpCode, BytecodeFunction, BytecodeModule, Instruction


class VMError(Exception):
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
            raise VMError("Unexpected end of code")
        instr = self.function.code[self.ip]
        self.ip += 1
        return instr


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
        self.globals["print"] = self._builtin_print
        self.globals["println"] = self._builtin_println
        self.globals["range"] = self._builtin_range
        self.globals["map"] = self._builtin_map
        self.globals["filter"] = self._builtin_filter
        self.globals["reduce"] = self._builtin_reduce
        self.globals["length"] = len
        self.globals["str"] = str
        self.globals["int"] = int
        self.globals["float"] = float
        self.globals["keys"] = lambda d: list(d.keys()) if isinstance(d, dict) else []
        self.globals["values"] = lambda d: (
            list(d.values()) if isinstance(d, dict) else []
        )
        # Result type builtins
        self.globals["Ok"] = lambda v: ("Ok", v)
        self.globals["Err"] = lambda v: ("Err", v)
        self.globals["is_ok"] = lambda r: isinstance(r, tuple) and r[0] == "Ok"
        self.globals["is_err"] = lambda r: isinstance(r, tuple) and r[0] == "Err"
        self.globals["unwrap"] = self._builtin_unwrap
        self.globals["unwrap_or"] = lambda r, default: (
            r[1] if (isinstance(r, tuple) and r[0] == "Ok") else default
        )

    def _builtin_unwrap(self, result: Any) -> Any:
        """Unwrap a Result type, raising on Err"""
        if isinstance(result, tuple) and result[0] == "Ok":
            return result[1]
        if isinstance(result, tuple) and result[0] == "Err":
            raise VMError(f"Unwrap on Err: {result[1]}")
        raise VMError(f"Unwrap on non-Result: {result}")

    def _builtin_print(self, *args):
        """Built-in print function"""
        print(*args, end="")

    def _builtin_println(self, *args):
        """Built-in println function"""
        print(*args)

    def _builtin_range(self, *args):
        """Built-in range function"""
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        raise VMError("range() takes 1-3 arguments")

    def _call_func(self, func: Any, args: List[Any]) -> Any:
        """Call any function (built-in or BytecodeFunction) and return result"""
        if callable(func):
            return func(*args)
        elif isinstance(func, BytecodeFunction):
            # Execute in the VM synchronously
            new_frame = CallFrame(func)
            extra = max(0, func.locals_count - len(args))
            new_frame.locals = list(args) + [None] * extra
            self.frames.append(new_frame)
            # Run until this frame returns
            stack_depth = len(self.frames) - 1
            while len(self.frames) > stack_depth:
                self._execute_instruction()
            # Result was pushed onto stack by RETURN_VALUE
            return self.pop()
        raise VMError(f"Cannot call {type(func)}")

    def _builtin_map(self, lst, func):
        """Built-in map function: map(lst, fn)"""
        return [self._call_func(func, [item]) for item in lst]

    def _builtin_filter(self, lst, func):
        """Built-in filter function: filter(lst, fn)"""
        return [item for item in lst if self._call_func(func, [item])]

    def _builtin_reduce(self, lst, func, initial):
        """Built-in reduce function: reduce(lst, fn, initial)"""
        result = initial
        for item in lst:
            result = self._call_func(func, [result, item])
        return result

    def push(self, value: Any):
        """Push value onto stack"""
        self.stack.append(value)

    def pop(self) -> Any:
        """Pop value from stack"""
        if not self.stack:
            raise VMError("Stack underflow")
        return self.stack.pop()

    def peek(self, offset: int = 0) -> Any:
        """Peek at stack without popping"""
        if len(self.stack) <= offset:
            raise VMError("Stack underflow")
        return self.stack[-(offset + 1)]

    def current_frame(self) -> CallFrame:
        """Get current call frame"""
        if not self.frames:
            raise VMError("No call frame")
        return self.frames[-1]

    def run(self, module: BytecodeModule):
        """Run a bytecode module"""
        self.module = module

        # Initialize globals
        for name in module.globals:
            if name not in self.globals:
                self.globals[name] = None

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
                raise VMError("No module loaded")
            name = self.module.globals[operand] if isinstance(operand, int) else operand
            if name in self.globals:
                self.push(self.globals[name])
            else:
                raise VMError(f"Undefined global: {name}")

        elif opcode == OpCode.STORE_GLOBAL:
            if self.module is None:
                raise VMError("No module loaded")
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
            # Stack: func was pushed first, then args — pop args then func
            args = [self.pop() for _ in range(argc)]
            args.reverse()
            func = self.pop()

            # Resolve integer index to BytecodeFunction (user-defined functions stored by index)
            if isinstance(func, int) and self.module is not None:
                func = self.module.functions[func]

            if callable(func):
                # Built-in or Python function
                result = func(*args)
                self.push(result)
            elif isinstance(func, BytecodeFunction):
                # AICode function — push frame; result is pushed when RETURN_VALUE executes
                new_frame = CallFrame(func)
                extra = max(0, func.locals_count - len(args))
                new_frame.locals = list(args) + [None] * extra
                self.frames.append(new_frame)
            else:
                raise VMError(f"Cannot call {type(func)}")

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
                raise VMError(f"Cannot index {type(obj)}")

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
            self.push(iter(obj))

        elif opcode == OpCode.ITER_NEXT:
            iterator = self.peek()
            try:
                value = next(iterator)
                self.push(value)
            except StopIteration:
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
            raise VMError(f"Unknown opcode: {opcode}")
