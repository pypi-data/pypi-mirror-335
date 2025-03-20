# SPDX-License-Identifier: GTDGmbH
# Copyright 2024 by GTD GmbH.
"""Class configuring the logging."""

import logging
import time
from dataclasses import dataclass

# fmt: off
logging_preset: dict[str, dict] = {
    "development": {
        "file_log": True,
        "file_level": logging.DEBUG,
        "console_log": True,
        "console_level": logging.DEBUG,
        "filter_Sparse": False,
    },

    "module": {
        "file_log": False,
        "file_level": logging.ERROR,
        "console_log": False,
        "console_level": logging.ERROR,
        "filter_Sparse": True,
    },

    "default": {
        "file_log": True,
        "file_level": logging.INFO,
        "console_log": True,
        "console_level": logging.INFO,
        "filter_Sparse": True,
    },
}
# fmt: on


class FilterSparse(logging.Filter):
    """Filter for sparse log messages."""

    _frequency: int = 1
    _last_print: float = 0.0

    def filter(self, record) -> bool:
        if record.__dict__.get("Sparse"):
            _now = time.time()
            if self._last_print and _now < self._last_print + (1 / self._frequency):
                return False
            self._last_print = _now
        return True


@dataclass
class LoggerConfiguration:
    """Logging mechanism for module."""

    preset: str = "default"
    """ Name of the preset """

    file: str = "./occtre.log"
    """Logging file"""


class Logger(logging.Logger):
    """BaseLogger class for prevent bad dataclass interferor."""

    def __init__(self, config: LoggerConfiguration) -> None:
        super().__init__("OcctreLogger")
        if config.preset and logging_preset.get(config.preset, None):
            self.config = logging_preset[config.preset]
        else:
            self.config = logging_preset["default"]

        if self.config["file_log"]:
            logging_file = config.file + (".log" if not config.file.endswith(".log") else "")
            file_stream: logging.FileHandler = logging.FileHandler(logging_file)
            file_stream.setLevel(self.config["file_level"])
            self.addHandler(file_stream)

        if self.config["console_log"]:
            console_stream: logging.StreamHandler = logging.StreamHandler()
            console_stream.setLevel(self.config["console_level"])
            self.addHandler(console_stream)

        if self.config["filter_Sparse"]:
            self.addFilter(FilterSparse())

    def makeRecord(self, *args, **kwargs) -> logging.LogRecord:
        rv = super().makeRecord(*args, **kwargs)
        rv.__dict__["Sparse"] = rv.__dict__.get("Sparse", False)
        return rv

    def info_sparse(self, msg) -> None:
        self.log(
            logging.INFO,
            msg,
            extra={"Sparse": self.config.get("filter_Sparse", False)},
        )
