# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Data structure class for storing/exporting collected information."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .logger import Logger
from .parser import Parser

if TYPE_CHECKING:
    from .address_hit import AddressHit


@dataclass
class Disassembly:
    """Disassembly of the binary."""

    def __init__(self, parser: Parser, logger: Logger) -> None:
        """Initialize the disassembly."""
        self.parser = parser
        self.logger = logger

        self.address_hits: dict[str, AddressHit] = {}

        # Store additional branch targets
        self.start_counter = 0
        self.start_address = None

    def update_data(
        self,
        disassembly: str,
        register_values: dict[str, Any] | None = None,
    ) -> str:
        """Update Data coverage entries."""
        hit: AddressHit
        hit, printable = self.parser.get_address_hit(disassembly)
        if not hit:
            self.logger.warning("Line not readable: " + disassembly)
            return ""

        if register_values:
            hit.instruction_decoded = self.parser.decode_instructions(
                hit.instruction_str,
                register_values,
            )

        # Store current address instruction
        if not self.address_hits.get(hit.address):
            self.address_hits[hit.address] = hit
        else:
            self.address_hits[hit.address].count += 1
            # Create a new entry with the different register values and store it again
            pseudo_address = hit.address + " " + str(self.address_hits[hit.address].count)
            hit.address = pseudo_address
            self.address_hits[hit.address] = hit
        return printable

    def update_instruction(self, disassembly: str, jumps: bool = False) -> str:
        """
        Extract information in the disassembled line, returns a printable
        representation of the result.
        """
        hit: AddressHit
        hit, printable = self.parser.get_address_hit(disassembly)
        if not hit:
            self.logger.warning("Line not readable: " + disassembly)
            return ""

        if not self.address_hits.get(hit.address):
            self.address_hits[hit.address] = hit
        else:
            self.address_hits[hit.address].count += 1

        if jumps:
            # Check if a jump is ongoing to log the target jumped address
            if self.start_address:
                self.start_counter -= 1
                if self.start_counter < 0:
                    self.address_hits.get(self.start_address).branch_jumps.add(
                        hit.address,
                    )
                    self.start_address = None

            # Check if current branch is branch instruction
            if self.parser.is_jump(hit.instruction_opcode):
                if self.start_address:  # check if branch is already ongoing -> log result
                    self.address_hits.get(self.start_address).branch_jumps.add(
                        hit.address,
                    )
                    self.start_address = None
                self.start_address = hit.address
                self.start_counter = self.parser.get_delay(hit.instruction_opcode)
        return printable
