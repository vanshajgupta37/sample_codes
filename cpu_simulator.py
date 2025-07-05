import re

class CPUSimulator:
    """
    Solves the Dynamic Pointer CPU Simulation problem.

    Problem Description:
    You are tasked with creating a simulator for a unique, minimalist CPU.
    This CPU has a set of integer registers, a single comparison flag, and
    operates on a list of string-based instructions. The defining feature of
    this CPU is its powerful and flexible addressing modes, which allow for
    direct, indirect (pointer-based), and immediate value manipulation.

    Your goal is to write a function that takes an initial state of the registers
    and a list of instructions (the "program"), simulates the execution, and
    returns the final state of the registers.

    CPU Components:
    1.  Registers: A list of integers.
    2.  Instruction Pointer (IP): Starts at 0, points to the current instruction.
    3.  Comparison Flag (CF): An integer set by the `CMP` instruction.
        -  It is -1 if operand1 < operand2.
        -  It is 0 if operand1 == operand2.
        -  It is 1 if operand1 > operand2.

    Addressing Modes (The Core Challenge):
    Operands in instructions can refer to values in three ways:
    -   `V<num>` (Value): The literal integer value. E.g., `V10` is the number 10.
        This can only be a source operand.
    -   `R<num>` (Register Direct): The value inside the specified register. E.g.,
        `R0` refers to the value at `registers[0]`.
    -   `P<num>` (Register Pointer/Indirect): The value at the address *pointed to*
        by the specified register. E.g., if `registers[1]` is `5`, then `P1` refers
        to the value at `registers[5]`.

    Instruction Set:
    -   `MOV dst, src`: Copies the value from `src` to `dst`.
    -   `ADD dst, src`: Adds the value from `src` to the value at `dst`.
    -   `MUL dst, src`: Multiplies the value at `dst` by the value from `src`.
    -   `CMP op1, op2`: Compares the values from `op1` and `op2` and sets the CF.
    -   `JMP target`: Unconditionally jumps to the instruction index specified by `target`.
    -   `JEQ target`: Jumps if the Comparison Flag is 0 (equal).
    -   `JGT target`: Jumps if the Comparison Flag is 1 (greater than).
    -   `JLT target`: Jumps if the Comparison Flag is -1 (less than).
    -   `HALT`: Stops execution immediately.

    Execution Flow:
    The simulation runs in a loop, fetching and executing instructions one by one.
    The IP increments by 1 after each instruction, unless a jump occurs. To prevent
    runaway programs, the simulation must also stop after a maximum number of
    execution steps (e.g., 500,000).
    """

    def __init__(self, registers, instructions, max_steps=500000):
        """
        Initializes the CPU state for a simulation run.

        Args:
            registers (list[int]): The initial state of the registers.
            instructions (list[str]): The program to execute.
            max_steps (int): The maximum number of instructions to execute
                to prevent infinite loops.
        """
        self.registers = list(registers)
        self.instructions = instructions
        self.max_steps = max_steps
        self.ip = 0  # Instruction Pointer
        self.cf = 0  # Comparison Flag
        self.steps_executed = 0

        # Pre-compile regex for faster parsing in the loop
        self.operand_regex = re.compile(r'([VRP])(\d+)')

    def _get_value(self, operand_str):
        """
        Decodes an operand string to get its actual value based on addressing modes.
        """
        match = self.operand_regex.match(operand_str)
        if not match:
            raise ValueError(f"Invalid operand format: {operand_str}")

        mode, num = match.groups()
        num = int(num)

        if mode == 'V':
            return num
        if mode == 'R':
            if not 0 <= num < len(self.registers):
                raise ValueError(f"Register index out of bounds: R{num}")
            return self.registers[num]
        if mode == 'P':
            if not 0 <= num < len(self.registers):
                raise ValueError(f"Register index out of bounds for pointer: P{num}")
            pointer_address = self.registers[num]
            if not 0 <= pointer_address < len(self.registers):
                raise ValueError(f"Pointer address out of bounds: P{num} -> {pointer_address}")
            return self.registers[pointer_address]

        raise ValueError("Unknown addressing mode.")

    def _set_value(self, operand_str, value):
        """
        Sets a value at a destination specified by an operand string.
        """
        match = self.operand_regex.match(operand_str)
        if not match:
            raise ValueError(f"Invalid operand format: {operand_str}")

        mode, num = match.groups()
        num = int(num)

        if mode == 'V':
            raise ValueError("Cannot set value to a literal (V-mode operand).")
        if mode == 'R':
            if not 0 <= num < len(self.registers):
                raise ValueError(f"Register index out of bounds: R{num}")
            self.registers[num] = value
        elif mode == 'P':
            if not 0 <= num < len(self.registers):
                raise ValueError(f"Register index out of bounds for pointer: P{num}")
            pointer_address = self.registers[num]
            if not 0 <= pointer_address < len(self.registers):
                raise ValueError(f"Pointer address out of bounds: P{num} -> {pointer_address}")
            self.registers[pointer_address] = value

    def run(self):
        """
        Executes the simulation loop for the loaded program.
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
                dest, src = operands
                self._set_value(dest, self._get_value(src))
            elif opcode == "ADD":
                dest, src = operands
                self._set_value(dest, self._get_value(dest) + self._get_value(src))
            elif opcode == "MUL":
                dest, src = operands
                self._set_value(dest, self._get_value(dest) * self._get_value(src))
            elif opcode == "CMP":
                op1, op2 = operands
                val1, val2 = self._get_value(op1), self._get_value(op2)
                if val1 < val2:
                    self.cf = -1
                elif val1 > val2:
                    self.cf = 1
                else:
                    self.cf = 0
            elif opcode == "JMP":
                self.ip = self._get_value(operands[0])
                jumped = True
            elif opcode == "JEQ":
                if self.cf == 0:
                    self.ip = self._get_value(operands[0])
                    jumped = True
            elif opcode == "JGT":
                if self.cf == 1:
                    self.ip = self._get_value(operands[0])
                    jumped = True
            elif opcode == "JLT":
                if self.cf == -1:
                    self.ip = self._get_value(operands[0])
                    jumped = True
            elif opcode == "HALT":
                break

            if not jumped:
                self.ip += 1

        return self.registers


def simulate_cpu(registers, instructions):
    """High-level function to run the CPU simulation."""
    simulator = CPUSimulator(registers, instructions)
    return simulator.run()


# =================
#  TESTS
# =================
def run_cpu_tests():
    # Test 1: Normal Case - Simple direct register arithmetic
    registers = [5, 10, 0]
    instructions = [
        "ADD R2, R0",  # R2 = 0 + 5 = 5
        "ADD R2, R1",  # R2 = 5 + 10 = 15
        "HALT"
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [5, 10, 15]

    # Test 2: Normal Case - Using indirect (pointer) addressing
    registers = [2, 10, 5]
    instructions = [
        "ADD P0, R1",
        "HALT"
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [2, 10, 15]

    # Test 3: Long Case - A loop to find the max value in registers R1-R3
    registers = [1, 50, 90, 20, 0, 4]
    # --- FIX IS HERE ---
    # The program logic has been corrected to avoid an infinite loop.
    instructions = [
        "MOV R4, R1",      # 0: Setup max_val = R1 (50)
        "ADD R0, V1",      # 1: (start_loop) iterator++
        "CMP R0, R5",      # 2: Compare iterator (R0) with end condition (R5=4)
        "JEQ V9",          # 3: If iterator == 4, jump to HALT
        "CMP P0, R4",      # 4: Compare R[iterator] with max_val (R4)
        "JGT V7",          # 5: If R[iterator] > max_val, jump to update max
        "JMP V1",          # 6: (continue_loop) Else, jump back to start_loop
        "MOV R4, P0",      # 7: (update_max) Update max_val
        "JMP V1",          # 8: After updating, jump back to start_loop
        "HALT"             # 9: (halt_label)
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs[4] == 90  # Max value should be 90

    # Test 4: Edge Case - HALT instruction stops immediately
    registers = [0, 0, 0]
    instructions = [
        "HALT",
        "ADD R0, V100"
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [0, 0, 0]

    # Test 5: Edge Case - Jump out of bounds should halt
    registers = [0]
    instructions = ["JMP V100"]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [0]

    # Test 6: Edge Case - Infinite loop test
    registers = [0]
    instructions = ["JMP V0"]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [0]

    # Test 7: Hard Case - Double Pointer operation
    registers = [1, 2, 0]
    instructions = [
        "MOV P0, V99" # This means registers[registers[0]] = 99 => registers[1] = 99
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [1, 99, 0]

    registers = [1, 2, 0]
    instructions = [
        "MOV P1, V88" # This means registers[registers[1]] = 88 => registers[2] = 88
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [1, 2, 88]

    # Test 8: Hard Case - Self-modifying jump target
    registers = [5, 0]
    instructions = [
        "MOV R1, V3",
        "MOV R0, R1",
        "JMP R0",       # Should jump to instruction 3
        "ADD R1, V100", # Instruction 3: This will run
        "HALT",
        "ADD R1, V999"  # Instruction 5: This should be skipped
    ]
    final_regs = simulate_cpu(registers, instructions)
    assert final_regs == [3, 103]

    print("✅ All 8 CPU Simulator tests passed!")


if __name__ == "__main__":
    run_cpu_tests()