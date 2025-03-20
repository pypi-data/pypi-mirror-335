# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""
Class configuring the CoverageTracer Tool. All module parts shall be designed to run as encapsulated
as possible. So configuration option shall also be separated.

The design of this concept is to initialize the application as follows:

1. Direct initialization: In this case, the class contains all necessary parameter, no shared
   information of the full configuration class is needed, The object is already existing in this
   full configuration class.
2. Indirect initialization: In this case the class needs a separate configuration object which
   contains all relevant information/shared objects to run.
"""

import socket
from dataclasses import dataclass, field
from pathlib import Path

from occtre.intern.logger import Logger, LoggerConfiguration
from occtre.intern.parser import ParserConfiguration
from occtre.intern.process import Process
from occtre.intern.recorder.recorder import RecorderConfiguration


@dataclass
class Configuration:
    """Test configuration."""

    host: Process = field(default_factory=Process)
    """ Process settings for GDB """

    target: Process = field(default_factory=Process)
    """ Process settings for the target """

    a2line: Process = field(default_factory=Process)
    """ Process settings for addr2line """

    recorder: RecorderConfiguration = field(default_factory=RecorderConfiguration)
    """ Process settings for the execution/recording """

    parser: ParserConfiguration = field(default_factory=ParserConfiguration)
    """ Parser of the input strings """

    log: LoggerConfiguration = field(default_factory=LoggerConfiguration)
    """Logging configuration for module"""

    logger: Logger = field(init=False)
    """Logging mechanism for module"""

    def __post_init__(self):
        """Post init function of dataclass module. Called after generated __init__."""
        self.logger = Logger(self.log)

    @staticmethod
    def _get_free_port():
        """Internal function to search for a free port."""
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def initialize(self, test_binary: str | None = None, task_port: str | None = None) -> None:
        """Initialize the module by calling after-load procedures."""
        if test_binary:
            binary_path = Path(test_binary)
            if not binary_path.exists():
                msg = f"Test binary {test_binary} not found"
                raise NotImplementedError(msg)
            self.logger.info("Update binary_path to " + test_binary)
            self.recorder.binary_path = binary_path
        elif self.recorder.binary_path:
            binary_path = self.recorder.binary_path
            if not self.recorder.binary_path.exists():
                msg = f"Test binary {self.recorder.binary_path} not found"
                raise NotImplementedError(
                    msg,
                )
        else:
            msg = f"Test binary {self.recorder.binary_path} not found."
            raise NotImplementedError(
                msg,
            )

        if task_port:
            self.logger.info("Update task_port to " + task_port)
            self.recorder.task_port = task_port

        # Configuration post-processing:
        #   - Select network port if necessary:
        if self.recorder.task_port == "" or self.recorder.task_port is None:
            self.recorder.task_port = str(self._get_free_port())

        #   - Replace placeholder in function options:
        self.host.replace_arguments("{port}", self.recorder.task_port)
        self.target.replace_arguments("{port}", self.recorder.task_port)
        self.a2line.replace_arguments("{port}", self.recorder.task_port)

        self.host.replace_arguments("{test_binary}", str(binary_path.absolute()))
        self.target.replace_arguments("{test_binary}", str(binary_path.absolute()))
        self.a2line.replace_arguments("{test_binary}", str(binary_path.absolute()))
