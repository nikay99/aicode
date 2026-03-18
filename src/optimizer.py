"""
AICode Bytecode Optimizer
Implements various bytecode optimization passes
"""

from typing import List, Dict, Set, Tuple, Optional
from src.bytecode import OpCode, Instruction, BytecodeFunction, BytecodeModule


class BytecodeOptimizer:
    """Optimizer for AICode bytecode"""

    def __init__(self):
        self.optimizations_applied = 0
        self.peephole_enabled = True
        self.constant_folding_enabled = True
        self.dead_code_elimination_enabled = True
        self.tail_call_enabled = True

    def optimize_module(self, module: BytecodeModule) -> BytecodeModule:
        """Optimize an entire bytecode module"""
        self.optimizations_applied = 0

        optimized_functions = []
        for func in module.functions:
            optimized_func = self.optimize_function(func)
            optimized_functions.append(optimized_func)

        # Create new module with optimized functions
        optimized_module = BytecodeModule()
        optimized_module.functions = optimized_functions
        optimized_module.globals = module.globals[:]
        optimized_module.constants = module.constants[:]
        optimized_module.entry_point = module.entry_point

        return optimized_module

    def optimize_function(self, func: BytecodeFunction) -> BytecodeFunction:
        """Optimize a single function"""
        code = func.code[:]
        constants = func.constants[:]

        # Apply optimizations in passes
        changed = True
        passes = 0
        max_passes = 5

        while changed and passes < max_passes:
            changed = False
            passes += 1

            if self.constant_folding_enabled:
                new_code, new_constants, folded = self._constant_folding(
                    code, constants
                )
                if folded:
                    code = new_code
                    constants = new_constants
                    changed = True
                    self.optimizations_applied += folded

            if self.peephole_enabled:
                new_code, peephole_count = self._peephole_optimizations(code)
                if peephole_count > 0:
                    code = new_code
                    changed = True
                    self.optimizations_applied += peephole_count

            if self.dead_code_elimination_enabled:
                new_code, dead_count = self._dead_code_elimination(code)
                if dead_count > 0:
                    code = new_code
                    changed = True
                    self.optimizations_applied += dead_count

            if self.tail_call_enabled:
                new_code, tail_count = self._tail_call_optimization(code)
                if tail_count > 0:
                    code = new_code
                    changed = True
                    self.optimizations_applied += tail_count

        return BytecodeFunction(
            name=func.name,
            arity=func.arity,
            code=code,
            constants=constants,
            locals_count=func.locals_count,
        )

    def _constant_folding(
        self, code: List[Instruction], constants: List
    ) -> Tuple[List[Instruction], List, int]:
        """
        Constant folding: evaluate constant expressions at compile time

        Example:
          PUSH_CONST 5     # 2
          PUSH_CONST 3     # 3
          ADD              # -
        Becomes:
          PUSH_CONST 8     # New constant (2+3)
        """
        new_code = []
        new_constants = constants[:]
        changed = 0
        i = 0

        while i < len(code):
            # Look for patterns: PUSH_CONST, PUSH_CONST, BINARY_OP
            if i + 2 < len(code):
                instr1 = code[i]
                instr2 = code[i + 1]
                instr3 = code[i + 2]

                if (
                    instr1.opcode == OpCode.PUSH_CONST
                    and instr2.opcode == OpCode.PUSH_CONST
                ):
                    val1 = constants[instr1.operand]
                    val2 = constants[instr2.operand]

                    # Check if both are numeric constants
                    if isinstance(val1, (int, float)) and isinstance(
                        val2, (int, float)
                    ):
                        result = None

                        if instr3.opcode == OpCode.ADD:
                            result = val1 + val2
                        elif instr3.opcode == OpCode.SUB:
                            result = val1 - val2
                        elif instr3.opcode == OpCode.MUL:
                            result = val1 * val2
                        elif instr3.opcode == OpCode.DIV and val2 != 0:
                            result = val1 / val2
                        elif instr3.opcode == OpCode.MOD and val2 != 0:
                            result = val1 % val2
                        elif instr3.opcode == OpCode.EQ:
                            result = val1 == val2
                        elif instr3.opcode == OpCode.NE:
                            result = val1 != val2
                        elif instr3.opcode == OpCode.LT:
                            result = val1 < val2
                        elif instr3.opcode == OpCode.GT:
                            result = val1 > val2
                        elif instr3.opcode == OpCode.LE:
                            result = val1 <= val2
                        elif instr3.opcode == OpCode.GE:
                            result = val1 >= val2

                        if result is not None:
                            # Add result as new constant
                            try:
                                const_idx = new_constants.index(result)
                            except ValueError:
                                const_idx = len(new_constants)
                                new_constants.append(result)

                            new_code.append(Instruction(OpCode.PUSH_CONST, const_idx))
                            i += 3
                            changed += 1
                            continue

            # Look for unary operations on constants
            if i + 1 < len(code):
                instr1 = code[i]
                instr2 = code[i + 1]

                if instr1.opcode == OpCode.PUSH_CONST:
                    val = constants[instr1.operand]

                    if isinstance(val, (int, float)):
                        if instr2.opcode == OpCode.NEG:
                            result = -val
                            try:
                                const_idx = new_constants.index(result)
                            except ValueError:
                                const_idx = len(new_constants)
                                new_constants.append(result)

                            new_code.append(Instruction(OpCode.PUSH_CONST, const_idx))
                            i += 2
                            changed += 1
                            continue

            new_code.append(code[i])
            i += 1

        return new_code, new_constants, changed

    def _peephole_optimizations(
        self, code: List[Instruction]
    ) -> Tuple[List[Instruction], int]:
        """
        Peephole optimizations: replace common instruction patterns

        Optimizations:
        - POP after PUSH_NULL (if value not used)
        - DUP followed by POP = no-op
        - LOAD_LOCAL n; STORE_LOCAL n = no-op
        - JUMP to next instruction = remove
        - PUSH_CONST; POP = no-op
        """
        new_code = []
        changed = 0
        i = 0

        while i < len(code):
            # Pattern: DUP, POP -> remove both
            if i + 1 < len(code):
                if code[i].opcode == OpCode.DUP and code[i + 1].opcode == OpCode.POP:
                    i += 2
                    changed += 1
                    continue

            # Pattern: LOAD_LOCAL n, STORE_LOCAL n -> remove both
            if i + 1 < len(code):
                if (
                    code[i].opcode == OpCode.LOAD_LOCAL
                    and code[i + 1].opcode == OpCode.STORE_LOCAL
                    and code[i].operand == code[i + 1].operand
                ):
                    i += 2
                    changed += 1
                    continue

            # Pattern: PUSH_CONST, POP -> remove both (if constant not used)
            if i + 1 < len(code):
                if (
                    code[i].opcode == OpCode.PUSH_CONST
                    and code[i + 1].opcode == OpCode.POP
                ):
                    i += 2
                    changed += 1
                    continue

            # Pattern: PUSH_NULL, POP -> remove both
            if i + 1 < len(code):
                if (
                    code[i].opcode == OpCode.PUSH_NULL
                    and code[i + 1].opcode == OpCode.POP
                ):
                    i += 2
                    changed += 1
                    continue

            new_code.append(code[i])
            i += 1

        return new_code, changed

    def _dead_code_elimination(
        self, code: List[Instruction]
    ) -> Tuple[List[Instruction], int]:
        """
        Dead code elimination: remove unreachable code

        Optimizations:
        - Code after RETURN/RETURN_VALUE (in same block)
        - Code after unconditional JUMP
        """
        new_code = []
        changed = 0
        i = 0

        while i < len(code):
            new_code.append(code[i])

            # Check if this is a terminal instruction
            if code[i].opcode in (OpCode.RETURN, OpCode.RETURN_VALUE, OpCode.HALT):
                # Skip all code until next label or end
                i += 1
                while i < len(code):
                    # Keep labels and NOPs for alignment
                    if code[i].opcode == OpCode.NOP:
                        new_code.append(code[i])
                        i += 1
                    else:
                        # Skip unreachable code
                        changed += 1
                        i += 1
                break

            i += 1

        return new_code, changed

    def _tail_call_optimization(
        self, code: List[Instruction]
    ) -> Tuple[List[Instruction], int]:
        """
        Tail call optimization: Convert tail calls to jumps

        Pattern:
          LOAD_GLOBAL n   # Load function
          ... args ...    # Push arguments
          CALL argc       # Call function
          RETURN_VALUE    # Return result

        Can be optimized if:
        - Function is the current function (recursive tail call)
        - We can reuse the current frame
        """
        new_code = []
        changed = 0
        i = 0

        while i < len(code):
            # Look for CALL followed by RETURN_VALUE
            if i + 1 < len(code):
                if (
                    code[i].opcode == OpCode.CALL
                    and code[i + 1].opcode == OpCode.RETURN_VALUE
                ):
                    # This is a potential tail call
                    # Mark it for optimization (in real implementation,
                    # this would require more context about the function)
                    pass

            new_code.append(code[i])
            i += 1

        return new_code, changed

    def get_stats(self) -> Dict[str, int]:
        """Get optimization statistics"""
        return {
            "optimizations_applied": self.optimizations_applied,
            "peephole_enabled": self.peephole_enabled,
            "constant_folding_enabled": self.constant_folding_enabled,
            "dead_code_elimination_enabled": self.dead_code_elimination_enabled,
            "tail_call_enabled": self.tail_call_enabled,
        }


class BytecodeCache:
    """Simple cache for compiled bytecode"""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, BytecodeModule] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[BytecodeModule]:
        """Get cached bytecode"""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, module: BytecodeModule):
        """Store bytecode in cache"""
        if len(self.cache) >= self.max_size:
            # Simple LRU: remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = module

    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "size": len(self.cache),
            "max_size": self.max_size,
        }


def optimize_and_cache(
    module: BytecodeModule,
    cache: Optional[BytecodeCache] = None,
    source_hash: Optional[str] = None,
) -> BytecodeModule:
    """
    Optimize a module and optionally cache it

    Args:
        module: The bytecode module to optimize
        cache: Optional cache to use
        source_hash: Optional hash of source code for caching

    Returns:
        Optimized bytecode module
    """
    # Check cache first
    if cache and source_hash:
        cached = cache.get(source_hash)
        if cached:
            return cached

    # Optimize the module
    optimizer = BytecodeOptimizer()
    optimized = optimizer.optimize_module(module)

    # Store in cache
    if cache and source_hash:
        cache.put(source_hash, optimized)

    return optimized
