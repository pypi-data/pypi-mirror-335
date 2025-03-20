from collections.abc import Sequence, Callable, Iterable
from dataclasses import replace, dataclass, field
from operator import attrgetter
from typing import Protocol, TypeAlias, TypeVar, Any

from findanywhere.ports.source import Position, DataType, Entry
from findanywhere.similarity import SIMILARITY_FACTORIES
from findanywhere.types.factory import Config
from findanywhere.types.input_data import InputData
from findanywhere.types.similarity import Evaluation, ScoredEntry, Similarity

_T = TypeVar('_T')


class EvaluationPort(Protocol[DataType]):
    """
    Class representing an evaluation port.

    Usage:
        An EvaluationPort is used to perform evaluations on a set of data entries against a reference.
    """
    def __call__(
            self,
            reference: InputData[DataType],
            entries: Sequence[Entry[Position, DataType]]
    ) -> Evaluation[Position, DataType]:
        """
        Args:
            reference: InputData[DataType]. The reference data used for evaluation.
            entries: Sequence[Entry[Position, DataType]]. The data entries to be evaluated against the reference.

        Returns:
            Evaluation[Position, DataType]. The result of the evaluation."""
        ...


EvaluationAdapter: TypeAlias = EvaluationPort


def get_best_with(
        aggregate: Callable[[Sequence[float]], float],
        scored_fields: Iterable[ScoredEntry[Position, DataType]]
) -> ScoredEntry[Position, DataType]:
    """Get the entry with the highest similarity score, aggregated using the given aggregate function.

    Args:
        aggregate: The aggregate function used to calculate the aggregated similarity score. It takes a sequence of
        floats and returns a single float.
        scored_fields: An iterable of ScoredEntry objects, each representing a field along with its similarity score.

    Returns:
        The ScoredEntry object with the highest similarity score, where the similarity score has been replaced with the
        aggregated similarity score.
    """
    scored_fields = tuple(scored_fields)
    aggregated_similarity: float = aggregate(list(map(attrgetter('similarity'), scored_fields)))
    return replace(max(scored_fields, key=attrgetter('similarity')), similarity=aggregated_similarity)


@dataclass(frozen=True)
class EvaluationConfig(Config):
    similarity: Similarity | str = 'jaro_winkler'
    similarity_config: dict[str, Any] = field(default_factory=dict)

    def get_similarity(self) -> Similarity:
        if isinstance(self.similarity, str):
            return SIMILARITY_FACTORIES[self.similarity].from_dict(self.similarity_config)
        if isinstance(self.similarity, Similarity):
            return self.similarity
        raise TypeError(f'Not a similarity or similarity name: {self.similarity}')



