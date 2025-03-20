"""Encoding Class."""

from __future__ import annotations


class Encoding:
    """
    Encoding represents a sequence of bytes for instruction encoding.

    E.g. the '31 c0' in:

    '16bd3:	31 c0                	xor    %eax,%eax'
    """

    def __init__(self, bites: list[int]) -> None:
        self.bites = bites

    def __len__(self) -> int:
        """
        Return size of the bytes.

        >>> len(Encoding([0xa,0xb,0xc]))
        3
        """
        return len(self.bites)

    def __repr__(self) -> str:
        """
        Convert an Encoding to a readable string.

        >>> Encoding([0xa,0xb,0xc])
        0xa 0xb 0xc
        """
        return " ".join(f"{b:#x}" for b in self.bites)
