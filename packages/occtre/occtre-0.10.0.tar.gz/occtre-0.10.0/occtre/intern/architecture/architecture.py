# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the target architecture."""

from abc import ABC


class Architecture(ABC):
    """Architecture Class."""

    def __init__(self) -> None:
        pass

    name: str = ""
    """ Architecture Name """

    # Program control-flow methods
    def is_jump(self, opcode: str = "") -> bool:
        """Return if opcode is a (potential) jump to a non-step address."""
        raise NotImplementedError

    def get_delay(
        self,
        opcode: str = "",
    ) -> int | None:  # pylint: disable=unused-argument
        """
        Return the delay of a jump instruction.
        The default delay is 0 except for special SPARC instructions.
        """
        return 0

    # IO control methods
    def is_memory_access(self, opcode: str = "") -> bool:
        """Return if opcode is a memory access."""
        raise NotImplementedError
