# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class to create a Recorder."""

from occtre.intern.disassembly import Disassembly
from occtre.intern.logger import Logger
from occtre.intern.parser import Parser
from occtre.intern.recorder.data_coverage import DataCoverageRecorder
from occtre.intern.recorder.instruction_coverage import InstructionCoverageRecorder
from occtre.intern.recorder.recorder import Recorder, RecorderConfiguration

recorder_presets = {
    "DataCoverageRecorder": DataCoverageRecorder,
    "InstructionRecorder": InstructionCoverageRecorder,
}


class RecorderFactory:
    """RecorderFactory to instantiate a Recorder object."""

    @staticmethod
    def create(
        config: RecorderConfiguration,
        disassembly: Disassembly,
        parser: Parser,
        logger: Logger,
    ) -> Recorder:
        """Create a recorder according to the given configuration."""
        if recorder_preset := recorder_presets.get(config.name):
            return recorder_preset(
                config=config,
                disassembly=disassembly,
                parser=parser,
                logger=logger,
            )

        msg = f"Unknown recorder {config.name}"
        raise NotImplementedError(msg)
