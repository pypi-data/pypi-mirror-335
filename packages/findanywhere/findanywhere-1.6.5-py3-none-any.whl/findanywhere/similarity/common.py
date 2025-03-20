from jellyfish import jaro_winkler_similarity, levenshtein_distance

from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import Similarity


def jaro_winkler(left: str, right: str) -> float:
    """
    Jaro-Winkler Similarity using the parameters and implementation of the library jellyfish

    Args:
        left: String to search
        right: String to compare

    Returns:
        Value from [0.0, 1.0] with higher values indicating higher similarities.
    """
    return jaro_winkler_similarity(left, right)


@as_factory('jaro_winkler', using=jaro_winkler)
def jaro_winkler_similarity_with(config: Config) -> Similarity[str]:
    """
    Args:
        config: The configuration object that contains the necessary information for calculating Jaro-Winkler
        similarity.

    Returns:
        Similarity[str]: The calculated Jaro-Winkler similarity between two strings.

    """
    return jaro_winkler


def inverted_levenshtein_distance(left: str, right: str) -> float:
    """
    Negative Levenshtein Distance.

    Args:
        left: String to search
        right: String to compare

    Returns:
        Value from ]-infinity, 0.0] with higher values indicating higher similarities.
    """
    return levenshtein_distance(left, right) * -1


@as_factory('inverted_levenshtein', using=inverted_levenshtein_distance)
def inverted_levenshtein_distance_with(config: Config) -> Similarity[str]:
    """
    Args:
        config: The configuration object that contains the necessary parameters for calculating the inverted Levenshtein
        distance.

    Returns:
        Similarity[str]: A similarity object calculating the inverted Levenshtein distance value.

    """
    return inverted_levenshtein_distance
