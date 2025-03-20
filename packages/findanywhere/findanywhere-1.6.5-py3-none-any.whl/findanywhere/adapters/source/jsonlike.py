from collections.abc import Sequence, Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from itertools import groupby
from json import load
from operator import attrgetter
from pathlib import Path
from typing import TextIO, Any

from yaml import safe_load

from findanywhere.algorithms.jsonlike import traverse_jsonlike, JSONFragment
from findanywhere.ports.source import everything, SourceConfig, SourceAdapter
from findanywhere.tokeinize import TOKENIZER_FACTORIES
from findanywhere.types.common import JSONType
from findanywhere.types.entry import Entry
from findanywhere.types.factory import as_factory
from findanywhere.types.tokenize import Tokenizer


@dataclass(frozen=True)
class JSONPosition:
    """
    Class representing a JSON position within a JSON object or array.

    Attributes:
        path (Sequence[str | int]): The sequence of keys or indices that make up the path to a JSON value.
    """
    path: Sequence[str | int]
    token: int


def _json_str_value(value: JSONType) -> str:
    return str(value) if value is not None else ''


def load_jsonlike_source(
        loader: Callable[[TextIO], JSONType],
        encoding: str,
        errors: str,
        location: Path | str,
        *,
        predicate: Callable[[JSONPosition], bool] = everything,
        tokenize: Callable[[str], Sequence[str]] = str.split
) -> Iterable[Sequence[Entry[JSONPosition, str]]]:
    """
    Args:
        loader: A callable that takes a TextIO object and returns a JSONType object.
        encoding: The encoding to use when reading the source file.
        errors: The error handling scheme to use when decoding the source file.
        location: The path to the source file.
        predicate: An optional callable that takes a JSONPosition object and returns a boolean.
                   Defaults to the function "everything".
        tokenize: An optional callable that takes a string and returns a sequence of strings. Defaults to the function
                  "str.split".

    Returns:
        An iterable of sequences containing Entry objects, where each Entry object represents a token in the source
        file. The sequences correspond to fragments of the JSON-like structure in the source file.

    Raises:
        FileNotFoundError: If the specified source file does not exist.
        PermissionError: If the specified source file cannot be opened due to insufficient permissions.
        UnicodeDecodeError: If the source file cannot be decoded using the specified encoding and error handling scheme.
        Any other exceptions raised by the loader function.
    """
    with Path(location).open(encoding=encoding, errors=errors) as src:
        fragments: Sequence[JSONFragment] = sorted(traverse_jsonlike(loader(src)), key=attrgetter('parent'))
        for parent, elements in groupby(fragments, key=attrgetter('parent')):
            yield tuple(
                Entry(position, token)
                for element in elements
                for token_no, token in enumerate(tokenize(_json_str_value(element.value)))
                if predicate(position := JSONPosition(element.path, token_no))
            )


class JSONLikeFormat(Enum):
    """
    Describes the possible formats for storing and representing data, specifically in JSON-like formats.

    Attributes:
        JSON (str): The JSON format.
        YAML (str): The YAML format.
        JSON_LINE (str): The JSON Line format.
    """
    JSON = 'json'
    YAML = 'yaml'
    JSON_LINE = 'json_line'


@dataclass(frozen=True)
class JSONLikeSourceConfig(SourceConfig[Path]):
    """
    Class representing a configuration for a source using a JSON-like format.

    Attributes:
        file_format (JSONLikeFormat): The file format of the source. Default is JSON.
        encoding (str): The encoding used for reading the source file. Default is 'utf-8'.
        errors (str): The error handling scheme used when decoding the source file. Default is 'surrogateescape'.
        tokenizer (str): The tokenizer type used for parsing the source file. Default is 'delimiter'.
        tokenizer_config (dict[str, Any]): The configuration options for the tokenizer. Default is an empty dictionary.

    Methods:
        location_type() -> type[Path]: Returns the data type used for representing the location of the source file.

    """
    file_format: JSONLikeFormat = JSONLikeFormat.JSON
    encoding: str = 'utf-8'
    errors: str = 'surrogateescape'

    @classmethod
    def location_type(cls) -> type[Path]:
        return Path


@as_factory('jsonlike', load_jsonlike_source)
def load_jsonlike_source_using(config: JSONLikeSourceConfig) -> SourceAdapter[Path, JSONPosition, str]:
    """
    Load a JSON-like source using the provided configuration.

    Args:
        config: The configuration object specifying the source parameters.

    Returns:
        A SourceAdapter object that can be used to interact with the JSON-like source.

    Raises:
        AttributeError: If an unsupported file format is specified in the configuration.
    """
    tokenizer: Tokenizer = config.get_tokenizer()
    match config.file_format:
        case JSONLikeFormat.JSON:
            loader: Callable[[TextIO], JSONType] = load
        case JSONLikeFormat.YAML:
            loader = safe_load
        case _: raise AttributeError(f'Unsupported file format {config.file_format}')

    return partial(load_jsonlike_source, loader, config.encoding, config.errors, tokenize=tokenizer)









