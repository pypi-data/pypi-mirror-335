"""Class configuring the used disassembler tool."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from re import Match
from typing import TYPE_CHECKING

from ocgraph.data import Address, FunctionHeader, Instruction

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator

    from ocgraph.configuration.architecture.architecture import Architecture

# Common regexes
HEX_PATTERN = r"[0-9a-fA-F]+"
HEX_LONG_PATTERN = r"(?:0x0*)?" + HEX_PATTERN


class DisassemblerError(Exception):
    """Raised when the extract_information method was not successful."""


class Disassembler(ABC):
    """Disassembler Class."""

    architecture: Architecture
    """Architecture configuration used by the disassembler"""

    name: str = ""
    """Disassembler tool identification like SparcV8Objdump, GDB, ..."""

    @abstractmethod
    def extract_information(self, lines: list[str]) -> Generator[Instruction | FunctionHeader]:
        """
        Parse the given lines of disassembler output.

        This extracts all available information from the disassembler
        output and returns a generator providing Instruction or a
        FunctionHeader.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def parse_jump_target(self, ops: list[str]) -> int | None:
        """Return the jump target value from a list of operands."""
        raise NotImplementedError  # pragma: no cover


class ObjdumpDisassembler(Disassembler):
    """Objdump Disassembler Class."""

    name: str = ""
    """ Disassembler tool identification like SparcV8Objdump, GDB, ..."""

    function_header_regex: str = r"^([0-9a-fA-F]+) <(.*)>:$"
    function_header_groups: dict[str, int] = {
        "address": 1,
        "name": 2,
    }

    instruction_regex: str = (
        r"^\s*([0-9a-fA-F]+):\t((?:[0-9a-fA-F]+ )+) *\t(\S+)[\t ]*([^\n\r\f\v;]*?) ?[\t ]*(?:|[#!;] *([0-9a-fA-F]+) *<(.*?)(\+.*)?>|\t.*:.*|<(.*)(\+.*)>|[#!;] 0x([0-9a-fA-F]+)|;abs 0x([0-9a-fA-F]+)|;.*)$"
    )
    instruction_groups: dict[str, int] = {
        "address": 1,
        "encoding": 2,
        "mnemonic": 3,
        "operands": 4,
        "decoded_immediate1": 5,
        "symbol": 6,
        "symbol_offset": 7,
        "relative_jump_base": 8,
        "relative_jump_offset": 9,
        "decoded_immediate2": 10,
        "absolute_jump_target": 11,
    }

    def __init__(self) -> None:
        self.current_function: str | None = None

    def extract_information(self, lines: list[str]) -> Generator[Instruction | FunctionHeader]:
        """
        Parse the given lines of disassembler output.

        This extracts all available information from the disassembler
        output and returns a generator providing Instruction or a
        FunctionHeader.
        """

        def get_match(match_object: Match[str], match_number: int) -> str:
            return match_object.group(match_number)

        for i, line in enumerate(lines):
            instruction = re.match(self.instruction_regex, line)
            function_header = re.match(self.function_header_regex, line)

            if function_header:
                address = get_match(function_header, self.function_header_groups["address"])
                name = get_match(function_header, self.function_header_groups["name"])
                self.current_function = name
                yield FunctionHeader(name, int(address, 16))
            elif instruction:
                relative_jump_base = get_match(
                    instruction,
                    self.instruction_groups["relative_jump_base"],
                )
                relative_jump_offset = get_match(
                    instruction,
                    self.instruction_groups["relative_jump_offset"],
                )
                address = get_match(instruction, self.instruction_groups["address"])
                absolute_jump_target = get_match(
                    instruction,
                    self.instruction_groups["absolute_jump_target"],
                )
                ops = [
                    x.strip()
                    for x in get_match(instruction, self.instruction_groups["operands"]).split(",")
                ]

                if address and relative_jump_base and relative_jump_offset:
                    target = Address(
                        base=relative_jump_base,
                        offset=int(relative_jump_offset, 16),
                    )
                elif address and absolute_jump_target:
                    target = Address(
                        abs_addr=int(absolute_jump_target, 16),
                        base=relative_jump_base,
                    )
                else:
                    target = Address(abs_addr=None)

                yield Instruction(
                    lineno=i,
                    address=Address(abs_addr=int(address, 16), base=self.current_function),
                    opcode=get_match(instruction, self.instruction_groups["mnemonic"]),
                    ops=ops,
                    target=target,
                )

    def parse_jump_target(self, ops: list[str]) -> int | None:
        """Return the jump target value from a list of operands."""
        # it assumes the last operand of the branch to be the target address
        return int(ops[-1], 16)
