from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Tokenizer(Protocol):
    """Tokenizer class for tokenizing a string into a sequence of strings.

    This class defines a protocol for tokenizing a given string into a sequence of strings.

    Methods:
        __call__: Tokenizes the given string and returns a sequence of strings.
    """
    def __call__(self, string: str) -> Sequence[str]:
        ...