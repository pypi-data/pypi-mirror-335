from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import partial
from string import whitespace

from jellyfish import jaro_winkler_similarity

from findanywhere.algorithms.strings import split
from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import Similarity





def token_best_fit_similarity(
        left: str,
        right: str,
        *,
        delimiter: str | None = None
) -> float:
    """
    Calculate the similarity between two strings (left and right) on the basis of 'best fit'
    approach with tokens. 'Best fit' means it finds the most similar token in the right string
    for each token in the left string, and calculates average similarity.

    The similarity metric used is Jaro-Winkler similarity, a string metric for measuring the
    edit distance between two sequences. The Jaro-Winkler similarity value is often used in
    data matching, record linkage, and name matching tasks, dealing with the messiness and variations
    of real-world data.

    Args:
        left: A string representing the left input.
        right: A string representing the right input.
        delimiter: A string or None, representing the delimiter used to split the inputs into tokens. If None,
        the inputs are split by whitespace.

    Returns:
        A float representing the token best-fit similarity between the left and right
        inputs.

    Example:
        token_best_fit_similarity('test string 1', 'test strng 1')
        should return a float close to 1 since the two strings are very similar.
    """
    left_tokens: set[str] = split(left, delimiter)
    right_tokens: set[str] = split(right, delimiter)
    similarity: float = 0.0
    if not left_tokens:
        return 1.0
    for token in left_tokens:
        similarity += max(map(partial(jaro_winkler_similarity, token), right_tokens), default=0.0)
    return similarity / len(left_tokens)


@dataclass(frozen=True)
class TokenBestFitConfig(Config):
    """

    The TokenBestFitConfig class is a configuration class that inherits from the Config base class. It is used to
    specify the configuration for the token best fit algorithm.

    Attributes:
    - delimiter (str | None): The delimiter used for tokenization. It can be a string or None if whitespace.

    """
    delimiter: str | None = None


@as_factory('token_best_fit_similarity', using=token_best_fit_similarity)
def token_best_fit_similarity_with(config: TokenBestFitConfig) -> Similarity[str]:
    return partial(
        token_best_fit_similarity,
        delimiter=config.delimiter
    )


def token_best_fit_multi_separator_similarity(
        left: str,
        right: str,
        *,
        delimiters: Iterable[str] = whitespace
) -> float:
    left_tokens: set[str] = split(left, set(delimiters))
    right_tokens: set[str] = split(right, set(delimiters))
    similarity: float = 0.0
    if not left_tokens:
        return 1.0
    for token in left_tokens:
        similarity += max(map(partial(jaro_winkler_similarity, token), right_tokens), default=0.0)
    return similarity / len(left_tokens)


@dataclass(frozen=True)
class TokenBestFitMultiSeparatorConfig(Config):
    delimiters: str | list[str] = field(default_factory=lambda: list(whitespace))


@as_factory('token_best_fit_multi_separator_similarity', token_best_fit_multi_separator_similarity)
def token_best_fit_mulit_separator_similarity_with(config: TokenBestFitMultiSeparatorConfig) -> Similarity[str]:
    return partial(token_best_fit_multi_separator_similarity, delimiters=config.delimiters)
