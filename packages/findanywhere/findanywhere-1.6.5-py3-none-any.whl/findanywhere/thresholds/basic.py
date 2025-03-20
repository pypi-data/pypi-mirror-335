from dataclasses import dataclass
from functools import partial

from findanywhere.types.entry import Position, DataType
from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import ScoredEvaluation, ThresholdFilter


def no_threshold(evaluation: ScoredEvaluation[Position, DataType]) -> bool:
    """
    Args:
        evaluation: A scored evaluation of a position with some data type.

    Returns:
        bool: Always returns True.
    """
    return True


def constant_threshold(constant: float, evaluation: ScoredEvaluation[Position, DataType]) -> bool:
    """
    Args:
        constant: A float representing the threshold value.
        evaluation: A ScoredEvaluation object containing the score to be evaluated.

    Returns:
        A boolean value indicating whether the score is greater than or equal to the constant threshold.
    """
    return evaluation.score >= constant


@as_factory('no', using=no_threshold)
def no_threshold_using(config: Config) -> ThresholdFilter:
    """
    Create a `no_threshold_using` method that uses the `no_threshold` method to create a `ThresholdFilter` object.

    Args:
        config: A `Config` object that provides the necessary configuration for creating the `ThresholdFilter` object.

    Returns:
        A `ThresholdFilter` object created using the `no_threshold` method.

    """
    return no_threshold


@dataclass(frozen=True)
class ConstantThresholdConfig(Config):
    """

    The `ConstantThresholdConfig` class represents a configuration for a constant threshold used in a system.
    It is a subclass of the `Config` class.

    Attributes:
        constant (float): The value of the constant threshold.

    """
    constant: float | str = 0.8


@as_factory('constant', using=constant_threshold)
def constant_threshold_using(config: ConstantThresholdConfig) -> ThresholdFilter:
    """Apply a constant threshold using the specified configuration.

    Args:
        config: The configuration for the constant threshold.

    Returns:
        A partial function that applies the constant threshold filter.

    """
    return partial(constant_threshold, float(config.constant))
