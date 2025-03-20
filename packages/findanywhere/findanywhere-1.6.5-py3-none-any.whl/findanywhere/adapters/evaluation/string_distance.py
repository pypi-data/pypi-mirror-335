from collections.abc import Sequence, Callable
from dataclasses import dataclass, field
from functools import partial
from itertools import product, groupby
from operator import itemgetter
from typing import Any

from jellyfish import jaro_winkler_similarity

from findanywhere.ports.evaluation import InputData, Evaluation, ScoredEntry, get_best_with, EvaluationAdapter, \
    EvaluationConfig
from findanywhere.ports.source import Position, Entry
from findanywhere.similarity import get_similarity_factory, get_aggregate_by_name
from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import Similarity


def evaluate_by_similarity(
        similarity: Similarity[str] | Callable[[str, str], float],
        aggregate: Callable[[Sequence[float]], float],
        reference: InputData[str],
        entries: Sequence[Entry[Position, str]]
) -> Evaluation[Position, str]:
    """
    Args:
        similarity: A similarity function or object of type Similarity[str] which measures the similarity between two
                    strings.
        aggregate: A function that takes a sequence of floats and returns a single float. It is used to aggregate
                   similarity scores.
        reference: An object of type InputData[str] which represents the reference data used for evaluation.
        entries: A sequence of Entry[Position, str] objects representing the entries to be evaluated.

    Returns:
        An object of type Evaluation[Position, str] which contains the evaluation results.

    """

    scores: list[tuple[str, ScoredEntry[Position, str]]] = sorted(
        (
            (field_, ScoredEntry(entry.position, entry.value, similarity(value, entry.value)))
            for (field_, value), entry in product(reference.fields.items(), entries)), key=itemgetter(0)
    )
    return Evaluation(reference.id, dict(
        (field_, get_best_with(aggregate, map(itemgetter(1), field_scores))) for field_, field_scores in
        groupby(scores, key=itemgetter(0))))


evaluate_by_similarity_default: EvaluationAdapter[str] = partial(
    evaluate_by_similarity, jaro_winkler_similarity, max
)

@dataclass(frozen=True)
class StringBasedEvaluationConfig(EvaluationConfig):
    """

    StringBasedEvaluationConfig

    This class represents a configuration for string-based evaluation.

    Attributes:
        aggregate (str): The aggregation operation to use for multiple similarity scores. Default is 'max'.

    """
    aggregate: str = 'max'


@as_factory('string_based_evaluation', using=evaluate_by_similarity)
def evaluate_by_similarity_using(config: StringBasedEvaluationConfig) -> EvaluationAdapter[str]:
    """
    Evaluates similarity using a given configuration.

    Args:
        config: The configuration for the string-based evaluation.

    Returns:
        An EvaluationAdapter that can be used to evaluate similarity.

    """
    return partial(
        evaluate_by_similarity,
        config.get_similarity(),
        get_aggregate_by_name(str(config.aggregate))
    )