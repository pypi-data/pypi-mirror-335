# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Data structure class for storing/exporting collected information."""


class AddressHit:
    """Store an executed instruction on a binary address."""

    address: str
    """Instruction binary address"""
    location: str
    """Instruction Label + Offset"""
    instruction_hex: str
    """Instruction in hex-format"""
    instruction_str: str
    """Instruction decoded """
    instruction_opcode: str
    """Instruction opcode decoded"""
    instruction_decoded: str
    """Instruction options with decoded registers"""
    count: int = 1
    """Count of instruction execution"""
    source_code: str = ""
    """Calculated source file location"""
    branch_jumps: set[str]
    """Target addresses after the conditional branch"""

    headers = {
        "address": "Address",
        "location": "Label(+off)",
        "instruction_hex": "Instruction (hex)",
        "instruction_opcode": "Opcode",
        "instruction_decoded": "Instruction decoded",
        "instruction_str": "Instruction",
        "count": "Executed",
        "source_code": "Code File",
        "branch_jumps": "Branch taken",
    }

    def __init__(
        self,
        address: str,
        location: str,
        instr_hex: str,
        instr_str: str,
        opcode: str,
    ) -> None:
        self.address = address
        self.location = location
        self.instruction_hex = instr_hex
        self.instruction_str = instr_str
        self.instruction_opcode = opcode
        self.count = 1
        self.branch_jumps = set()
