from typing import List, Tuple, Any
import re


def run_cpu_program(initial_registers: List[int], instructions: List[str], max_steps: int = 500000) -> List[int]:
    """
    Simulates a minimalist CPU with registers, comparison flag, and various
    addressing modes (Value, Register Direct, Register Pointer).
    Executes instructions like MOV, ADD, MUL, CMP, JMP, JEQ, JGT, JLT, HALT.
    All CPU state and logic are contained within this single function.

    Args:
        initial_registers: A list of initial integer values for the CPU registers.
        instructions: A list of strings, each representing a CPU instruction.
        max_steps: The maximum number of instructions to execute before halting.

    Returns:
        The final state of the registers after program execution.
    """

    # --- CPU State (formerly class attributes) ---
    registers: List[int] = list(initial_registers)  # Make a copy to avoid modifying original
    ip: int = 0  # Instruction Pointer
    cf: int = 0  # Comparison Flag (-1 for <, 0 for ==, 1 for >)
    steps_executed: int = 0

    # Pre-compile regex outside the loop for efficiency
    operand_regex = re.compile(r'([VRP])(\d+)')

    # --- Helper functions (inlined within the main function) ---
    def _get_value(operand_str: str) -> int:
        """Decodes operand string to its integer value."""
        match = operand_regex.match(operand_str)
        if not match:
            # Handle invalid operand format, though input is assumed valid by problem
            raise ValueError(f"Invalid operand format: {operand_str}")

        mode, num_str = match.groups()
        num = int(num_str)

        if mode == 'V': return num
        if mode == 'R':
            if num < 0 or num >= len(registers):
                raise IndexError(f"Register R{num} out of bounds.")
            return registers[num]
        if mode == 'P':
            # Pointer: value at register 'num' is the index
            if num < 0 or num >= len(registers):
                raise IndexError(f"Register R{num} (for pointer) out of bounds.")
            ptr_index = registers[num]
            if ptr_index < 0 or ptr_index >= len(registers):
                raise IndexError(f"Pointer address R[{num}] -> R[{ptr_index}] out of bounds.")
            return registers[ptr_index]
        return -1  # Should not be reached given valid modes

    def _set_value(operand_str: str, value: int) -> None:
        """Sets a value at the destination specified by an operand string."""
        match = operand_regex.match(operand_str)
        if not match:
            raise ValueError(f"Invalid operand format for set: {operand_str}")

        mode, num_str = match.groups()
        num = int(num_str)

        if mode == 'R':
            if num < 0 or num >= len(registers):
                raise IndexError(f"Register R{num} out of bounds for write.")
            registers[num] = value
        elif mode == 'P':
            # Pointer: value at register 'num' is the index
            if num < 0 or num >= len(registers):
                raise IndexError(f"Register R{num} (for pointer) out of bounds for write.")
            ptr_index = registers[num]
            if ptr_index < 0 or ptr_index >= len(registers):
                raise IndexError(f"Pointer address R[{num}] -> R[{ptr_index}] out of bounds for write.")
            registers[ptr_index] = value
        # 'V' mode (Value) cannot be a destination, so no else needed.

    # --- Main CPU Execution Loop (from run method) ---
    while 0 <= ip < len(instructions) and steps_executed < max_steps:
        steps_executed += 1

        instruction = instructions[ip].strip()
        if not instruction:
            ip += 1
            continue

        parts = instruction.replace(',', ' ').split()
        opcode = parts[0]
        operands = parts[1:]
        jumped = False  # Flag to indicate if IP was modified by a jump

        if opcode == "MOV":
            _set_value(operands[0], _get_value(operands[1]))
        elif opcode == "ADD":
            _set_value(operands[0], _get_value(operands[0]) + _get_value(operands[1]))
        elif opcode == "MUL":
            _set_value(operands[0], _get_value(operands[0]) * _get_value(operands[1]))
        elif opcode == "CMP":
            val1, val2 = _get_value(operands[0]), _get_value(operands[1])
            if val1 < val2:
                cf = -1
            elif val1 > val2:
                cf = 1
            else:
                cf = 0
        elif opcode == "JMP":
            ip = _get_value(operands[0])
            jumped = True
        elif opcode == "JEQ":
            if cf == 0:
                ip = _get_value(operands[0])
                jumped = True
        elif opcode == "JGT":
            if cf == 1:
                ip = _get_value(operands[0])
                jumped = True
        elif opcode == "JLT":
            if cf == -1:
                ip = _get_value(operands[0])
                jumped = True
        elif opcode == "HALT":
            break  # Exit the loop immediately

        if not jumped:
            ip += 1  # Move to the next instruction if no jump occurred

    return registers  # Return the final state of the registers


# ====================== TEST CASES (Modified to call the single function) ======================

def test_one():
    # Simple direct register arithmetic
    registers = [5, 10, 0]
    instructions = ["ADD R2, R0", "ADD R2, R1", "HALT"]
    assert run_cpu_program(registers, instructions) == [5, 10, 15]


def test_two():
    # Using indirect (pointer) addressing
    registers = [2, 10, 5]
    instructions = ["ADD P0, R1", "HALT"]
    assert run_cpu_program(registers, instructions) == [2, 10, 15]


def test_three():
    # Loop to find max value
    registers = [1, 50, 90, 20, 0, 4]
    instructions = [
        "MOV R4, R1", "ADD R0, V1", "CMP R0, R5", "JEQ V9",
        "CMP P0, R4", "JGT V7", "JMP V1", "MOV R4, P0",
        "JMP V1", "HALT"
    ]
    final_regs = run_cpu_program(registers, instructions)
    assert final_regs[4] == 90


def test_four():
    # HALT instruction stops immediately
    registers = [0, 0, 0]
    instructions = ["HALT", "ADD R0, V100"]
    assert run_cpu_program(registers, instructions) == [0, 0, 0]


def test_five():
    # Jump out of bounds should halt
    registers = [0]
    instructions = ["JMP V100"]
    assert run_cpu_program(registers, instructions) == [0]


def test_six():
    # Infinite loop test (halts due to max_steps)
    registers = [0]
    instructions = ["JMP V0"]
    assert run_cpu_program(registers, instructions) == [0]


def test_seven():
    # Double Pointer operation
    registers_1 = [1, 2, 0]
    instructions_1 = ["MOV P0, V99"]
    assert run_cpu_program(registers_1, instructions_1) == [1, 99, 0]

    registers_2 = [1, 2, 0]  # Re-initialize registers for the second sub-test
    instructions_2 = ["MOV P1, V88"]
    assert run_cpu_program(registers_2, instructions_2) == [1, 2, 88]


def test_eight():
    # Self-modifying jump target
    registers = [5, 0]
    instructions = [
        "MOV R1, V3", "MOV R0, R1", "JMP R0",
        "ADD R1, V100", "HALT", "ADD R1, V999"
    ]
    assert run_cpu_program(registers, instructions) == [3, 103]