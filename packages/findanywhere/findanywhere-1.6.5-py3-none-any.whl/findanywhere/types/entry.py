from dataclasses import dataclass
from typing import TypeVar, Generic

Position = TypeVar('Position')
DataType = TypeVar('DataType')

@dataclass(frozen=True)
class Entry(Generic[Position, DataType]):
    """
    Class representing an entry in a data structure.

    Attributes:
        position: The position of the entry.
        value: The value stored in the entry.

    Generic type parameters:
        Position: The type of the position of the entry.
        DataType: The type of the value stored in the entry.

    """
    position: Position
    value: DataType