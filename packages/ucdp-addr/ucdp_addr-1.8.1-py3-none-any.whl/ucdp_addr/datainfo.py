"""Data Information."""

from collections.abc import Iterator
from typing import TypeAlias

import ucdp as u

from .addrrange import AddrRange
from .data import Data, DataType, check_data, get_datatype

AddrData: TypeAlias = tuple[int, int]
"""Address-Data Pair."""


class DataInfo(u.Object):
    """
    Data Information.

    Single Data:

        >>> datainfo = DataInfo.create(5)
        >>> datainfo
        DataInfo(datatype=SINGLE, data=5)
        >>> str(datainfo)
        'SINGLE: 5'
        >>> tuple(datainfo.iter(AddrRange(width=64, depth=8)))
        ((Hex('0x0'), 5),)
        >>> tuple(datainfo.iter(AddrRange(baseaddr=0x1000, width=64, depth=8)))
        ((Hex('0x1000'), 5),)

    Burst Data:

        >>> datainfo = DataInfo.create((5, 6, 7))
        >>> datainfo
        DataInfo(datatype=BURST, data=(5, 6, 7))
        >>> str(datainfo)
        'BURST: (5, 6, 7)'
        >>> tuple(datainfo.iter(AddrRange(width=64, depth=8)))
        ((Hex('0x0'), 5), (Hex('0x8'), 6), (Hex('0x10'), 7))
        >>> tuple(datainfo.iter(AddrRange(baseaddr=0x1000, width=64, depth=8)))
        ((Hex('0x1000'), 5), (Hex('0x1008'), 6), (Hex('0x1010'), 7))

    Scattered Data:

        >>> datainfo = DataInfo.create(((16, 5), (28, 6), (60, 7)))
        >>> datainfo
        DataInfo(datatype=SCAT, data=((16, 5), (28, 6), (60, 7)))
        >>> str(datainfo)
        'SCAT: ((16, 5), (28, 6), (60, 7))'
        >>> tuple(datainfo.iter(AddrRange(width=64, depth=8)))
        ((Hex('0x10'), 5), (Hex('0x1C'), 6), (Hex('0x3C'), 7))
        >>> tuple(datainfo.iter(AddrRange(baseaddr=0x1000, width=64, depth=8)))
        ((Hex('0x1010'), 5), (Hex('0x101C'), 6), (Hex('0x103C'), 7))

    Errors:

        >>> DataInfo.create('a')
        Traceback (most recent call last):
          ...
        TypeError: a
        >>> DataInfo.create(('a', 'b'))
        Traceback (most recent call last):
          ...
        TypeError: ('a', 'b')
    """

    datatype: DataType
    data: Data

    def __str__(self) -> str:
        return f"{self.datatype.name}: {self.data}"

    @staticmethod
    def create(data: Data) -> "DataInfo":
        """Create :any:`DataInfo` for `data`."""
        datatype = get_datatype(data)
        return DataInfo(datatype=datatype, data=data)

    def iter(self, addrrange: AddrRange) -> Iterator[AddrData]:
        """Iteratate over single address value pairs according to access."""
        yield from _iter_data(self.datatype, self.data, addrrange)


def _iter_data(datatype: DataType, data: Data, addrrange: AddrRange) -> Iterator[AddrData]:
    baseaddr = addrrange.baseaddr
    check_data(data, addrrange.width)
    if datatype == DataType.SINGLE:
        yield baseaddr, data
    elif datatype == DataType.BURST:
        wordsize = addrrange.wordsize
        for idx, value in enumerate(data):  # type: ignore[arg-type]
            yield u.Hex(baseaddr + idx * wordsize), value
    else:
        addrmask = addrrange.addrmask
        for addr, value in data:  # type: ignore[union-attr]
            yield baseaddr + (addr & addrmask), value
