from typing import List, Tuple
import re

class CPUSimulator:
    """
    Simulates a minimalist CPU with registers, comparison flag, and various
    addressing modes (Value, Register Direct, Register Pointer).
    Executes instructions like MOV, ADD, MUL, CMP, JMP, JEQ, JGT, JLT, HALT.
    Instruction Set:
    - `MOV dst, src`: Copies the value from `src` to `dst`.
    - `ADD dst, src`: Adds the value from `src` to the value at `dst`.
    - `MUL dst, src`: Multiplies the value at `dst` by the value from `src`.
    - `CMP op1, op2`: Compares the values from `op1` and `op2` and sets the CF.
    - `JMP target`: Unconditionally jumps to the instruction index specified by `target`.
    - `JEQ target`: Jumps if the Comparison Flag is 0 (equal).
    - `JGT target`: Jumps if the Comparison Flag is 1 (greater than).
    - `JLT target`: Jumps if the Comparison Flag is -1 (less than).
    - `HALT`: Stops execution immediately.
    """

    def __init__(self, registers: List[int], instructions: List[str], max_steps: int = 500000):
        """Initializes CPU state."""
        self.registers = list(registers)
        self.instructions = instructions
        self.max_steps = max_steps
        self.ip = 0
        self.cf = 0
        self.steps_executed = 0
        self.operand_regex = re.compile(r'([VRP])(\d+)')

    def _get_value(self, operand_str: str) -> int:
        """Decodes operand string to its integer value."""
        match = self.operand_regex.match(operand_str)
        mode, num = match.groups()
        num = int(num)

        if mode == 'V': return num
        if mode == 'R': return self.registers[num]
        if mode == 'P': return self.registers[self.registers[num]]
        return -1 # Should not be reached

    def _set_value(self, operand_str: str, value: int) -> None:
        """Sets a value at the destination specified by an operand string."""
        match = self.operand_regex.match(operand_str)
        mode, num = match.groups()
        num = int(num)

        if mode == 'R': self.registers[num] = value
        elif mode == 'P': self.registers[self.registers[num]] = value

    def run(self) -> List[int]:
        """
        Executes the loaded program and returns the final register state.
        Stops on HALT or max_steps exceeded.
        """
        while 0 <= self.ip < len(self.instructions) and self.steps_executed < self.max_steps:
            self.steps_executed += 1
            instruction = self.instructions[self.ip].strip()
            if not instruction:
                self.ip += 1
                continue

            parts = instruction.replace(',', ' ').split()
            opcode = parts[0]
            operands = parts[1:]
            jumped = False

            if opcode == "MOV":
                self._set_value(operands[0], self._get_value(operands[1]))
            elif opcode == "ADD":
                self._set_value(operands[0], self._get_value(operands[0]) + self._get_value(operands[1]))
            elif opcode == "MUL":
                self._set_value(operands[0], self._get_value(operands[0]) * self._get_value(operands[1]))
            elif opcode == "CMP":
                val1, val2 = self._get_value(operands[0]), self._get_value(operands[1])
                self.cf = -1 if val1 < val2 else (1 if val1 > val2 else 0)
            elif opcode == "JMP":
                self.ip = self._get_value(operands[0])
                jumped = True
            elif opcode == "JEQ":
                if self.cf == 0: self.ip = self._get_value(operands[0]); jumped = True
            elif opcode == "JGT":
                if self.cf == 1: self.ip = self._get_value(operands[0]); jumped = True
            elif opcode == "JLT":
                if self.cf == -1: self.ip = self._get_value(operands[0]); jumped = True
            elif opcode == "HALT":
                break

            if not jumped:
                self.ip += 1
        return self.registers

# ====================== TEST CASES ======================

def test_one():
    # Simple direct register arithmetic
    registers = [5, 10, 0]
    instructions = ["ADD R2, R0", "ADD R2, R1", "HALT"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [5, 10, 15]

def test_two():
    # Using indirect (pointer) addressing
    registers = [2, 10, 5]
    instructions = ["ADD P0, R1", "HALT"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [2, 10, 15]

def test_three():
    # Loop to find max value
    registers = [1, 50, 90, 20, 0, 4]
    instructions = [
        "MOV R4, R1", "ADD R0, V1", "CMP R0, R5", "JEQ V9",
        "CMP P0, R4", "JGT V7", "JMP V1", "MOV R4, P0",
        "JMP V1", "HALT"
    ]
    simulator = CPUSimulator(registers, instructions)
    final_regs = simulator.run()
    assert final_regs[4] == 90

def test_four():
    # HALT instruction stops immediately
    registers = [0, 0, 0]
    instructions = ["HALT", "ADD R0, V100"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [0, 0, 0]

def test_five():
    # Jump out of bounds should halt
    registers = [0]
    instructions = ["JMP V100"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [0]

def test_six():
    # Infinite loop test (halts due to max_steps)
    registers = [0]
    instructions = ["JMP V0"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [0]

def test_seven():
    # Double Pointer operation
    registers = [1, 2, 0]
    instructions = ["MOV P0, V99"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [1, 99, 0]

    registers = [1, 2, 0]
    instructions = ["MOV P1, V88"]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [1, 2, 88]

def test_eight():
    # Self-modifying jump target
    registers = [5, 0]
    instructions = [
        "MOV R1, V3", "MOV R0, R1", "JMP R0",
        "ADD R1, V100", "HALT", "ADD R1, V999"
    ]
    simulator = CPUSimulator(registers, instructions)
    assert simulator.run() == [3, 103]
