"""Module, Word and Field Reference."""

from typing import TypeAlias

import ucdp as u

from .addrrange import AddrRange
from .addrspace import Addrspace, Field, Word


class AddrMapRef(u.Object):
    """Address Map Reference."""

    addrrange: AddrRange
    """Address Range."""

    addrspace: Addrspace | None = None
    """Address Space."""

    word: Word | None = None
    """Word."""

    field: Field | None = None
    """Field."""

    def __str__(self) -> str:
        if self.addrspace:
            result = f"{self.addrspace.name}"
            if self.word:
                result = f"{result}.{self.word.name}"
                if self.field:
                    result = f"{result}.{self.field.name}"
            return result
        return f"{self.addrrange.baseaddr}"

    @staticmethod
    def create(
        addrspace: Addrspace, word: Word | None = None, field: Field | None = None, addrrange: AddrRange | None = None
    ) -> "AddrMapRef":
        """
        Create Addrspace with Proper AddrRange.

        Args:
            addrspace: Address Space

        Keyword Args:
            word: Word
            field: Field (requires word as well)
            addrrange: Address Range
        """
        if addrrange is None:
            if word:
                addrrange = AddrRange(
                    baseaddr=addrspace.baseaddr + word.byteoffset,
                    width=word.width,
                    depth=word.depth or 1,
                )
            else:
                addrrange = AddrRange(baseaddr=addrspace.baseaddr, width=addrspace.width, depth=addrspace.depth)
        return AddrMapRef(addrrange=addrrange, addrspace=addrspace, word=word, field=field)


ToAddrMapRef: TypeAlias = AddrMapRef | AddrRange | Addrspace | str | int
"""Unresolved Address Map Reference."""

RawAddrMapRef = ToAddrMapRef
"""Obsolete Alias."""
