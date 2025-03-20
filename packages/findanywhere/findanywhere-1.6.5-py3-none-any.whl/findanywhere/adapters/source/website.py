from collections import defaultdict
from collections.abc import Sequence, Callable, Iterable
from dataclasses import dataclass, field
from functools import partial
from itertools import count, chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator

from bs4 import BeautifulSoup, Tag

from findanywhere.ports.source import everything, SourceConfig, SourceAdapter, Location
from findanywhere.types.common import RemoteLocation, LocalOrRemoteLocation
from findanywhere.types.entry import Entry
from findanywhere.types.factory import as_factory
from findanywhere.utils.buffer_database import BufferDatabase


@dataclass(frozen=True)
class HTMLPosition:
    """Class to represent a position in an XML document.

    Attributes:
        tag (str): The tag of the XML element at this position.
        path (Sequence[str]): The path of tags from the root to the element at this position.
        index (int): The index of the XML element within its parent.
        token (int): The index of the token within the element.

    """
    tag: str
    path: Sequence[str]
    index: int
    token: int


def _get_parents(tag: Tag) -> Sequence[str]:
    """
    Args:
        tag (Tag): The tag whose parents need to be retrieved.

    Returns:
        Sequence[str]: The parents of the given tag in reverse order.
    """
    return tuple(parent.name for parent in reversed(tuple(tag.parents)))[1:]


@dataclass(frozen=True)
class HTMLTag:
    """Represent an HTML tag with its text content and path.

    Attributes:
        tag (str): The name of the HTML tag.
        text (str): The text content of the HTML tag.
        path (Sequence[str]): The path of parent tags leading to this tag.

    Methods:
        from_tag(tag: Tag) -> HTMLTag: Create an HTMLTag instance from a BeautifulSoup Tag object.
        __lt__(other: HTMLTag) -> bool: Compare the path of this HTMLTag with another HTMLTag.

    """
    tag: str
    text: str
    path: Sequence[str]

    @property
    def canonical_path(self) -> str:
        """
        Returns the canonical path of the current object.

        This method concatenates all elements of the `path` attribute with a forward slash as a separator and returns
        the resulting string.

        Returns:
            str: The canonical path.
        """
        return '/'.join(self.path)

    @property
    def full_path(self) -> str:
        """
        Return the full path of the object.

        Returns:
            str: The full path of the object.
        """
        return '/'.join(chain(self.path, (self.tag, )))

    @classmethod
    def from_tag(cls, tag: Tag) -> 'HTMLTag':
        """
        Constructs an instance of 'HTMLTag' from a given 'Tag' object.

        Args:
            tag: A 'Tag' object representing an HTML tag.

        Returns:
            An instance of 'HTMLTag' with the same name, string, and parents as the given 'Tag' object.
        """
        return cls(str(tag.name), str(tag.string), _get_parents(tag))

    def __lt__(self, other):
        """
        Args:
            other: The object to compare with self.

        Returns:
            True if the path of self is less than the path of the other object, False otherwise.

        """
        return self.path < other.path


def load_html_source(
        html_parser_name: str,
        location: Path | RemoteLocation,
        *,
        predicate: Callable[[HTMLPosition], bool] = everything,
        tokenize: Callable[[str], Sequence[str]] = str.split
) -> Iterable[Sequence[Entry[HTMLPosition, str]]]:
    """
    Load HTML source and yield entries based on specified parameters.

    Args:
        html_parser_name: Name of the HTML parser to be used.
        location: File path or remote location of the HTML source.
        predicate: Callable function to filter HTML positions. Default is set to `everything`.
        tokenize: Callable function to tokenize HTML source. Default is set to `str.split`.

    Returns:
        An iterable of sequences, where each sequence contains an `Entry` object and an HTML position represented by an
        `HTMLPosition` object.
    """
    def _tag_filter(tag_: Tag) -> bool:
        return bool((tag_.string if tag_.string else '').strip()) if tag_ else False

    index_map: dict[Sequence[str], Iterator[int]] = defaultdict(count)

    with TemporaryDirectory() as temp_dir:

        buffer_db: BufferDatabase[HTMLTag] = BufferDatabase[HTMLTag](Path(temp_dir), HTMLTag)

        with location.open('r') as src:
            soup: BeautifulSoup = BeautifulSoup(src.read(), html_parser_name)
            for element in sorted(map(HTMLTag.from_tag, soup.find_all(_tag_filter))):
                buffer_db.add_entry(element.canonical_path, element)

        for path in buffer_db.get_unique_paths():
            yield [
                Entry(position, token)
                for tag in buffer_db.get_all_with_path(path)
                for i, token in enumerate(tokenize(tag.text))
                if predicate(position := HTMLPosition(tag.tag, tuple(tag.path), next(index_map[tag.full_path]), i))
            ]


@dataclass(frozen=True)
class HTMLSourceConfig(SourceConfig[LocalOrRemoteLocation]):
    """
    HTMLSourceConfig class represents the configuration for an XML data source.

    Attributes:
        tokenizer (str): The type of tokenizer to be used for parsing the XML data. Default is 'delimiter'.
        tokenizer_config (dict[str, Any]): Additional configuration for the tokenizer. Default is an empty dictionary.

    """
    html_parser_name: str = 'html.parser'

    @classmethod
    def location_type(cls) -> type[LocalOrRemoteLocation]:
        return LocalOrRemoteLocation



@as_factory('website', load_html_source)
def load_html_source_using(config: HTMLSourceConfig) -> SourceAdapter[LocalOrRemoteLocation, HTMLPosition, str]:
    """
    Loads the HTML source using the provided configuration.

    Args:
        config: An instance of HTMLSourceConfig containing the necessary configuration options.

    Returns:
        A SourceAdapter object with the specified generic types:
            - The source location type is LocalOrRemoteLocation.
            - The position type is HTMLPosition.
            - The return type is str.

    Example usage:

        config = HTMLSourceConfig(html_parser_name='beautifulsoup')
        source_adapter = load_html_source_using(config)

        # You can now use the source_adapter object to perform operations on the HTML source.
    """
    return partial(load_html_source, config.html_parser_name)