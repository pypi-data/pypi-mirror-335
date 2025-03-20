# SPDX-License-Identifier: GTDGmbH

"""
Module entry point for the ocgraph package.

Let this module be executed from the command line with python -m ocgraph from root of the project.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from .configuration import OcGraphConfiguration
from .interface import Analyzer, CoverageReader, Drawer

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence


def read_lines(file_path: str) -> list[str]:
    """Read all lines from the file and return them as a list."""
    with Path(file_path).open("r", encoding="utf-8-sig") as file:
        return file.readlines()


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Separate argument parser for testing purposes."""
    parser = argparse.ArgumentParser(
        description="Assembly to Control-Flow-Graph rendering.",
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Disassembled object file",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--diss",
        help="Disassembler option",
        required=True,
        choices=OcGraphConfiguration.disassemblers(),
    )
    parser.add_argument(
        "-a",
        "--arch",
        help="Architecture option",
        required=True,
        choices=OcGraphConfiguration.architectures(),
    )

    parser.add_argument("-c", "--coverage", help="Coverage file for printing coverage")
    parser.add_argument("-v", "--view", action="store_true", help="View as a dot graph")
    parser.add_argument("-o", "--output", help="Target output filename")
    parser.add_argument(
        "-l",
        "--logger",
        choices=OcGraphConfiguration.loggers(),
        default="default",
        help="Logging mechanism preset",
    )
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> None:
    """Command-line entry point to the program."""
    parsed_args = parse_args(args)

    # Create configuration
    config = OcGraphConfiguration(
        disassembler=parsed_args.diss,
        arch=parsed_args.arch,
        logging_preset=parsed_args.logger,
    )

    lines = read_lines(parsed_args.file)

    analyser = Analyzer(config=config)
    analyser.parse_lines(lines=lines)

    if parsed_args.coverage:
        cov_reader = CoverageReader(instructions=analyser.instructions, config=config)
        cov_reader.update_by_csv(parsed_args.coverage)

    analyser.analyze()

    drawer = Drawer(analyser.configuration)
    drawer.draw_cfg(
        name=analyser.function_name or "",
        basic_blocks=analyser.basic_blocks,
        output=parsed_args.output,
    )
