# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class for hiding all the Parser."""

from dataclasses import dataclass
from typing import Any

from occtre.intern.architecture.architecture import Architecture
from occtre.intern.architecture.arm import ArmArchitecture
from occtre.intern.architecture.ppc import PpcArchitecture
from occtre.intern.architecture.sparc_v8 import SparcV8Architecture
from occtre.intern.architecture.x86 import X86Architecture
from occtre.intern.disassembler.disassembler import Disassembler
from occtre.intern.disassembler.sparc_v8 import SparcV8GccObjdump

from .address_hit import AddressHit

disassembler_presets = {
    "sparc_v8": SparcV8GccObjdump,
}

architecture_presets = {
    "sparc_v8": SparcV8Architecture,
    "arm": ArmArchitecture,
    "PowerPC": PpcArchitecture,
    "x86": X86Architecture,
}


@dataclass
class ParserConfiguration:
    """Class for configure a parser."""

    disassembler: str | None = None
    """ Name of the disassembler program """

    architecture: str | None = None
    """ Name of the architecture """

    def __post_init__(self):
        if self.disassembler not in disassembler_presets:
            raise NotImplementedError("Unknown Disassembler: " + str(self.disassembler))
        if self.architecture not in architecture_presets:
            raise NotImplementedError("Unknown Architecture: " + str(self.architecture))


class Parser:
    """Class for parsing inputs."""

    _disassembler: Disassembler
    """ Internal disassembler object """

    _architecture: Architecture
    """ Internal architecture object """

    def __init__(self, config: ParserConfiguration) -> None:
        """Dataclass post init function. Called after generated init procedure."""
        super().__init__()

        if config.disassembler:
            if disassembler_preset := disassembler_presets.get(
                config.disassembler,
                None,
            ):
                self._disassembler = disassembler_preset()
            else:
                msg = f"Unknown Disassembler {config.disassembler}"
                raise NotImplementedError(msg)
        else:
            msg = "No Disassembler configured"
            raise NotImplementedError(msg)

        if config.architecture:
            if architecture_preset := architecture_presets.get(
                config.architecture,
                None,
            ):
                self._architecture = architecture_preset()
            else:
                msg = f"Unknown Architecture {config.architecture}"
                raise NotImplementedError(msg)
        else:
            msg = "No Architecture configured"
            raise NotImplementedError(msg)

    # Disassembler methods
    def extract_information(self, str_input: str) -> dict[str, str]:
        """Redirect to internal disassembler function."""
        return self._disassembler.extract_information(str_input=str_input)

    def get_registers(self, str_input: str, single: bool = True) -> list[str]:
        """Returns the opcode relevant address registers of a disassembly."""
        return self._disassembler.get_registers(str_input=str_input, single=single)

    def get_opcode(self, str_input: str) -> str | bool:
        """Returns the opcode of a disassembled line."""
        return self._disassembler.get_opcode(str_input=str_input)

    def get_address_hit(self, str_input: str) -> tuple[AddressHit, str]:
        """Returns the opcode of a disassembled line."""
        return self._disassembler.get_address_hit(str_input=str_input)

    def decode_instructions(self, instr_str: str, register_values: dict[str, Any]):
        return self._disassembler.decode_instructions(
            instr_str=instr_str,
            register_values=register_values,
        )

    # Architecture methods
    def is_jump(self, opcode: str = "") -> bool:
        """Redirect to internal architecture function."""
        return self._architecture.is_jump(opcode=opcode)

    def get_delay(self, opcode: str = "") -> int | None:
        """Redirect to internal architecture function."""
        return self._architecture.get_delay(opcode=opcode)

    def is_memory_access(self, opcode: str = "") -> bool:
        """Redirect to internal architecture function."""
        return self._architecture.is_memory_access(opcode=opcode)
