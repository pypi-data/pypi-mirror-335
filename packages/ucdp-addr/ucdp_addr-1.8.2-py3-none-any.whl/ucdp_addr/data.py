"""Access Type Description."""

from enum import Enum
from typing import Any, TypeAlias

Data: TypeAlias = int | tuple[int, ...] | list[int] | tuple[tuple[int, int], ...] | list[tuple[int, int]]
"""Data."""


class DataType(Enum):
    """Trans Type."""

    SINGLE = 0
    BURST = 1
    SCAT = 2

    def __repr__(self):
        return self.name


def check_data(data: Data, width: int):
    """Check Data."""
    high = 2**width - 1
    for idx, value in enumerate(_unify_data(data)):
        if value > high or value < 0:
            raise ValueError(f"value {value} at index {idx} exceeds limits [0, {high}]")


def _unify_data(data: Data) -> list[int]:
    if isinstance(data, int):
        return [data]
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return data  # type: ignore[return-value]
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            return [value for _, value in data]
    raise TypeError(data)


def get_size(data: Any, wordsize: int) -> int:
    """Determine Maximum Addressed Size of Data."""
    if isinstance(data, int):
        return wordsize
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return wordsize * len(data)
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            addrs = [addr for addr, _ in data]  # type:ignore[union-attr]
            return max(addrs) + wordsize
    raise TypeError(data)


def get_datatype(data: Any) -> DataType:
    """Data Type."""
    if isinstance(data, int):
        return DataType.SINGLE
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return DataType.BURST
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            return DataType.SCAT
    raise TypeError(data)
