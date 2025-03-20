# SPDX-License-Identifier: GTDGmbH
# Copyright 2024 by GTD GmbH.
"""Contains instruction info for X86-compatible targets."""

from .architecture import Architecture


class X86Architecture(Architecture):
    """X86Architecture Class."""

    def is_jump(self, opcode: str = "") -> bool:
        return opcode.startswith(("j", "ret")) or "call" in opcode
