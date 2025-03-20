"""Basic Block Class."""

from typing import Any

from .instruction import Instruction


class BasicBlock:
    """Class to represent an object code basic block as node in CFG."""

    def __init__(self, key: Any) -> None:
        self.key = key
        self.instructions: list[Instruction] = []
        self.jump_edge = None
        self.no_jump_edge = None

    def add_instruction(self, instruction: Instruction) -> None:
        """Add instruction to this block."""
        self.instructions.append(instruction)

    def add_jump_edge(self, basic_block_key: Any) -> None:
        """Add jump target block to this block."""
        if isinstance(basic_block_key, BasicBlock):
            self.jump_edge = basic_block_key.key
        else:
            self.jump_edge = basic_block_key

    def add_no_jump_edge(self, basic_block_key: Any) -> None:
        """Add no jump target block to this block."""
        if isinstance(basic_block_key, BasicBlock):
            self.no_jump_edge = basic_block_key.key
        else:
            self.no_jump_edge = basic_block_key

    def __repr__(self) -> str:
        """Convert a BasicBlock into a representative string."""
        return f"BasicBlock({', '.join([str(i) for i in self.instructions])})"
