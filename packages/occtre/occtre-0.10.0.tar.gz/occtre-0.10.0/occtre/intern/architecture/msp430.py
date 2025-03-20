# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the sparc v8 architecture."""

from .architecture import Architecture

# fmt: off
# Source: https://www.ti.com/sc/data/msp/databook/chp8.pdf

_Msp430ProgramFlowControl = [
    # 8.4.1.2 Single Operand Instructions
    "CALL", "RETI",

    # 8.4.1.3 Conditional Jumps
    "JC",   # Jump if Carry = 1
    "JHS",  # Jump if dst is higher or same than src (C = 1)
    "JEQ",  # Jump if dst equals src (Z = 1)
    "JZ",   # Jump if Zero Bit = 1
    "JGE",  # Jump if dst is greater than or equal to src (N .xor. V = 0)
    "JLT",  # Jump if dst is less than src (N .xor. V = 1)
    "JMP",  # Jump unconditionally
    "JN",   # Jump if Negative Bit = 1
    "JNC",  # Jump if Carry = 0
    "JLO",  # Jump if dst is lower than src (C = 0)
    "JNE",  # Jump if dst is not equal to src (Z = 0)
    "JNZ",  # Jump if Zero Bit = 0

    # 8.4.2 Emulated Instructions
    "BR", "RET",
]

_Msp430DataInstructions = [
    # TODO: Add load instructions
    # TODO: Add store instructions
    #   Isse: Access is done immediately, see 8.2.2 Addressing Modes
]
# fmt: on


class Msp430Architecture(Architecture):
    """Sparc V8 Architecture."""

    name: str = "Msp430"

    def is_jump(self, opcode: str = "") -> bool:
        return opcode in _Msp430ProgramFlowControl

    def get_delay(self, opcode: str = "") -> int:
        return 0

    def is_memory_access(self, opcode: str = "") -> bool:
        return opcode in _Msp430DataInstructions
