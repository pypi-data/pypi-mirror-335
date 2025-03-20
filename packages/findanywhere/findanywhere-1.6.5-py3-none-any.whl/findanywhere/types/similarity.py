from dataclasses import dataclass
from typing import TypeVar, Protocol, Generic, runtime_checkable

from findanywhere.types.entry import Entry, Position, DataType
from findanywhere.types.input_data import InputID

_T = TypeVar('_T', contravariant=True)


@runtime_checkable
class Similarity(Protocol[_T]):
    """
    Function that calculates the similarity of two values. Higher values indicate more similar values. Usually
    similarity ratings range from 0 to 1, but other ratings are possible, too.
    """

    def __call__(self, left: _T, right: _T) -> float:
        ...


@dataclass(frozen=True)
class ScoredEntry(Entry[Position, DataType]):
    """
    Represents a scored entry with a similarity value.

    Attributes:
        similarity (float): The similarity value of the scored entry.

    """
    similarity: float


@dataclass(frozen=True)
class Evaluation(Generic[Position, DataType]):
    """

    Evaluation Class

    A class representing the evaluation of a specific input.

    Attributes:
        of (InputID): The ID of the input being evaluated.
        best_matches (dict[str, ScoredEntry]): A dictionary containing the best matches for each position.

    """
    of: InputID
    best_matches: dict[str, ScoredEntry[Position, DataType]]


@dataclass(frozen=True)
class ScoredEvaluation(Evaluation[Position, DataType]):
    """
    Class representing a scored evaluation.

    Attributes:
        score (float): The score of the evaluation.

    """
    score: float


class DeduceScore(Protocol[Position, DataType]):
    """

    This class represents a function-like object that takes an evaluation object and returns a scored evaluation object.

    Methods:
        __call__: Executes the function-like object.

    """
    def __call__(self, evaluation: Evaluation[Position, DataType]) -> ScoredEvaluation[Position, DataType]:
        """
        Args:
            evaluation: An instance of the Evaluation class with generic types `Position` and `DataType`. It represents
            the evaluation result.

        Returns:
            An instance of the ScoredEvaluation class with generic types `Position` and `DataType`. It represents the
            scored evaluation result.
        """
        ...


class ThresholdFilter(Protocol[Position, DataType]):
    """

    This class represents a filter that determines whether a scored evaluation passes a threshold.
    """
    def __call__(self, evaluation: ScoredEvaluation[Position, DataType]) -> bool:
        """
        Args:
            evaluation: The scored evaluation of the position with its data type.

        Returns:
            bool: True if the method is called successfully, False otherwise.
        """
        ...