# SPDX-License-Identifier: GTDGmbH
"""Module for configuration of the ocgraph package."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .architecture import (
    ArmArchitecture,
    MSP430Architecture,
    PpcArchitecture,
    SparcArchitecture,
    X86Architecture,
)
from .disassembler import (
    GdbDisassembler,
    ObjDumpArmDisassembler,
    ObjDumpMsp430Disassembler,
    ObjDumpPpcDisassembler,
    ObjDumpSparcDisassembler,
    ObjDumpx86Disassembler,
)
from .logger import OCGraphLogger, preset_logging

if TYPE_CHECKING:  # pragma: no cover
    from .architecture import Architecture
    from .disassembler import Disassembler

# fmt: off
disassembler_option: dict[str, dict[str, Disassembler]] = {
    "OBJDUMP": {
        "sparc": ObjDumpSparcDisassembler(),
        "ppc": ObjDumpPpcDisassembler(),
        "x86": ObjDumpx86Disassembler(),
        "arm": ObjDumpArmDisassembler(),
        "msp430": ObjDumpMsp430Disassembler(),
    },
    "GDB": {
        "sparc": GdbDisassembler(),
        "ppc": GdbDisassembler(),
        "x86": GdbDisassembler(),
        "arm": GdbDisassembler(),
        "msp430": GdbDisassembler(),
    },
}

architecture_option: dict[str, dict[str, str | Architecture | Disassembler]] = {
    "x86": {
        "platform": "X86",
        "architecture": X86Architecture(),
    },
    "arm": {
        "platform": "ARM",
        "architecture": ArmArchitecture(),
    },
    "sparc": {
        "platform": "SPARC",
        "architecture": SparcArchitecture(),
    },
    "ppc": {
        "platform": "PPC",
        "architecture": PpcArchitecture(),
    },
    "msp430": {
        "platform": "MSP430",
        "architecture": MSP430Architecture(),
    },
}
# fmt: on


class OcGraphConfiguration:
    """Implement configuration presets for the ASM2CFG tool."""

    def __init__(
        self,
        arch: str = "sparc",
        disassembler: str = "OBJDUMP",
        logging_preset: str = "default",
    ) -> None:
        if architecture_option.get(arch) is None:
            msg = "Architecture option not supported!"
            raise NotImplementedError(msg)
        if disassembler_option.get(disassembler) is None:
            msg = "Disassembler option not supported!"
            raise NotImplementedError(msg)
        if preset_logging.get(logging_preset) is None:
            msg = "Logging preset not supported!"
            raise NotImplementedError(msg)

        # load module preset
        _preset = architecture_option[arch]
        _preset["disassembler"] = disassembler_option[disassembler][arch]
        self.__dict__ = _preset

        # configure logging
        self.logger = OCGraphLogger("OcGraph", logging_preset, "ocgraph")

    @staticmethod
    def architectures() -> list[str]:
        """Return all available architectures options."""
        return list(architecture_option.keys())

    @staticmethod
    def disassemblers() -> list[str]:
        """Return all available disassemblers options."""
        return list(disassembler_option.keys())

    @staticmethod
    def loggers() -> list[str]:
        """Return all available disassemblers options."""
        return list(preset_logging.keys())

    logger: logging.Logger = logging.getLogger("OcGraph")
    """Logging mechanism for module"""

    architecture: Architecture
    """Target architecture instance"""

    disassembler: Disassembler
    """Target disassembler tool like OBJDump, GDB, ..."""
