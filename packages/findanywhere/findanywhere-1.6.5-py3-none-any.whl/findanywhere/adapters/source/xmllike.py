from collections import defaultdict, deque
from collections.abc import Callable, Sequence, Iterable, Iterator
from dataclasses import dataclass, field
from functools import partial
from itertools import count
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast
from xml.sax import parse, ContentHandler


from findanywhere.ports.source import everything, SourceConfig, SourceAdapter, Location
from findanywhere.tokeinize import TOKENIZER_FACTORIES
from findanywhere.types.entry import Entry
from findanywhere.types.factory import as_factory
from findanywhere.types.tokenize import Tokenizer
from findanywhere.utils.buffer_database import BufferDatabase


@dataclass(frozen=True)
class XMLPosition:
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


@dataclass(frozen=True)
class XMLTag:
    """
    A class representing an XML tag.

    Attributes:
        tag (str): The name of the XML tag.
        text (Sequence[str]): The text contents of the XML tag.
        path (Sequence[str]): The path to the XML tag.

    Properties:
        normalized_path (str): The normalized path to the XML tag, with tabs separating each level.
        normalized_text (str): The normalized text contents of the XML tag, with whitespace stripped and multiple
                               spaces collapsed into a single space.

    """
    tag: str
    text: Sequence[str] = field(default_factory=list)
    path: Sequence[str] = field(default_factory=list)

    @property
    def normalized_path(self) -> str:
        """
        Returns a string representation of the normalized path.

        Returns:
            str: The normalized path joined by tabs.
        """
        return '\t'.join(self.path)

    @property
    def normalized_text(self) -> str:
        """
        Returns the normalized text of the given text.

        This method takes in a string or list of strings as input and returns the normalized text. The normalized text
        is obtained by removing leading and trailing whitespaces from each element in the input, filtering out empty
        elements, and then joining the remaining elements with a single whitespace between them.
        """
        return ' '.join(filter(bool, map(str.strip, self.text)))


class _CallbackContentHandler(ContentHandler):
    """
    Class representing a callback content handler for XML parsing.

    This class extends the `ContentHandler` class provided by the `xml.sax` module.
    It processes XML elements and their content and invokes a callback function for each element.

    Attributes:
        _callback (Callable[[XMLTag], None]): The callback function to be invoked for each XML element.
        _element_stack (deque[str]): A stack of XML element names.
        _text (list[str]): A list of text content within XML elements.
        _attributes (dict[str, Any]): A dictionary of XML attributes for the current element.

    Methods:
        startElement(name, attrs): Method invoked at the start of an XML element.
        startElementNS(name, qname, attrs): Method invoked at the start of a namespaced XML element.
        endElement(name): Method invoked at the end of an XML element.
        endElementNS(name, qname): Method invoked at the end of a namespaced XML element.
        characters(content): Method invoked for XML character data within an element.
    """
    def __init__(self, callback: Callable[[XMLTag], None], include_attributes: bool = True):
        super().__init__()
        self._callback: Callable[[XMLTag], None] = callback
        self._element_stack: deque[str] = deque()
        self._text: list[str] = list()
        self._attributes: dict[str, Any] = dict()
        self._include_attributes: bool = include_attributes

    def startElement(self, name, attrs) -> None:
        """
        Args:
            name: str - The name of the element.

            attrs: dict - The attributes of the element.

        """
        return self._handle_start(name, attrs)

    def startElementNS(self, name, qname, attrs) -> None:
        """
        Args:
            name: A string representing the name of the element.
            qname: A string representing the qualified name of the element.
            attrs: A dictionary containing the attributes of the element.

        """
        return self._handle_start(qname, attrs)

    def endElement(self, name) -> None:
        """
        Args:
            name: The name of the XML element that has ended.

        """
        return self._handle_end(name)

    def endElementNS(self, name, qname) -> None:
        """
        Args:
            name: The name of the XML namespace-qualified element that is ending.
            qname: The fully qualified name of the XML element that is ending.

        """
        return self._handle_end(qname)


    def _handle_start(self, name, attrs) -> None:
        self._element_stack.append(name)
        path: Sequence[str] = tuple(self._element_stack)
        if self._include_attributes:
            for key, value in attrs.items():
                self._callback(XMLTag(f'{key}@{name}', [str(value)], path))



    def _handle_end(self, name) -> None:
        relevant_text: Sequence[str] = tuple(filter(bool, map(str.strip, self._text)))
        tag: str = self._element_stack.pop()
        path: Sequence[str] = tuple(self._element_stack)
        self._callback(XMLTag(tag, relevant_text, path))
        self._text.clear()

    def characters(self, content) -> None:
        """
        Args:
            content: The content to be added to the list of characters in the object.

        """
        self._text.append(content)


def load_xml_source(
        include_attributes: bool,
        location: Path,
        *,
        predicate: Callable[[XMLPosition], bool] = everything,
        tokenize: Tokenizer = cast(Tokenizer, str.split)
) -> Iterable[Sequence[Entry[XMLPosition, str]]]:
    """
    Args:
        include_attributes: Indicates if text in attributes is to be extracted.
        location: The location of the XML file to load.
        predicate: A function that takes an XMLPosition object as input and returns a boolean value indicating whether
                  the position meets certain conditions. Default is 'everything', which returns True for all positions.
        tokenize: A function that takes a string as input and returns a sequence of tokens. Default is 'str.split',
                  which splits the string into tokens using whitespace as the delimiter.

    Returns:
        An iterable of sequences of Entry objects, where each Entry object contains an XMLPosition object and a string
        token.
    """
    with location.open('rb') as src:
        with TemporaryDirectory() as temp_dir:
            buffer: BufferDatabase[XMLTag] = BufferDatabase[XMLTag](Path(temp_dir), XMLTag)

            def _log_result(result: XMLTag) -> None:
                buffer.add_entry(result.normalized_path, result)

            parse(src, _CallbackContentHandler(_log_result, include_attributes))

            for path in buffer.get_unique_paths():
                tags: Sequence[XMLTag] = buffer.get_all_with_path(path)
                tag_indices: dict[str, Iterator[int]] = defaultdict(count)
                results: list[Entry[XMLPosition, str]] = list()
                for tag in tags:
                    tag_index: int = next(tag_indices[tag.tag])
                    for i, token in enumerate(tokenize(tag.normalized_text)):
                        position: XMLPosition = XMLPosition(tag.tag.lower(), tag.path, tag_index, i)
                        if predicate(position):
                            results.append(Entry[XMLPosition, str](position, token))
                if results:
                    yield tuple(results)
                    results.clear()


@dataclass(frozen=True)
class XMLSourceConfig(SourceConfig[Path]):
    """
    XMLSourceConfig class represents the configuration for an XML data source.

    Attributes:
        tokenizer (str): The type of tokenizer to be used for parsing the XML data. Default is 'delimiter'.
        tokenizer_config (dict[str, Any]): Additional configuration for the tokenizer. Default is an empty dictionary.

    """
    include_attributes: bool = True

    @classmethod
    def location_type(cls) -> type[Path]:
        return Path


@as_factory('xmlfile', load_xml_source)
def load_xml_source_using(config: XMLSourceConfig) -> SourceAdapter[Path, XMLPosition, str]:
    """
    Args:
        config: The configuration object for loading XML source data.

    Returns:
        An instance of `SourceAdapter` with the following type parameters:
            - `Path`: The type representing file paths.
            - `XMLPosition`: The type representing XML positions.
            - `str`: The type representing XML source data.

    """
    return partial(load_xml_source, config.include_attributes, tokenize=config.get_tokenizer())
