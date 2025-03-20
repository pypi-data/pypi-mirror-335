from collections.abc import Callable, Sequence

from findanywhere.similarity.common import inverted_levenshtein_distance_with, jaro_winkler_similarity_with
from findanywhere.similarity.token import token_best_fit_similarity_with, token_best_fit_mulit_separator_similarity_with
from findanywhere.similarity.rest import rest_endpoint_similarity, rest_endpoint_similarity_with
from findanywhere.types.factory import FactoryMap, Factory, Config
from findanywhere.types.similarity import Similarity


SIMILARITY_FACTORIES: FactoryMap[Similarity[str]] = FactoryMap[Similarity[str]](
    [
        inverted_levenshtein_distance_with, jaro_winkler_similarity_with,
        token_best_fit_similarity_with, token_best_fit_mulit_separator_similarity_with,
        rest_endpoint_similarity_with
    ]
)


_AGGREGATES: dict[str, Callable[[Sequence[float]], float]] = dict(
    (func.__name__, func)
    for func in (max, min)
)


def get_similarity_factory(name: str) -> Factory[Similarity, Config]:
    return SIMILARITY_FACTORIES[name]



def get_aggregate_by_name(name: str) -> Callable[[Sequence[float]], float]:
    return _AGGREGATES[name]