from collections.abc import Sequence, Iterable
from functools import partial
from json import loads
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from findanywhere.ports.source import Position, DataType
from findanywhere.search.base import Search, buffered_search
from findanywhere.types.entry import Entry
from findanywhere.types.input_data import InputData


def parallel_search(
        input_data: Sequence[InputData[DataType]],
        search_: Search[Position, DataType],
        entries: Iterable[Sequence[Entry[Position, DataType]]],
        processes: int = cpu_count(),
        chunk_size: int = 1000,
) -> Iterable[dict[str, Any]]:
    """
    Performs parallel search on given input data using a specified search algorithm, and
    outputs the result in chunks. This function is useful for large datasets where searching
    needs to be distributed among multiple processor cores for optimized performance.

    Args:
        input_data (Sequence[InputData[DataType]]): The input data sequence to perform the search on.
        search_ (Search[Position, DataType]): The search algorithm to use.
        entries (Iterable[Sequence[Entry[Position, DataType]]]): An iterable of entries to search from.
        processes (int, optional): The number of worker processes to use. If not provided,
                        it defaults to the number of processors on the machine.
        chunk_size (int, optional): The number of tasks each worker process will be assigned at one time.
                        Large chunk sizes are more efficient for large tasks (due to reduced overhead),
                        but can lead to imbalanced workloads. The default value is 1000.

    Returns:
        Iterable[dict[str, Any]]: An iterable of the results.
    """
    with Pool(processes) as pool:
        with TemporaryDirectory() as temp_dir:
            buffer_dir: Path = Path(temp_dir)
            for result_file in pool.imap_unordered(
                    partial(buffered_search, search_, buffer_dir, input_data),
                    entries,
                    chunksize=chunk_size
            ):
                with result_file.open(encoding='utf-8', errors='surrogateescape') as src:
                    for result in map(loads, src):
                        yield result
