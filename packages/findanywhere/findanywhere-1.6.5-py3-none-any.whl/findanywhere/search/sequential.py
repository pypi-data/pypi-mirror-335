from collections.abc import Sequence, Iterable
from dataclasses import asdict
from typing import Any

from findanywhere.search.base import Search
from findanywhere.types.entry import Entry
from findanywhere.types.input_data import InputData, DataType, Position


def sequential_search(
    input_data: Sequence[InputData[DataType]],
    search_: Search[Position, DataType],
    entries: Iterable[Sequence[Entry[Position, DataType]]],
) -> Iterable[dict[str, Any]]:
    """
    Perform sequential search on the given input data using the specified search algorithm.

    Unlike parallel search, this function processes the input data and entries sequentially,
    which could be better for small data sets or for systems with single or limited processor cores.

    Args:
        input_data: A sequence of InputData objects containing data of a specific type.
        search_: A search function that takes input_data and an entry as parameters and returns a sequence of matches.
        entries: An iterable of sequences of Entry objects containing positions and data to search for.

    Returns:
        An iterable of dictionaries, where each dictionary represents a match found by the search function. The
        dictionaries contain attributes and values corresponding to the matched Entry objects.

    """
    for entry in entries:
        for result in map(asdict, search_(input_data, entry)):
            yield result
