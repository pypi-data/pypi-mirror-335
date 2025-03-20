"""Represents a function with an address."""


class FunctionHeader:
    """FunctionHeader Class."""

    def __init__(
        self,
        name: str,
        addr: int,
    ) -> None:
        """Create a new FunctionHeader."""
        self.name = name
        self.addr = addr

    def __repr__(self) -> str:
        """
        Transform a FunctionHeader into a readable string.

        >>> FunctionHeader("fn", 0x1234)
        FunctionHeader(fn at 0x1234)
        """
        return f"FunctionHeader({self.name} at 0x{self.addr:x})"
