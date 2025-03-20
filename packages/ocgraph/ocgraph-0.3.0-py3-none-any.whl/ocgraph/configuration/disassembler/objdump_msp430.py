"""Class for parsing the objdump MSP430 input."""

from __future__ import annotations

import re

from .disassembler import ObjdumpDisassembler


class ObjDumpMsp430Disassembler(ObjdumpDisassembler):
    """Objdump MSP430 disassembler."""

    name: str = "MSP430 Objdump Disassembler"

    def parse_jump_target(self, ops: list[str]) -> int | None:
        pattern_jump = r"abs\s+(0x[0-9a-fA-F]+)"
        pattern_call = r"#0x([0-9a-fA-F]+)"
        for op in ops:
            match_jump = re.search(pattern_jump, op)
            match_call = re.search(pattern_call, op)
            if match_jump:
                abs_adr = match_jump.group(1)
                return int(abs_adr, 16)
            if match_call:
                abs_adr = match_call.group(1)
                return int(abs_adr, 16)
        return None
