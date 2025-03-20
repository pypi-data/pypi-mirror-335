# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the used disassembler tool."""

import re
from typing import Any

from occtre.intern.address_hit import AddressHit

from .disassembler import Disassembler, DisassemblerError


class SparcV8GccObjdump(Disassembler):
    """GCC Objdump SPARC v8 disassembler."""

    name: str = "GCC Objdump SPARC v8"

    # Expected format: <hex address> <<label+offset>>: <opcode> <interpreted opcode>
    regex: str = r"(\S+)( <(\S+)>|):\s+([\S ]+)\s([\S  ]+)"
    regex_information: dict[str, int] = {
        "address": 1,
        "location": 3,
        "instruction_hex": 4,
        "instruction_str": 5,
    }

    def extract_information(self, str_input: str) -> dict[str, str]:
        result = {}

        if "=> " in str_input:
            extracted_line = str_input.split("=> ", 1)[1].split("\n", 1)[0]

            information = re.search(self.regex, extracted_line)
            if not information:
                raise DisassemblerError(
                    "Line not processable: \n" + str(extracted_line),
                )

            address = str(information.group(self.regex_information.get("address")))
            location = str(information.group(self.regex_information.get("location")))
            instr_d = str(
                information.group(self.regex_information.get("instruction_str")),
            )
            instr_h = str(
                information.group(self.regex_information.get("instruction_hex")),
            )
            opcode = instr_d.split()[0]

            result = {
                "address": address,
                "location": location,
                "instr_h": instr_h,
                "instr_d": instr_d,
                "opcode": opcode,
                "printable": extracted_line,
            }
        else:
            raise DisassemblerError("Line not processable: \n" + str(str_input))

        return result

    def get_registers(self, str_input: str, single: bool = True) -> list[str]:
        """Returns the opcode relevant address registers of a disassembly."""
        information = self.extract_information(str_input)
        instr_str = information.get("instr_d")
        if single:
            instr_str = instr_str.split("]")[0].split("[")[-1]
        return re.findall(r"%\w+", instr_str)

    def get_opcode(self, str_input: str) -> str | bool:
        """Returns the opcode of a disassembled line."""
        try:
            information = self.extract_information(str_input)
        except DisassemblerError:
            return False

        return information.get("opcode")

    def get_address_hit(self, str_input: str) -> tuple[AddressHit, str]:
        """Returns an AddressHit of the disassembled line."""
        try:
            information = self.extract_information(str_input)
        except DisassemblerError:
            return None, ""

        address = information.get("address")
        location = information.get("location")
        instr_d = information.get("instr_d")
        instr_h = information.get("instr_h")
        opcode = information.get("opcode")
        printable = information.get("printable")

        return AddressHit(address, location, instr_h, instr_d, opcode), printable

    def decode_instructions(self, instr_str: str, register_values: dict[str, Any]):
        instruction_decoded = ""
        if register_values is not None:
            address = instr_str.split("]")[0].split("[")[-1]
            for register in register_values:
                address = address.replace(register, register_values[register])
            instruction_decoded = (
                instr_str.split("[")[0] + str(hex(eval(address))) + instr_str.split("]")[1]
            )
        return instruction_decoded
