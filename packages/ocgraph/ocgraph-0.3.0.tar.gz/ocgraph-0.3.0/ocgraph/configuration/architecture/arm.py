# SPDX-License-Identifier: GTDGmbH
"""Contains instruction info for ARM-compatible targets."""

import re

from ocgraph.data import Instruction

from .architecture import GenericArchitecture


class ArmArchitecture(GenericArchitecture):
    """ArmArchitecture Class."""

    def is_call(self, instruction: Instruction) -> bool:
        # Various flavors of call:
        #   bl 0x19d90 <_IO_vtable_check>
        # Note that we should be careful to not mix it with conditional
        # branches like 'ble'.
        if instruction.opcode:
            return instruction.opcode.startswith("bl") and instruction.opcode not in (
                "blt",
                "ble",
                "bls",
            )
        return False

    def is_branch(self, instruction: Instruction) -> bool:
        if instruction.opcode:
            return instruction.opcode[0] == "b" and not self.is_call(instruction)
        return False

    def is_unconditional_branch(self, instruction: Instruction) -> bool:
        return instruction.opcode == "b"

    def is_sink(self, instruction: Instruction) -> bool:
        """
        Is this an instruction which terminates function execution e.g. return?
        Detect various flavors of return like
          bx lr
          pop {r2-r6,pc}
        Note that we do not consider conditional branches (e.g. 'bxle') to sink.
        """
        return (
            bool(
                re.search(
                    r"\bpop\b.*\bpc\b",
                    f"{instruction.opcode} {','.join(instruction.ops)}" or "",
                ),
            )
            or (instruction.opcode == "bx" and instruction.ops[0] == "lr")
            or instruction.opcode == "udf"
        )
