from collections.abc import Iterable, Sequence
from re import Pattern, split as regex_split


def split(string: str, delimiter: str | Iterable[str] | None) -> set[str]:
    """
    Args:
        string: A string that needs to be split.
        delimiter: A delimiter used to split the string. It can be a single character, a collection of characters,
                   or None. If delimiter is None, the string will be split using whitespace as the delimiter.

    Returns:
        A set containing the split tokens of the given string.

    Example usage:
        >>> string = "Hello World"
        >>> delimiter = " "
        >>> split(string, delimiter)
        {'Hello', 'World'}

        >>> string = "1,2,3,4,5"
        >>> delimiter = ","
        >>> split(string, delimiter)
        {'1', '2', '3', '4', '5'}

        >>> string = "Hello World"
        >>> split(string, None)
        {'Hello', 'World'}
    """
    match delimiter:
        case str(split_by): return set(string.split(split_by))
        case None: return set(string.split())
        case _:
            tokens: set[str] = {string}
            for symbol in delimiter:
                tokens = {subtoken.strip() for token in tokens for subtoken in token.split(symbol)}
            return tokens


def tokenize(string: str, delimiters: set[str]) -> Sequence[str]:
    """
    Args:
        string: A string to be tokenized.
        delimiters: A set of delimiters to split the string.

    Returns:
        A sequence of tokens generated from splitting the input string using the provided delimiters.

    Example:
        >>> input_string = "Hello, world! How are you?"
        >>> input_delimiters = {",", "!", "?"}
        >>> tokenize(input_string, input_delimiters)
        ['Hello', ' world', ' How are you']
    """
    tokens: Sequence[str] = [string]

    for delimiter in delimiters:
        tokens = list(filter(None, (subtoken for token in tokens for subtoken in token.split(delimiter))))
    return tokens


