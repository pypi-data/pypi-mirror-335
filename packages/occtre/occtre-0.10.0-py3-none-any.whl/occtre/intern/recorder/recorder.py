# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the CoverageTracer Tool."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from occtre.intern.disassembly import Disassembly
from occtre.intern.logger import Logger
from occtre.intern.parser import Parser
from occtre.intern.process import Process

recorder_presets = {
    "DataCoverageRecorder",
    "InstructionRecorder",
}


@dataclass
class RecorderConfiguration:
    """Configuration for the recording."""

    name: str = "InstructionRecorder"
    """Name of the recorder, for allowed entries check recorder_presets."""

    binary_path: Path = Path("a.out")
    """Path to the binary"""

    task_port: str = "1234"
    """Communication port of the tasks"""

    start_label: str = ""
    """ Assembler label for the start logging of the coverage """

    stop_label: str = ""
    """ Assembler label for stop logging the coverage """

    jumps: bool = False
    """ Enable jump logging """

    command_step: str = "stepi"
    """ Enable jump logging """

    def __post_init__(self):
        if self.name not in recorder_presets:
            raise NotImplementedError("Unknown Recorder: " + self.name)


class Recorder(ABC):
    """Recorder class, doing the recording work."""

    config: RecorderConfiguration
    """Configuration for the recorder"""

    target_task: Process = Process()
    """Task running communication to the target (Monitor, Simulator, Script ...)"""
    host_task: Process = Process()
    """Task running the communication on the host (GDB, other debugger, etc. pp) """

    def __init__(
        self,
        config: RecorderConfiguration,
        disassembly: Disassembly,
        parser: Parser,
        logger: Logger,
    ) -> None:
        super().__init__()
        self.config = config
        self._disassembly: Disassembly = disassembly
        self._parser: Parser = parser
        self._log: Logger = logger

    def init_tasks(self, target_task: Process, host_task: Process) -> None:
        """Setting the task before recording."""
        self.target_task: Process = target_task
        self.host_task: Process = host_task

    def start_tasks(self) -> None:
        """Start the task before recording."""
        self.target_task.run(self._log)
        self.host_task.run(self._log)

    def get_target_streams(self) -> tuple[str, str]:
        """Get (OUT, ERR) stream of the target task."""
        return self.target_task.check()

    def get_host_streams(self) -> tuple[str, str]:
        """Get (OUT, ERR) stream of the host task."""
        return self.host_task.check()

    @abstractmethod
    def connect_tasks(self):
        raise NotImplementedError

    @abstractmethod
    def initialize_target(self):
        raise NotImplementedError

    @abstractmethod
    def kill_apps(self):
        """Kill all connected processes."""
        raise NotImplementedError

    @abstractmethod
    def record(self):
        """Execute and disassemble the loaded binary."""
        raise NotImplementedError
