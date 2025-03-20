# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Interface for using the CoverageTracer Tool."""

from typing import TYPE_CHECKING

from occtre.configuration.configuration import Configuration
from occtre.intern.address2line import Address2Line
from occtre.intern.address_hit import AddressHit
from occtre.intern.disassembly import Disassembly
from occtre.intern.parser import Parser
from occtre.intern.recorder.recorder_factory import RecorderFactory
from occtre.intern.table_exporter import TableExporter

if TYPE_CHECKING:
    from occtre.intern.recorder.recorder import Recorder


class CoverageTracer:
    """CoverageTracer class."""

    def __init__(self, config: Configuration) -> None:
        """Initialize a CoverageTracer using a Configuration."""
        self.config: Configuration = config
        self._log = config.logger

        self._parser = Parser(config.parser)
        self.disassembly: Disassembly = Disassembly(self._parser, logger=config.logger)
        self.recorder: Recorder = RecorderFactory.create(
            config=self.config.recorder,
            disassembly=self.disassembly,
            parser=self._parser,
            logger=self._log,
        )
        self.recorder.init_tasks(
            target_task=config.target,
            host_task=config.host,
        )

        self.addr2line = Address2Line(config.a2line, self._log)

    def run(self) -> None:
        """Run the complete coverage tracer using the given configuration."""
        self._start_tasks()
        self.check_task_each()

        self.recorder.connect_tasks()
        self.check_task_each()

        self.recorder.initialize_target()
        self.check_task_each()

        self.recorder.record()
        self.check_task_each()

        self.addr2line.update_disassembly(self.disassembly)

        _values = [vars(v) for v in self.disassembly.address_hits.values()]
        TableExporter.export_to_file(
            _values,
            AddressHit.headers,
            str(self.config.recorder.binary_path) + ".csv",
        )
        TableExporter.export_to_file(
            _values,
            AddressHit.headers,
            str(self.config.recorder.binary_path) + ".md",
        )

    def _start_tasks(self) -> None:
        self.recorder.start_tasks()
        self.addr2line.start_tasks()

    def check_task_each(self) -> None:
        """Call check_task for each task."""

        def _print(msg: str, pre: str = "", post: str = "") -> None:
            """Intern log function for the check function."""
            msg = ("\n" + msg) if (msg and msg.strip()) else "None"
            self._log.info(pre + msg + post)

        out_read, err_read = self.recorder.get_target_streams()
        _print(out_read, "## TARGET STDOUT: ")
        _print(out_read, "## TARGET STDERR: ")

        out_read, err_read = self.recorder.get_host_streams()
        _print(out_read, "## HOST STDOUT: ")
        _print(out_read, "## HOST STDERR: ")

        out_read, err_read = self.addr2line.get_streams()
        _print(out_read, "## A2LINE STDOUT: ")
        _print(out_read, "## A2LINE STDERR: ")

    def kill_processes(self) -> None:
        self.recorder.kill_apps()
        self.config.a2line.kill()
