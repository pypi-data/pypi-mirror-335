# SPDX-License-Identifier: GTDGmbH
"""Class for drawing the output."""

from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING, Any

from graphviz import Digraph  # type: ignore

from ocgraph.data import Coverage

if TYPE_CHECKING:  # pragma: no cover
    from ocgraph.configuration import OcGraphConfiguration
    from ocgraph.data import BasicBlock

coverage_color = {
    Coverage.MISS: "#f08080",  # light coral
    Coverage.LINE_TAKEN: "#90ee90",  # light green
    Coverage.JUMP_BOTH: "#90ee90",  # light green
    Coverage.JUMP_PASS: "#fdfd96",  # pastel yellow
    Coverage.JUMP_TAKEN: "#fdfd96",  # pastel yellow
}


class Drawer:
    """Drawer Class."""

    def __init__(
        self,
        config: OcGraphConfiguration,
        graph_options: dict[str, Any] | None = None,
    ) -> None:
        self.config = config
        self.graph_option = graph_options if graph_options else {}

    def set_graph_option(self, graph_options: dict[str, Any]) -> None:
        """Set new graph options."""
        self.graph_option = graph_options

    @staticmethod
    def _escape(text: str) -> str:
        """
        Escape used dot graph characters in given instruction so they will be
        displayed correctly.
        """
        text = text.replace("&", "&amp;")
        text = text.replace("<", r"&lt;")
        text = text.replace(">", r"&gt;")
        return text.replace("\t", "&#9;")

    def _create_label(
        self,
        basic_block: BasicBlock,
        line_coverage: bool = False,
    ) -> str:
        """Create annotated graph label."""
        label = ""
        returns = set()

        # start label
        label += '< <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0"> \n'
        # for each instruction in block
        for instr in basic_block.instructions:
            if not instr or not instr.address or not instr.opcode:
                continue

            bg_color = coverage_color[instr.coverage] if line_coverage else "white"
            label += (
                "<TR>"
                f'<TD ALIGN="LEFT" COLSPAN="2" BGCOLOR="{bg_color}" >'
                f"0x{instr.address.abs_addr:0>8x}:   {instr.opcode:<10} "
                f"{Drawer._escape(text=', '.join(instr.ops))}"
                "</TD></TR>\n"
            )
            if self.config.architecture.is_sink(instr):
                for return_addr in instr.returns:
                    if isinstance(return_addr, int):
                        returns.add(f"0x{return_addr:x}")

        # add JUMP/NO JUMP cells with dot PORT navigation
        cells = [basic_block.jump_edge, basic_block.no_jump_edge]
        span = 3 - len(
            [x for x in cells if x is not None],
        )  # 3 - count of trues in cells

        label = self._label_edges(label, basic_block, span, returns)
        label += " </TABLE> >"
        return label

    def _label_edges(
        self,
        label: str,
        basic_block: BasicBlock,
        span: int,
        returns: set[str],
    ) -> str:
        label += "<TR>"
        if basic_block.no_jump_edge:
            label += f'<TD BORDER="1" COLSPAN="{span}" PORT="pass">NO JUMP</TD>'
        if basic_block.jump_edge:
            label += f'<TD BORDER="1" COLSPAN="{span}" PORT="jump">JUMP</TD>'
        if not basic_block.jump_edge and not basic_block.no_jump_edge:
            label += (
                f'<TD BORDER="1" COLSPAN="2">RETURN targets: '
                f'{str(returns) if returns else "--"}</TD>'
            )
        label += "</TR>"
        return label

    def _create_cfg(
        self,
        name: str,
        basic_blocks: dict[int, BasicBlock],
        coverage: bool = False,
    ) -> Digraph:
        """Create a control flow graph."""
        dot = Digraph(name=name, comment=name, engine="dot")
        dot.attr("graph", label=name)
        dot.attr("graph", fontname="Mono")
        dot.attr("node", fontname="Mono")
        dot.attr("edge", fontname="Mono")

        basic_block_keys = []

        # Create nodes in graph
        for address, basic_block in basic_blocks.items():
            key = str(address)
            label = self._create_label(basic_block, coverage)
            dot.node(name=key, label=label, shape="plaintext", **self.graph_option)
            basic_block_keys.append(key)

        # Create edges in graph
        for basic_block in basic_blocks.values():
            if basic_block.jump_edge:
                key = str(basic_block.jump_edge)
                if key not in basic_block_keys:
                    dot.node(
                        name=key,
                        label=hex(basic_block.jump_edge),
                        shape="plaintext",
                        **self.graph_option,
                    )
                    basic_block_keys.append(key)
                dot.edge(f"{basic_block.key}:jump", str(basic_block.jump_edge))
            if basic_block.no_jump_edge:
                key = str(basic_block.no_jump_edge)
                if key not in basic_block_keys:
                    dot.node(
                        name=key,
                        label=hex(basic_block.no_jump_edge),
                        shape="plaintext",
                        **self.graph_option,
                    )
                    basic_block_keys.append(key)
                dot.edge(f"{basic_block.key}:pass", str(basic_block.no_jump_edge))
        return dot

    def view_cfg(self, name: str, basic_blocks: dict[int, BasicBlock]) -> None:  # pragma: no cover
        """View a function graph."""
        dot = self._create_cfg(name, basic_blocks)
        dot.format = "gv"
        with tempfile.NamedTemporaryFile(mode="w+b", prefix=name) as filename:
            dot.view(filename.name)

    def draw_cfg(
        self,
        name: str,
        basic_blocks: dict[int, BasicBlock],
        output: str | None = None,
    ) -> None:
        """Draw a function graph."""
        dot = self._create_cfg(name, basic_blocks, coverage=True)

        filename = output if output else name
        dot.format = "pdf"
        dot.render(filename=filename, cleanup=True)
        self.config.logger.info(f"Saved CFG to a file {filename}.{dot.format}")

        dot.format = "gv"
        dot.render(filename=filename, cleanup=True)
