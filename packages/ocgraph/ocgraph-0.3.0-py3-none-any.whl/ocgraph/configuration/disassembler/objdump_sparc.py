"""Class for parsing the objdump SPARC input."""

from __future__ import annotations

from .disassembler import ObjdumpDisassembler


class ObjDumpSparcDisassembler(ObjdumpDisassembler):
    """Objdump SPARC disassembler."""

    name: str = "SPARC Objdump Disassembler (SparcV8 Binutils)"
