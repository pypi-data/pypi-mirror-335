"""Represents location in program which may be absolute or relative."""

from __future__ import annotations


class Address:
    """Address Class."""

    def __init__(
        self,
        abs_addr: int | None = None,
        base: str | None = None,
        offset: int | None = None,
    ) -> None:
        self.abs_addr = abs_addr
        self.base = base
        self.offset = offset

    def is_absolute(self) -> bool:
        """
        Return if Address is absolute.

        Examples
        --------
        >>> Address(abs_addr=0x1234).is_absolute()
        True
        >>> Address(base="fn").is_absolute()
        False

        """
        return self.base is None

    def is_relative(self) -> bool:
        """
        Return if Address is relative.

        >>> Address(abs_addr=0x1234).is_relative()
        False
        >>> Address(base="fn").is_relative()
        True
        """
        return not self.is_absolute()

    def __repr__(self) -> str:
        """
        Convert an Address into a representative string.

        >>> Address(abs_addr=0x1234)
        Address(0x1234, None+None)
        >>> Address(base="fn", offset=0x1234)
        Address(None, fn+0x1234)
        >>> Address(abs_addr=0x5678, base="fn", offset=0x1234)
        Address(0x5678, fn+0x1234)
        """
        abs_addr = f"0x{self.abs_addr:x}" if self.abs_addr is not None else None
        base = self.base
        offset = f"0x{self.offset:x}" if self.offset is not None else None
        return f"Address({abs_addr}, {base}+{offset})"
