# SPDX-License-Identifier: GTDGmbH
"""Contains instruction info for X86-compatible targets."""

from ocgraph.data import Instruction

from .architecture import GenericArchitecture


class X86Architecture(GenericArchitecture):
    """X86Architecture Class."""

    def is_call(self, instruction: Instruction) -> bool:
        # Various flavors of call:
        #   call   *0x26a16(%rip)
        #   call   0x555555555542
        #   addr32 call 0x55555558add0
        if instruction.opcode:
            return "call" in instruction.opcode
        return False

    def is_branch(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return instruction.opcode[0] == "j"
        return False

    def is_unconditional_branch(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return instruction.opcode.startswith("jmp")
        return False

    def is_sink(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return instruction.opcode.startswith("ret")
        return False
