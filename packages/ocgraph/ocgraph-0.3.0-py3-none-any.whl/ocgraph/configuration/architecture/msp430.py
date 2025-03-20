# SPDX-License-Identifier: GTDGmbH
"""Contains instruction info for MSP430-compatible targets."""

from ocgraph.data import Instruction

from .architecture import GenericArchitecture

msp430_conditional_branches = [
    "jc",
    "jhs",
    "jeq",
    "jz",
    "jge",
    "jl",
    "jn",
    "jnc",
    "jlo",
    "jne",
    "jnz",
]

msp430_unconditional_branches = [
    "br",
    "jmp",
]


class MSP430Architecture(GenericArchitecture):
    """Msp430Architecture Class."""

    def is_call(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return "call" in instruction.opcode
        return False

    def is_branch(self, instruction: Instruction) -> bool:
        return instruction.opcode in (msp430_conditional_branches + msp430_unconditional_branches)

    def is_direct_branch(self, instruction: Instruction) -> bool:
        return self.is_branch(instruction)

    def is_unconditional_branch(self, instruction: Instruction) -> bool:
        return instruction.opcode in msp430_unconditional_branches

    def is_sink(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return instruction.opcode.startswith("ret")
        return False
