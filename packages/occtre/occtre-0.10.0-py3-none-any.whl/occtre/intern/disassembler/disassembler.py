# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the used disassembler tool."""

from abc import ABC, abstractmethod
from typing import Any

from occtre.intern.address_hit import AddressHit


class DisassemblerError(Exception):
    """Raised when the extract_information method was not successful."""


class Disassembler(ABC):
    """Disassembler Class."""

    def __init__(self) -> None:
        pass

    name: str = ""
    """ Disassembler tool identification like OBJDump, GDB, ..."""

    @abstractmethod
    def extract_information(self, str_input: str) -> dict[str, str]:
        """
        Specification of the extracted information. Required attributes are:
        * address = instruction location in the binary
        * location: instruction address location
        * instr_d: instruction in disassembled format
        * instr_h: instruction in hex-notation
        * opcode: instruction opcode
        * op_options: operation options
        * printable: a printable line of the collected information.
        """
        raise NotImplementedError

    @abstractmethod
    def get_registers(self, str_input: str, single: bool = True) -> list[str]:
        """Returns the opcode relevant address registers of a disassembly."""
        raise NotImplementedError

    @abstractmethod
    def get_opcode(self, str_input: str) -> str | bool:
        """Returns the opcode of a disassembled line."""
        raise NotImplementedError

    @abstractmethod
    def get_address_hit(self, str_input: str) -> tuple[AddressHit, str]:
        """Returns the opcode of a disassembled line."""
        raise NotImplementedError

    @abstractmethod
    def decode_instructions(self, instr_str: str, register_values: dict[str, Any]):
        raise NotImplementedError
