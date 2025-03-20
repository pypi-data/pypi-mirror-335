# SPDX-License-Identifier: GTDGmbH
"""Contains instruction info for Sparc-compatible targets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .architecture import GenericArchitecture

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.data import Instruction

# fmt: off
sparc_v8_call_opcodes = [
    "call",
]

sparc_v8_sink_opcodes = [
    # ret: return from subroutine
    # retl: return from leaf subroutine
    "ret", "retl",
]

sparc_v8_Bicc_opcodes = [
    # conditional icc branch opcodes
    "ba", "bn", "bne", "be", "bg", "ble", "bge", "bl", "bgu", "bleu", "bcc",
    "bcs", "bpos", "bneg", "bvc", "bvs",
]

sparc_v8_FBfcc_opcodes = [
    # conditional fcc branch opcodes
    "fba", "fbn", "fbu", "fbg", "fbug", "fbl", "fbul", "fblg", "fbne", "fbe",
    "fbue", "fbge", "fbuge", "fble", "fbule", "fbo",
]

sparc_v8_CBfcc_opcodes = [
    # conditional coprocessor opcodes
    "cba", "cbn", "cb3", "cb2", "cb23", "cb1", "cb13", "cb12", "cb123", "cb0",
    "cb03", "cb02", "cb023", "cb01", "cb013", "cb012",
]

sparc_v8_Ticc_opcodes = [
    # conditional traps on icc
    "ta", "tn", "tne", "te", "tg", "tle", "tge", "tl", "tgu", "tleu", "tcc",
    "tcs", "tpos", "tneg", "tvc", "tvs",
]

sparc_v8_branch_cond_delay_opcodes = [
    f"{x},a" for x in
    sparc_v8_Bicc_opcodes +
    sparc_v8_FBfcc_opcodes +
    sparc_v8_CBfcc_opcodes
]

sparc_v8_unconditional_branch_opcodes = [
    "jmpl", "jmp", "b", "b,a",
]

sparc_v8_delayed_opcodes = sparc_v8_Bicc_opcodes + \
                           sparc_v8_FBfcc_opcodes + \
                           sparc_v8_CBfcc_opcodes + \
                           sparc_v8_branch_cond_delay_opcodes + \
                           sparc_v8_unconditional_branch_opcodes

sparc_v8_conditional_branch_opcodes = sparc_v8_Bicc_opcodes + \
                                      sparc_v8_FBfcc_opcodes + \
                                      sparc_v8_CBfcc_opcodes + \
                                      sparc_v8_Ticc_opcodes + \
                                      sparc_v8_branch_cond_delay_opcodes
# fmt: on


class SparcArchitecture(GenericArchitecture):
    """SparcArchitecture Class."""

    def is_call(self, instruction: Instruction) -> bool:
        return instruction.opcode in sparc_v8_call_opcodes

    def is_branch(self, instruction: Instruction) -> bool:
        return instruction.opcode in (
            sparc_v8_conditional_branch_opcodes + sparc_v8_unconditional_branch_opcodes
        )

    def get_branch_delay(self, instruction: Instruction) -> int:
        if instruction.opcode in sparc_v8_delayed_opcodes or self.is_sink(instruction):
            delay = 2
        else:
            delay = 1
        return delay

    def is_direct_branch(self, instruction: Instruction) -> bool:
        # every branch is disassembled with the complete offset,
        # i.e. every branch is direct
        return self.is_branch(instruction)

    def is_unconditional_branch(self, instruction: Instruction) -> bool:
        return instruction.opcode in sparc_v8_unconditional_branch_opcodes

    def is_sink(self, instruction: Instruction) -> bool:
        return instruction.opcode in sparc_v8_sink_opcodes
