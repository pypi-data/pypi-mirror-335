from findanywhere.tokeinize.common import tokenize_by_regex_with, tokenize_by_delimiter_with
from findanywhere.types.factory import FactoryMap
from findanywhere.types.tokenize import Tokenizer

TOKENIZER_FACTORIES: FactoryMap[Tokenizer] = FactoryMap[Tokenizer](
    [tokenize_by_regex_with, tokenize_by_delimiter_with]
)