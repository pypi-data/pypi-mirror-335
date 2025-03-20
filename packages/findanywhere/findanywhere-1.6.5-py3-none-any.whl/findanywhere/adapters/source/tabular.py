from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from csv import DictReader, field_size_limit
from functools import partial
from pathlib import Path
from sys import maxsize
from typing import Literal

from findanywhere.ports.source import SourceAdapter, SourceConfig
from findanywhere.types.entry import Entry
from findanywhere.types.factory import as_factory


@dataclass(frozen=True)
class TablePosition:
    """

    TablePosition represents the position of a table in a document.

    Attributes:
        line (int): The line number of the table.
        column (str): The column letter of the table.

    """
    line: int
    column: str


def _handle_extra_columns(items: Iterable[tuple[str | None, str | list[str]]]) -> Iterable[tuple[str, str]]:
    extra_column_count: int = 1
    for column, value in items:
        if isinstance(value, list):
            for extra_value in value:
                yield f'_extra_column_{extra_column_count}', extra_value
                extra_column_count += 1
        else:
            yield str(column), value



def load_tabular_source(
    encoding: str,
    errors: str,
    delimiter: str,
    large_fields: bool,
    location: Path
) -> Iterable[Sequence[Entry[TablePosition, str]]]:
    """
    Args:
        encoding: A string representing the encoding of the file to be opened.
        errors: A string representing how decoding errors should be handled. Default is 'strict'.
        delimiter: A string representing the delimiter used to separate values in the file.
                   Tabs can be used by specifying *@tab* as delimiter.
        large_fields: Indicates that the file contains fields that are larger than the maximum default size.
        location: A `Path` object representing the location of the file to be opened.

    Returns:
        An iterable containing sequences of `Entry[TablePosition, str]` objects.

    Raises:
        FileNotFoundError: If the file at the specified `location` does not exist.
        PermissionError: If the file at the specified `location` cannot be opened due to insufficient permissions.

    """
    if delimiter == '@tab':
        delimiter = '\t'
    if large_fields:
        field_size_limit(maxsize)

    with Path(location).open(encoding=encoding, errors=errors) as src:
        reader: DictReader = DictReader(src, delimiter=delimiter)
        for line_no, row in enumerate(reader):
            yield tuple(
                Entry[TablePosition, str](TablePosition(line_no, column), value)
                for column, value in _handle_extra_columns(row.items())
            )


@dataclass(frozen=True)
class TabularSourceConfig(SourceConfig[Path]):
    """
    TabularSourceConfig class is a configuration class for tabular data sources.

    Attributes:
        encoding (str): The encoding used to read the tabular data. Default is 'utf-8'.
        errors (str): The error handling strategy used when decoding the tabular data. Default is 'surrogateescape'.
        delimiter (str): The delimiter character used to separate values in the tabular data. Default is ','.
    """
    encoding: str = 'utf-8'
    errors: str = 'surrogateescape'
    delimiter: str = ','
    large_fields: bool = True

    @classmethod
    def location_type(cls) -> type[Path]:
        return Path


@as_factory(
    'tabular',
    load_tabular_source
)
def load_tabular_source_using(config: TabularSourceConfig) -> SourceAdapter[Path, TablePosition, str]:
    """
    Load tabular source using the given configuration.

    Args:
        config (TabularSourceConfig): The configuration for loading the tabular source.

    Returns:
        SourceAdapter[Path, TablePosition, str]: A source adapter for loading tabular source.
    """
    return partial(load_tabular_source, config.encoding, config.errors, config.delimiter, config.large_fields)