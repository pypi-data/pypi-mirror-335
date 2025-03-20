# SPDX-License-Identifier: GTDGmbH
# Copyright 2024 by GTD GmbH.
"""Contains instruction info for ARM-compatible targets."""

from .architecture import Architecture


class ArmArchitecture(Architecture):
    """ArmArchitecture Class."""

    def is_jump(self, opcode: str = "") -> bool:
        return opcode.startswith("b")
