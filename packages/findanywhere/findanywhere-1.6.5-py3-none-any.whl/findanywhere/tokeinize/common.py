from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial, reduce
from itertools import compress
from re import Pattern, UNICODE, MULTILINE, DOTALL, IGNORECASE, compile as regex
from operator import or_
from string import whitespace

from findanywhere.algorithms.strings import tokenize
from findanywhere.types.factory import as_factory, Config
from findanywhere.types.tokenize import Tokenizer


def tokenize_by_regex(pattern: Pattern, string: str) -> Sequence[str]:
    """
    Args:
        pattern: A regular expression pattern used for tokenizing the string.
        string: A string to be tokenized.

    Returns:
        A sequence of strings where each element is a token extracted from the given string by splitting it using the
        provided regular expression pattern.
    """
    return pattern.split(string)


@dataclass(frozen=True)
class RegexTokenizerConfig(Config):
    """

    The RegexTokenizerConfig class is a configuration class for a regex tokenizer. It inherits from the Config class.

    Attributes:
        pattern (str): The regex pattern used for tokenizing.
        unicode (bool): Determines whether to enable unicode flag for the regex pattern. Default is True.
        multiline (bool): Determines whether to enable multiline flag for the regex pattern. Default is True.
        dotall (bool): Determines whether to enable dotall flag for the regex pattern. Default is True.
        ignore_case (bool): Determines whether to enable ignore case flag for the regex pattern. Default is True.

    Properties:
        flags (int): The bitwise OR combination of regex flags based on the configuration attributes.

    """
    pattern: str = r'\s+'
    unicode: bool = True
    multiline: bool = True
    dotall: bool = True
    ignore_case: bool = True

    @property
    def flags(self) -> int:
        """
        Returns the combined flags value based on the current settings.

        Returns: An integer value representing the combined flags.
        """
        return reduce(
            or_,
            compress(
                (UNICODE, MULTILINE, DOTALL, IGNORECASE),
                (self.unicode, self.multiline, self.dotall, self.ignore_case)
            )
        )


@as_factory('regex', using=tokenize_by_regex)
def tokenize_by_regex_with(config: RegexTokenizerConfig) -> Tokenizer:
    """
    Args:
        config: An instance of RegexTokenizerConfig containing the configuration for tokenizing by regex.

    Returns:
        A Tokenizer function wrapped in a factory decorator. The factory decorator receives 'regex' as the factory type
        and uses the 'tokenize_by_regex' function as the implementation. The factory function takes a config object of
        type RegexTokenizerConfig and returns a partial function that applies the 'tokenize_by_regex' function with a
        compiled regex pattern generated from the config object. The partial function serves as the actual Tokenizer
        function.
    """
    return partial(tokenize_by_regex, regex(config.pattern, config.flags))


@dataclass(frozen=True)
class DelimiterTokenizerConfig(Config):
    """
    A class representing the configuration for a delimiter tokenizer.

    Attributes:
        delimiters (set[str]): The set of delimiters to be used for tokenizing.

    """
    delimiters: set[str] | frozenset[str] | list[str] = frozenset(whitespace)


@as_factory('delimiter', using=tokenize)
def tokenize_by_delimiter_with(config: DelimiterTokenizerConfig) -> Tokenizer:
    """
    Args:
        config: A DelimiterTokenizerConfig object containing the configuration for the tokenizer.

    Returns:
        A Tokenizer object that tokenizes text using the specified delimiters.
    """
    return partial(tokenize, delimiters=config.delimiters)


