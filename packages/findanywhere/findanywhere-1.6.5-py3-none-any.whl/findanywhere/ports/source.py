from collections.abc import Iterable, Callable, Sequence
from dataclasses import dataclass, field
from typing import TypeVar, Protocol, TypeAlias, Generic, Any

from findanywhere.tokeinize import TOKENIZER_FACTORIES
from findanywhere.types.entry import Entry
from findanywhere.types.factory import Config
from findanywhere.types.tokenize import Tokenizer

Location = TypeVar('Location', contravariant=True)
Position = TypeVar('Position')
DataType = TypeVar('DataType')


def everything(_: Position) -> bool:
    """
    Args:
        _: The Position object to be checked for evaluation.

    Returns:
        bool: Returns True.

    """
    return True


class SourcePort(Protocol[Location, Position, DataType]):
    """
    Retrieves a sequence of Entry objects based on the given location and optional predicate.
    """
    def __call__(
            self, location: Location, predicate: Callable[[Position], bool] = everything
    ) -> Iterable[Sequence[Entry[Position, DataType]]]:
        """
        Args:
            location: A Location object that specifies the location to search for entries.
            predicate: A Callable object that takes a Position object as input and returns a boolean value.
            The predicate is used to filter entries based on specific criteria. If not provided, the default predicate
            (everything) will be used.

        Returns:
            An iterable sequence of Entry objects, where each entry contains a Position object and a DataType object.
        """
        ...


SourceAdapter: TypeAlias = SourcePort


@dataclass(frozen=True)
class SourceConfig(Config, Generic[Location]):
    """
    Class representing the source configuration for the application.
    """
    @classmethod
    def location_type(cls) -> type[Location]:
        """
        Returns the type of the 'Location' class.

        Returns:
            The type of the 'Location' class.

        Raises:
            NotImplementedError: Subclasses should implement this method.
        """
        raise NotImplementedError()

    tokenizer: Tokenizer | str = 'delimiter'
    tokenizer_config: dict[str, Any] = field(default_factory=dict)

    def get_tokenizer(self) -> Tokenizer:
        if isinstance(self.tokenizer, str):
            return TOKENIZER_FACTORIES[self.tokenizer].from_dict(self.tokenizer_config)
        if isinstance(self.tokenizer, Tokenizer):
            return self.tokenizer
        raise TypeError(f'Not a tokenizer or tokenizer name: {self.tokenizer}')