# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the CoverageTracer Tool."""

from occtre.intern.disassembly import Disassembly
from occtre.intern.logger import Logger
from occtre.intern.process import Process


class Address2Line:
    """Recorder class, doing the recording work."""

    def __init__(self, address2line_task: Process, logger: Logger) -> None:
        self.a2l_task: Process = address2line_task
        self.log: Logger = logger

    def start_tasks(self) -> None:
        """Start the task before query the task."""
        self.a2l_task.run(self.log)

    def get_streams(self) -> tuple[str, str]:
        """Setting the task before recording."""
        return self.a2l_task.check()

    def update_disassembly(self, disassembly: Disassembly) -> None:
        """Update the disassembly using A2L task."""
        self.log.info("Update Address2Line of instructions.")

        # Record the covered addresses and coverage data
        for k in iter(sorted(disassembly.address_hits.keys())):
            self.a2l_task.command(k)
            out_read = self.a2l_task.check_out(num_expected_lines=1)
            disassembly.address_hits[k].source_code = out_read.strip()
            self.log.info("addr2line[" + k + "]: " + out_read.strip())

    def kill_process(self) -> None:
        self.a2l_task.kill()
