"""Class for parsing the objdump x86 input."""

from __future__ import annotations

from .disassembler import ObjdumpDisassembler


class ObjDumpx86Disassembler(ObjdumpDisassembler):
    """x86 objdump disassembler."""

    name: str = "x86 Disassembler (x86 Binutils)"
