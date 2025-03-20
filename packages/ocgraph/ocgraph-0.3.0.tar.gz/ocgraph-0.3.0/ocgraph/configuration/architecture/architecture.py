# SPDX-License-Identifier: GTDGmbH
"""Contains all necessary functions for a TargetInfo class."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.data import Instruction

# Common regexes
HEX_PATTERN = r"[0-9a-fA-F]+"
HEX_LONG_PATTERN = r"(?:0x0*)?" + HEX_PATTERN


class Architecture(ABC):
    """TargetInfo Class defining the target specific instruction set characteristics."""

    @abstractmethod
    def is_call(self, instruction: Instruction) -> bool:
        """Return if disassembled instruction is a subroutine call."""
        raise NotImplementedError  # pragma:no cover

    @abstractmethod
    def is_unconditional_branch(self, instruction: Instruction) -> bool:
        """Return if disassembled instruction is an unconditional branch."""
        raise NotImplementedError  # pragma:no cover

    @abstractmethod
    def get_branch_delay(self, instruction: Instruction) -> int:
        """Return the branch delay of an instruction."""
        raise NotImplementedError  # pragma:no cover

    @abstractmethod
    def is_direct_branch(self, instruction: Instruction) -> bool:
        """Return true when the given instruction is a direct branch."""
        raise NotImplementedError  # pragma:no cover

    @abstractmethod
    def is_branch(self, instruction: Instruction) -> bool:
        """
        Return if disassembled instruction is a branch instruction
        (conditional or unconditional).
        """
        raise NotImplementedError  # pragma:no cover

    @abstractmethod
    def is_sink(self, instruction: Instruction) -> bool:
        """Return if disassembled instruction serves as sink (e.g. ret)."""
        raise NotImplementedError  # pragma:no cover


class GenericArchitecture(Architecture):
    """TargetInfo Class defining the target specific instruction set characteristics."""

    def get_branch_delay(self, instruction: Instruction) -> int:
        """Return the branch delay of an instruction."""
        return 1

    def is_direct_branch(self, instruction: Instruction) -> bool:
        """Return true if the given instruction is a direct branch."""
        return self.is_branch(instruction) and bool(
            re.search(HEX_LONG_PATTERN, "|".join(instruction.ops)),
        )
