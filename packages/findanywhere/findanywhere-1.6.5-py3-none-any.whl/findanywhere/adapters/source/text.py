from collections.abc import Callable, Sequence, Iterable
from dataclasses import dataclass, field
from functools import partial
from operator import attrgetter
from pathlib import Path
from typing import Any

from toolz import compose

from findanywhere.algorithms.strings import tokenize
from findanywhere.ports.source import SourceAdapter, Entry, everything, SourceConfig
from findanywhere.tokeinize import TOKENIZER_FACTORIES
from findanywhere.types.factory import as_factory
from findanywhere.types.tokenize import Tokenizer


@dataclass(frozen=True)
class TextPosition:
    """
    Dataclass representing a position in a text document.

    Attributes:
        line (int): The line number of the position in the text document.
        token (int): The token number within the line of the position in the text document.
    """
    line: int
    token: int


def load_text_source(
        encoding: str,
        errors: str,
        location: Path | str,
        *,
        predicate: Callable[[TextPosition], bool] = everything,
        tokenize: Callable[[str], Sequence[str]] = str.split
) -> Iterable[Sequence[Entry[TextPosition, str]]]:
    """
    Loads a text source from the given location and yields sequences of entries containing the
    text positions and corresponding tokens.

    Args:
        encoding (str): The encoding of the text source.
        errors (str): The error handling strategy for decoding the text source.
        location (Path): The location of the text source file.
        predicate (Callable[[TextPosition], bool], optional): A predicate function used to filter entries.
            Defaults to everything, which allows all entries.
        tokenize (Callable[[str], Sequence[str]], optional): A tokenization function used to tokenize lines of text.
            Defaults to str.split.

    Returns:
        Iterable[Sequence[Entry[TextPosition, str]]]: An iterable that yields sequences of entries. Each entry in the
        sequence contains a TextPosition object representing the position of a token in the text source and the
        corresponding token string.

    """
    with Path(location).open(encoding=encoding, errors=errors) as src:
        for line_no, line in enumerate(src):
            yield tuple(
                filter(
                    compose(predicate, attrgetter('position')),
                    (Entry(TextPosition(line_no, token_no), token) for token_no, token in enumerate(tokenize(line)))
                )
            )


@dataclass(frozen=True)
class TextSourceConfig(SourceConfig[Path]):
    """
    TextSourceConfig class

    This class represents the configuration for a text source.

    Attributes:
        encoding (str): The encoding of the text source. Default is 'utf-8'.
        errors (str): The error handling scheme for decoding the text source. Default is 'surrogateescape'.
    """
    encoding: str = 'utf-8'
    errors: str = 'surrogateescape'

    @classmethod
    def location_type(cls) -> type[Path]:
        return Path


@as_factory('textfile', load_text_source)
def load_text_source_using(config: TextSourceConfig) -> SourceAdapter[Path, TextPosition, str]:
    """
    Args:
        config: The configuration object that contains various parameters for loading the text source.

    Returns:
        SourceAdapter[Path, TextPosition, str]: The source adapter that can be used to load and process the text source.

    Raises:
        None
    """
    tokenizer: Tokenizer = config.get_tokenizer()
    return partial(load_text_source, config.encoding, config.errors, tokenize=tokenizer)