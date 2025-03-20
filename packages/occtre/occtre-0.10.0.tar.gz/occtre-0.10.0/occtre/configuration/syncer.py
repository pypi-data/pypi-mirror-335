# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""
Class configuring the CoverageTracer Tool.
The system for processing configuration classes is described in:
https://pypi.org/project/dataclass-binder/.
"""

import tomlkit
from dataclass_binder import Binder

from .configuration import Configuration


class Syncer:
    """Class for handling sync configuration with files."""

    @staticmethod
    def load_toml(file_path: str) -> Configuration:
        """Load configuration from file."""
        with open(file_path, encoding="utf-8") as file:
            _doc = tomlkit.load(file)
        return Binder(Configuration).bind(_doc.value)

    @staticmethod
    def dump_toml(file_path: str, config: Configuration) -> None:
        """Dump configuration to file."""
        # TODO: not working currently, only dump dataclass attributes!
        with open(file_path, "w", encoding="utf-8") as file:
            tomlkit.dump(config.__dict__, file)
