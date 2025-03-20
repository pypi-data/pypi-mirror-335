"""Holds info about branch sources and destinations in asm function."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.configuration.configuration import OcGraphConfiguration

    from .address import Address
    from .instruction import Instruction


class JumpTable:
    """JumpTable Class."""

    def __init__(
        self,
        instructions: list[Instruction],
        configuration: OcGraphConfiguration,
    ) -> None:
        self.config: OcGraphConfiguration = configuration

        # Address where the jump begins and value which address
        # to jump to. This also includes calls.
        self.abs_sources: dict[int, Address] = {}
        self.rel_sources: dict[int, Address] = {}

        # Addresses where jumps end inside the current function.
        self.abs_destinations: set[int] = set()
        self.rel_destinations: set[int] = set()

        # Iterate over the instructions and collect jump targets and branching points.
        for instr in instructions:
            if instr is None or instr.target is None or instr.address is None:
                continue

            if instr.target.abs_addr is not None and instr.address.abs_addr is not None:
                self.abs_sources[instr.address.abs_addr] = instr.target
                self.abs_destinations.add(instr.target.abs_addr)

            if instr.target.offset is not None and instr.address.offset is not None:
                self.rel_sources[instr.address.offset] = instr.target
                self.rel_destinations.add(instr.target.offset)

    def is_jump_target(self, addr: Address) -> bool:
        """Return if address is a destination."""
        if addr.abs_addr is not None:
            return addr.abs_addr in self.abs_destinations
        if addr.offset is not None:
            return addr.offset in self.rel_destinations
        return False

    def get_target(self, addr: Address) -> Address | None:
        """Return the target of a branch."""
        if addr.abs_addr is not None:
            return self.abs_sources.get(addr.abs_addr)
        if addr.offset is not None:
            return self.rel_sources.get(addr.offset)
        return None
