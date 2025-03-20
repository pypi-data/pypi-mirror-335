# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Internal interface class for commanding/interacting with created tasks."""

import logging
import queue
import subprocess
import sys
from dataclasses import dataclass, field
from subprocess import PIPE, Popen
from threading import Thread

ON_POSIX = "posix" in sys.builtin_module_names


@dataclass
class Process:
    """Class for convenient task access and manipulation."""

    """Configuration for a process"""
    name: str = ""
    """ Name of the process """

    cmd: list[str] = field(default_factory=list)
    """ Execution target start command """

    opt: list[str] = field(default_factory=list)
    """ Execution target additional start options """

    # Internal, not-initialized attributes
    proc: subprocess.Popen = field(init=False)
    """ Subprocess object of this Task """
    queue_out: queue.Queue = field(init=False)
    """ Queue of the proces output stream text """
    queue_err: queue.Queue = field(init=False)
    """ Queue of the process error stream text """
    thread_out: Thread = field(init=False)
    """ Thread for collecting the output stream """
    thread_err: Thread = field(init=False)
    """ Thread for collecting the error stream """

    def replace_arguments(self, pattern: str, replacement: str) -> None:
        """Replace argument which are post-defined."""
        self.opt = [x.replace(pattern, replacement) for x in self.opt]

    def run(self, logger: logging.Logger | None = None) -> None:
        """Initialize task with given command and register out queue."""
        _cmd = self.cmd + self.opt

        if logger:
            logger.info(f"{self.name}: Start with command: {_cmd!s}")

        self.proc = Popen(
            _cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=ON_POSIX,
        )

        self.queue_out = queue.Queue()
        self.thread_out = Thread(target=self._read_output)
        self.thread_out.daemon = True  # thread dies with the program
        self.thread_out.start()

        self.queue_err = queue.Queue()
        self.thread_err = Thread(target=self._read_error)
        self.thread_err.daemon = True  # thread dies with the program
        self.thread_err.start()

    def _read_output(self) -> None:
        """Internal function for read the command line output."""
        if self.proc.stdout:
            for read_line in iter(self.proc.stdout.readline, b""):
                self.queue_out.put(read_line)
            self.proc.stdout.close()

    def _read_error(self) -> None:
        """Internal function for read the error line output."""
        if self.proc.stderr:
            for read_line in iter(self.proc.stderr.readline, b""):
                self.queue_err.put(read_line)
            self.proc.stderr.close()

    def send(self, txt) -> None:
        """Send byte encoded string to task input."""
        if self.proc.stdin:
            self.proc.stdin.write(txt)
            self.proc.stdin.flush()

    def read(
        self,
        err: bool = False,
        until: str | None = None,
        num_expected_lines: int = -1,
    ) -> str:
        """Read content of the task connected output queue."""
        content = ""
        lines_read = 0
        timeout = 1
        block = True
        while True:
            if until is None and num_expected_lines >= 0 and lines_read >= num_expected_lines:  # pylint: disable=chained-comparison
                timeout = 0
                block = False
            try:
                if err:
                    read_line = self.queue_err.get(block=block, timeout=timeout).decode(
                        "utf-8",
                    )
                else:
                    read_line = self.queue_out.get(block=block, timeout=timeout).decode(
                        "utf-8",
                    )
                lines_read += 1
                content += read_line
                if until is not None and until in read_line:
                    break
            except queue.Empty:
                break
        return content

    def kill(self) -> None:
        """Send kill signal to the connected task."""
        self.proc.kill()

    def check(self, until=None, num_expected_lines=-1) -> tuple[str, str]:
        """Convenience function for easy checking the current task queues."""
        out_read = self.read(until=until, num_expected_lines=num_expected_lines)
        err_read = self.read(err=True, num_expected_lines=0)

        return out_read, err_read

    def check_out(self, until=None, num_expected_lines=-1) -> str:
        """Convenience function for easy checking the current stdout task queue."""
        return self.read(until=until, num_expected_lines=num_expected_lines)

    def command(self, command: str, logger: logging.Logger | None = None) -> None:
        """Convenience function for easy sending string commands to stdin of a process."""
        command_bytes = bytes(command + "\n", "utf-8")
        self.send(command_bytes)

        if logger:
            logger.info(f"## {self.name}: {command}")
