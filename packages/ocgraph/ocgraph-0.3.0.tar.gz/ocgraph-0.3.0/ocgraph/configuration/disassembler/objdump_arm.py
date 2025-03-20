"""Class for parsing the objdump ARM input."""

from __future__ import annotations

from .disassembler import ObjdumpDisassembler


class ObjDumpArmDisassembler(ObjdumpDisassembler):
    """Objdump ARM disassembler."""

    name: str = "ARM Objdump Disassembler"
