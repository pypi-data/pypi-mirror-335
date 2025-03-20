# SPDX-License-Identifier: GTDGmbH
"""Class for read coverage input and update the instruction."""

from __future__ import annotations

import ast
import csv
from typing import TYPE_CHECKING

from ocgraph.data import Address, Instruction

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.configuration import OcGraphConfiguration


class CoverageReader:  # pylint: disable=too-few-public-methods
    """CoverageReader Class."""

    def __init__(
        self,
        instructions: list[Instruction],
        config: OcGraphConfiguration,
    ) -> None:
        self.instructions = instructions
        self.config = config

    def update_by_csv(self, file_path: str) -> None:
        """Read coverage csv file and update."""
        # Store for coverage information
        coverage_info: dict[int, set[int]] = {}

        # read the csv file. expected values in address and branch_jumps
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                _temp = ast.literal_eval(row["branch_jumps"])
                coverage_info[int(row["address"], 0)] = {int(x, 0) for x in _temp}

        # update instructions
        for instr in self.instructions:
            if (
                instr.address
                and instr.address.abs_addr
                and (covered_branch_targets := coverage_info.get(instr.address.abs_addr, None))
                is not None
            ):
                is_branch = self.config.architecture.is_branch(instr)

                # Check if this is a branch which misses its branch target.
                # This happens when the branch is indirect and
                # objdump does not know the address of the branch target.
                if is_branch:
                    if instr.target is None:
                        instr.target = Address(None)

                    if instr.target.abs_addr is None:
                        max_distance = 0
                        likely_branch_target = None

                        # Determine the most interesting branch target,
                        # which is the one furthest away from the branch location
                        for branch_target in covered_branch_targets:
                            distance = abs(instr.address.abs_addr - branch_target)
                            if distance > max_distance:
                                max_distance = distance
                                likely_branch_target = branch_target

                        instr.target.abs_addr = likely_branch_target

                instr.update_coverage(covered_branch_targets, is_branch=is_branch)
