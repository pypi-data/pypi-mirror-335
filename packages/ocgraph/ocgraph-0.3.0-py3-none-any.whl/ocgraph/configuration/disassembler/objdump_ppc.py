"""Class for parsing the objdump PPC input."""

from __future__ import annotations

from .disassembler import ObjdumpDisassembler


class ObjDumpPpcDisassembler(ObjdumpDisassembler):
    """Objdump PPC disassembler."""

    name: str = "PPC Objdump Disassembler (PPC Binutils)"
