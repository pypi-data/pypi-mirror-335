"""Class for parsing the input."""

from __future__ import annotations

from .disassembler import ObjdumpDisassembler


class GdbDisassembler(ObjdumpDisassembler):
    """x86 GDB disassembler."""

    name: str = "Default GDB Disassembler (x86 Binutils)"
