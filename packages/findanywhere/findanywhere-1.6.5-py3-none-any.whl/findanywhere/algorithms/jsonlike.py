from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from itertools import chain

from findanywhere.types.common import JSONType


def is_primitive(value: JSONType) -> bool:
    """
    Checks if a value is a primitive data type.

    Args:
        value: The value to be checked.

    Returns:
        bool: True if the value is a primitive data type, False otherwise.
    """
    return isinstance(value, (int, float, bool, str, type(None)))


@dataclass(frozen=True)
class JSONFragment:
    """

    The `JSONFragment` class represents a fragment of a JSON object, which includes a value and its path within the
    JSON object.

    Attributes:
        value (JSONType): The value of the JSON fragment.
        path (Sequence[str | int]): The path of the JSON fragment within the JSON object.

    Methods:
        from_parent(cls, parent: 'JSONFragment', index: str | int, value: JSONType) -> 'JSONFragment':
            Creates a new `JSONFragment` object from a parent `JSONFragment` object, assigning it a value and an index.

    """
    value: JSONType
    path: Sequence[str | int] = field(default_factory=list)

    def __lt__(self, other) -> bool:
        return self.path < other.path

    @property
    def parent(self) -> Sequence[str | int]:
        return self.path[0: -1]

    @classmethod
    def from_parent(cls, parent: 'JSONFragment', index: str | int, value: JSONType) -> 'JSONFragment':
        """
        Args:
            parent: The parent JSONFragment object from which the new JSONFragment will be created.
            index: The index of the new JSONFragment within the parent object.
            value: The value that will be assigned to the new JSONFragment.

        Returns:
            JSONFragment: The newly created JSONFragment object with the specified parent, index, and value.
        """
        return replace(parent, value=value, path=list(chain(parent.path, (index,))))


def traverse_jsonlike(
    fragment: JSONFragment | JSONType
) -> Iterable[JSONFragment]:
    """
    Args:
        fragment: A JSONFragment or a JSONType object representing a fragment of a JSON-like structure.

    Returns:
        An iterable of JSONFragments representing all the primitive elements in the given JSON-like structure.
    """
    if not isinstance(fragment, JSONFragment):
        fragment = JSONFragment(fragment)
    match fragment.value:
        case list(elements):
            for i, element in enumerate(elements):
                element_fragment: JSONFragment = JSONFragment.from_parent(fragment, i, element)
                if is_primitive(element):
                    yield element_fragment
                else:
                    yield from traverse_jsonlike(element_fragment)
        case dict(items):
            for key, value in items.items():
                item_fragment: JSONFragment = JSONFragment.from_parent(fragment, key, value)
                if is_primitive(value):
                    yield item_fragment
                else:
                    yield from traverse_jsonlike(item_fragment)
        case _:
            yield fragment