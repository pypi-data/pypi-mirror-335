# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the CoverageTracer Tool."""

from .recorder import Recorder


class DataCoverageRecorder(Recorder):
    """Recorder for data coverage."""

    def _print(self, msg: str, pre: str = "", post: str = "") -> None:
        """Internal log function for the check function."""
        msg = ("\n" + msg) if (msg and msg.strip()) else "None"
        self._log.info(pre + msg + post)

    def connect_tasks(self) -> None:
        self.host_task.command(
            f"target extended-remote localhost:{self.config.task_port}",
            self._log,
        )

    def initialize_target(self) -> None:
        # load file
        self.host_task.command(
            "file " + str(self.config.binary_path.absolute()),
            self._log,
        )
        # set start label
        self.host_task.command("b " + self.config.start_label, self._log)
        # load into target
        self.host_task.command("load " + str(self.config.binary_path), self._log)

        if "sis" in self.target_task.name.lower():
            # Send initialization command to simulator to prevent trap on startup
            self.host_task.command("monitor run 0", self._log)

        # start program til first breakpoint self.start_label
        self.host_task.command("c", self._log)
        self.host_task.command("info register", self._log)

    def kill_apps(self) -> None:
        """Kill all connected processes."""
        try:
            out_read, err_read = self.host_task.check()
            self._print(out_read, "## HOST STDOUT: ")
            self._print(err_read, "## HOST STDERR: ")

            out_read, err_read = self.target_task.check()
            self._print(out_read, "## TARGET STDOUT: ")
            self._print(err_read, "## TARGET STDERR: ")

            self.host_task.command("bt", self._log)
            self.host_task.command("info register", self._log)

            self.host_task.command("disconnect", self._log)
            self.host_task.command("quit", self._log)
            self.target_task.command("quit", self._log)

            out_read, err_read = self.host_task.check()
            self._print(out_read, "## HOST STDOUT: ")
            self._print(err_read, "## HOST STDERR: ")

            out_read, err_read = self.target_task.check()
            self._print(out_read, "## TARGET STDOUT: ")
            self._print(err_read, "## TARGET STDERR: ")

        except BrokenPipeError:
            pass

    def record(self) -> None:
        """Execute and disassemble the loaded binary."""
        self._log.info("Disassemble Start")

        # While running test binary:
        while True:
            # disassemble current address
            self.host_task.command("disassemble /r $pc,+1")
            out_read = self.host_task.check_out(until="dump")

            if self.config.stop_label in out_read:
                self._log.info("disassemble /r $pc,+1: " + str(out_read))
                break

            result = ""
            opcode = self._parser.get_opcode(out_read)

            if self._parser.is_memory_access(opcode):
                registers_raw = self._parser.get_registers(out_read)

                register_values = {}
                for register in registers_raw:
                    self.host_task.command("info register " + register[1:], self._log)
                    register_values[register] = self.host_task.check_out().split()[2]
                self._log.info(f"registers: {register_values}")
                result = self._disassembly.update_data(out_read, register_values)

            if not opcode or len(opcode) == 0:  # no feedback from process
                self._log.info(out_read)
                break

            self._log.info_sparse(f"disassemble /r $pc,+1:  {result}")  # log result
            self.host_task.command(self.config.command_step)  # step to next instruction
