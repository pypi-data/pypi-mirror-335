"""Class for read and analyze the input string."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ocgraph.data import Address, BasicBlock, Instruction, JumpTable

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.configuration import OcGraphConfiguration
    from ocgraph.configuration.disassembler import Disassembler


class Analyzer:
    """Analyzer Class."""

    def __init__(self, config: OcGraphConfiguration) -> None:
        self.configuration = config
        self.logger = self.configuration.logger
        self.parser: Disassembler = self.configuration.disassembler

        self.lines: list[str] = []
        self.function_name: str = ""
        self.instructions: list[Instruction] = []
        self.jump_table: JumpTable
        self.basic_blocks: dict[int, BasicBlock] = {}

    def parse_file(self, file_path: str) -> None:
        """Parse a assembler file."""
        with open(file_path, encoding="utf8") as asm_file:
            lines = asm_file.readlines()
        self.parse_lines(lines)

    def parse_lines(self, lines: list[str]) -> None:
        """Parse a list of assembly lines."""
        self.lines = lines
        self._parse_instructions()
        # Compute already known jump targets
        # This is only a first pass as indirect jumps can't be
        # discovered yet
        self._compute_jump_targets()

    def analyze(self) -> None:
        # Re-compute jump targets this time with indirect branches
        self._compute_jump_targets()
        self._infer_relative_addresses()
        self._create_jump_table()
        self._create_basic_blocks()

    def _parse_instructions(self) -> None:
        self.instructions = []

        for info in self.parser.extract_information(self.lines):
            if isinstance(info, Instruction):
                self.instructions.append(info)
            else:
                if self.function_name:
                    msg = "we handle only one function for now"
                    raise RuntimeError(msg)
                self.logger.info(f"New function {info.name}")
                self.function_name = info.name

    def _compute_jump_targets(self) -> None:
        # Infer target address for jump instructions
        for instr in self.instructions:
            if (
                instr.target is None or instr.target.abs_addr is None
            ) and self.configuration.architecture.is_direct_branch(instr):
                if instr.target is None:
                    instr.target = Address(None)
                # parse the absolute target out of the operands
                # (first hex address is assumed to be the target address)
                try:
                    instr.target.abs_addr = self.parser.parse_jump_target(instr.ops)
                except ValueError:
                    # Mark the address as not (yet) known
                    instr.target.abs_addr = None

    def _infer_relative_addresses(self) -> None:
        # Infer relative addresses (for objdump or stripped gdb)
        if (
            len(self.instructions) > 0
            and self.instructions[0].address
            and self.instructions[0].address.abs_addr is not None
        ):
            start_address = self.instructions[0].address.abs_addr
        else:
            start_address = 0
        if (
            len(self.instructions) > 0
            and self.instructions[-1].address
            and self.instructions[-1].address.abs_addr is not None
        ):
            end_address = self.instructions[-1].address.abs_addr
        else:
            end_address = 0xFFFFFFFF

        for instr in self.instructions:
            for addr in (instr.address, instr.target):
                if (
                    addr is not None
                    and addr.abs_addr is not None
                    and addr.offset is None
                    and start_address <= addr.abs_addr <= end_address
                ):
                    addr.offset = addr.abs_addr - start_address

        self.logger.debug("Instructions:")
        for instruction in self.instructions:
            if instruction is not None:
                self.logger.debug(f"  {instruction}")

    def _create_jump_table(self) -> None:
        self.jump_table = JumpTable(self.instructions, self.configuration)

        self.logger.debug("Absolute destinations:")
        for dst in self.jump_table.abs_destinations:
            if dst:
                self.logger.debug(f"  {dst:#x}")
            else:
                self.logger.debug("  None")
        self.logger.debug("Relative destinations:")
        for dst in self.jump_table.rel_destinations:
            if dst:
                self.logger.debug(f"  {dst:#x}")
            else:
                self.logger.debug("  None")
        self.logger.debug("Absolute branches:")
        for key, addr in self.jump_table.abs_sources.items():
            self.logger.debug(f"  {key:#x} -> {addr}")
        self.logger.debug("Relative branches:")
        for key, addr in self.jump_table.rel_sources.items():
            self.logger.debug(f"  {key:#x} -> {addr}")

    def _create_basic_blocks(self) -> None:
        """
        Now iterate over the assembly again and split it to basic blocks using the branching
        information from earlier.
        """
        self.basic_blocks = {}

        curr_basic_block: BasicBlock | None = None
        # Store last block if ending with branch opcode
        prev_branch_block: BasicBlock | None = None

        # block completion flag (introduced for SPARC pipeline)
        block_completion: int = 0

        for instruction in self.instructions:
            # if block completion is in progress
            if block_completion > 0:
                block_completion -= 1
                if block_completion > 0 and curr_basic_block:
                    self.basic_blocks[curr_basic_block.key].add_instruction(instruction)
                    continue
                curr_basic_block = None

            # Current program counter
            pc_addr = instruction.address
            # Get optional jump target
            jump_target = self.jump_table.get_target(pc_addr or Address(None))
            is_unconditional = self.configuration.architecture.is_unconditional_branch(
                instruction,
            )

            # Start new blocks if last ended
            if curr_basic_block is None and pc_addr is not None and pc_addr.abs_addr is not None:
                # Create new basic block
                self.basic_blocks[pc_addr.abs_addr] = curr_basic_block = BasicBlock(
                    key=pc_addr.abs_addr,
                )

                # if previous basic block ended in branch instruction. Add the basic
                # block what follows if the jump was not taken.
                if prev_branch_block is not None:
                    prev_branch_block.add_no_jump_edge(curr_basic_block)
                    prev_branch_block = None
            # or if current address is a jump target
            elif (
                curr_basic_block is not None
                and pc_addr is not None
                and pc_addr.abs_addr is not None
                and self.jump_table.is_jump_target(pc_addr)
            ):
                closing_block = curr_basic_block
                self.basic_blocks[pc_addr.abs_addr] = curr_basic_block = BasicBlock(
                    key=pc_addr.abs_addr,
                )
                closing_block.add_no_jump_edge(pc_addr.abs_addr)

            if curr_basic_block is not None:
                curr_basic_block.add_instruction(instruction)

            # End current block if current opcode is a jump/branch/sink
            if jump_target and curr_basic_block:
                curr_basic_block.add_jump_edge(jump_target.abs_addr)
                prev_branch_block = None if is_unconditional else curr_basic_block
                block_completion = self.configuration.architecture.get_branch_delay(
                    instruction,
                )
            elif self.configuration.architecture.is_sink(instruction):
                block_completion = self.configuration.architecture.get_branch_delay(
                    instruction,
                )
                prev_branch_block = None

        if prev_branch_block:
            # If last instruction of the function is jump/call, then add dummy
            # block to designate end of the function.
            end_instruction = Instruction(
                0,
                Address(None),
                "",
                [],
                Address(None),
            )
            end_block = BasicBlock("end_of_function")
            end_block.add_instruction(end_instruction)
            prev_branch_block.add_no_jump_edge(end_block.key)
            self.basic_blocks[end_block.key] = end_block
