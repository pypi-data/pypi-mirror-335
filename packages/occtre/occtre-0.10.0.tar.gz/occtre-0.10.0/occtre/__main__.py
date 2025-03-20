# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Module file for calling on command line."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from .configuration.syncer import Syncer
from .interface.coverage_tracer import CoverageTracer

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .configuration.configuration import Configuration


def parse_args(args: Sequence[str] | None = None) -> argparse.ArgumentParser.parse_args:
    """Separate argument parser for testing purposes."""
    parser = argparse.ArgumentParser(description="Program to run the coverage tracer.")

    parser.add_argument(
        "-b",
        "--binary",
        help="Test binary path",
        default="a.out",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--port",
        help="Task Port",
        default="",
        required=False,
    )

    parser.add_argument(
        "-c",
        "--config",
        default="./config.toml",
        help="Path to configuration file",
    )

    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> None:
    """Command-line entry point to the program."""
    args = parse_args(args)

    # Create configuration
    config: Configuration = Syncer.load_toml(args.config)
    config.initialize(test_binary=args.binary, task_port=args.port)

    # Create CoverageTracer and execute a run
    tracer = CoverageTracer(config=config)
    tracer.run()
