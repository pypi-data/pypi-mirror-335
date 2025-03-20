"""
This module contains the core search functionality of the application.
It provides two key functions: `search` and `buffered_search`.

`search` is a generic function that evaluates input data against a set of entries
using the provided evaluation and scoring mechanisms. It filters the results based on a threshold filter.

`buffered_search` function performs a search, using an instance of the `search` function,
on the provided input data and entries. The results are stored in a buffer file created
in the specified directory. The buffer file contains the search results in a JSON line
format (each search result is a separate JSON object).

Together, these functions enable flexible and efficient searching within the context of the application.
"""

from collections.abc import Sequence, Iterable
from dataclasses import asdict
from json import dump
from pathlib import Path
from typing import Protocol, Any
from uuid import uuid4

from findanywhere.ports.evaluation import EvaluationAdapter, Position
from findanywhere.types.entry import Entry
from findanywhere.types.input_data import InputData, DataType
from findanywhere.types.similarity import DeduceScore, ThresholdFilter, ScoredEvaluation


def search(
        evaluate: EvaluationAdapter[DataType],
        deduce_score: DeduceScore[Position, DataType],
        threshold: ThresholdFilter[Position, DataType],
        input_data: Sequence[InputData[DataType]],
        entries: Sequence[Entry[Position, DataType]]
) -> Iterable[ScoredEvaluation[Position, DataType]]:
    """
    Evaluates the input data against a set of entries using the provided evaluation and scoring mechanisms,
    and filters the results based on a threshold filter. The function is generic and can work in different contexts
    matching/searching tasks.

    Args:
        evaluate: An instance of EvaluationAdapter[DataType], used to evaluate the search data against the entries.
        deduce_score: An instance of DeduceScore[Position, DataType], used to calculate the score based on the search
        data evaluation.
        threshold: An instance of ThresholdFilter[Position, DataType], used to filter the scored evaluations based on a
        threshold.
        input_data: A sequence of InputData[DataType] objects, representing the search data for which evaluations need
        to be generated.
        entries: A sequence of Entry[Position, DataType] objects, representing the entries against which the search data
        is evaluated.

    Returns:
        An iterable of ScoredEvaluation[Position, DataType] objects, containing the scored evaluations that pass the
        threshold filter.

    """
    for search_data in input_data:
        scored_evaluation: ScoredEvaluation[Position, DataType] = deduce_score(evaluate(search_data, entries))
        if threshold(scored_evaluation):
            yield scored_evaluation


class Search(Protocol[Position, DataType]):
    """
    A generic class representing a search algorithm.
    """

    def __call__(
            self,
            input_data: Sequence[InputData[DataType]],
            entries: Sequence[Entry[Position, DataType]]
    ) -> Iterable[ScoredEvaluation[Position, DataType]]:
        """
        Args:
            input_data: A sequence of InputData objects representing the input data for evaluation.
            entries: A sequence of Entry objects representing the entries to be evaluated.

        Returns:
            An iterable of ScoredEvaluation objects representing the evaluation results.
        """
        ...


class SearchPattern(Protocol[Position, DataType]):
    """
    A class representing a search pattern.

    The SearchPattern class is a callable protocol that defines the behavior of a search pattern. It takes in input data
    , a search algorithm, and a set of entries to evaluate. It returns an iterable of scored
    evaluations or dictionaries.

    """

    def __call__(
            self,
            input_data: Sequence[InputData[DataType]],
            search_: Search[Position, DataType],
            entries: Iterable[Sequence[Entry[Position, DataType]]]
    ) -> Iterable[ScoredEvaluation[Position, DataType] | dict[str, Any]]:
        """
        Args:
            input_data: A sequence of InputData objects, representing the input data to be evaluated.
            search_: A Search object, representing the search algorithm to be used.
            entries: An iterable of sequences of Entry objects, representing the entries to be evaluated.

        Returns:
            An iterable of ScoredEvaluation objects or dictionaries. Each ScoredEvaluation object represents the result
            of evaluating an entry and contains the position and data type scores. Each dictionary represents the result
             of evaluating an entry and contains additional information.
        """
        ...


def buffered_search(
        search_: Search[Position, DataType],
        directory: Path,
        input_data: Sequence[InputData[DataType]],
        entries: Sequence[Entry[Position, DataType]]
) -> Path:
    """
    Performs a search using an instance of the `Search` class on the provided input data and entries.
    The results are written to a buffer file in JSON line format (each search result is a separate JSON object).
    The buffer file is created in the specified directory.

    Args:
        search_: An instance of the Search class that takes Position and DataType as type parameters.
        directory: The directory where the buffer file will be created.
        input_data: A sequence of InputData objects that contain the input data for the search.
        entries: A sequence of Entry objects that define the entries for the search.

    Returns:
        Path: The path to the created buffer file.

    """
    buffer_file: Path = directory.joinpath(f'{uuid4()}.json_line')
    with buffer_file.open('w', encoding='utf-8', errors='surrogateescape') as out:
        for result in search_(input_data, entries):
            dump(asdict(result), out)
            out.write('\n')
    return buffer_file
