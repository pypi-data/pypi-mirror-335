from operator import attrgetter

from findanywhere.ports.source import Position
from findanywhere.types.entry import DataType
from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import Evaluation, ScoredEvaluation, DeduceScore


def average_score(evaluation: Evaluation[Position, DataType]) -> ScoredEvaluation[Position, DataType]:
    """
    Calculate the average score of an evaluation.

    Args:
        evaluation: An Evaluation object containing the best matches and their similarities.

    Returns:
        A ScoredEvaluation object with the original evaluation, best matches, and the average score.
    """
    score_sum: float = sum(map(attrgetter('similarity'), evaluation.best_matches.values()))
    score: float = score_sum / len(evaluation.best_matches) if evaluation.best_matches else 0.0
    return ScoredEvaluation(evaluation.of, evaluation.best_matches, score)


def maximum_score(evaluation: Evaluation[Position, DataType]) -> ScoredEvaluation[Position, DataType]:
    """
    Args:
        evaluation: An Evaluation object containing the results of a scoring operation.

    Returns:
        A ScoredEvaluation object, which includes the best matches and the maximum similarity score among them.
    """
    return ScoredEvaluation(
        evaluation.of, evaluation.best_matches, max(map(attrgetter('similarity'), evaluation.best_matches.values()))
    )


@as_factory('average', using=average_score)
def create_average_score(config: Config) -> DeduceScore[Position, DataType]:
    """
    Args:
        config: The configuration object that contains the necessary information to create the average score.

    Returns:
        An instance of the DeduceScore class with the average_score function as the implementation.

    Raises:
        None
    """
    return average_score


@as_factory('maximum', using=maximum_score)
def create_maximum_score(config: Config) -> DeduceScore[Position, DataType]:
    """
    Args:
        config: The configuration object that contains the necessary parameters for creating the maximum score.

    Returns:
        The maximum score created based on the provided configuration.

    """
    return maximum_score
