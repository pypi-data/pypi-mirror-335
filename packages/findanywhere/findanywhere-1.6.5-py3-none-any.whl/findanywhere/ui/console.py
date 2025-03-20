from argparse import ArgumentParser, Namespace, BooleanOptionalAction, Action, SUPPRESS
from collections.abc import Iterable
from dataclasses import fields, MISSING, Field
from functools import partial
from io import StringIO
from json import dump
from multiprocessing import cpu_count
from pathlib import Path
from typing import cast, Any, TypeVar

from toolz import valmap, valfilter

from findanywhere.adapters.evaluation import EVALUATION_FACTORIES
from findanywhere.adapters.source import SOURCE_FACTORIES
from findanywhere.ports.evaluation import EvaluationAdapter
from findanywhere.ports.source import SourceAdapter
from findanywhere.schema import load_schema, SearchSchema
from findanywhere.scores import DEDUCTION_FACTORIES
from findanywhere.search.base import Search, search, SearchPattern
from findanywhere.search.parallel import parallel_search
from findanywhere.search.sequential import sequential_search
from findanywhere.similarity import SIMILARITY_FACTORIES
from findanywhere.thresholds import THRESHOLD_FACTORIES
from findanywhere.tokeinize import TOKENIZER_FACTORIES
from findanywhere.types.factory import FactoryMap, Factory, Config
from findanywhere.types.input_data import InputData
from findanywhere.types.similarity import Similarity, DeduceScore, ThresholdFilter
from findanywhere.types.tokenize import Tokenizer


def main() -> None:
    """
    Main method for searching data in a data set using a schema.
    """
    parser: ArgumentParser = ArgumentParser('Search for data in a data set using a schema')
    parser.add_argument('schema', type=Path, help='Schema to use for search.')
    parser.add_argument('input_data', type=Path, help='JSON file with input data')
    parser.add_argument('--processes', type=int, default=cpu_count())
    parser.add_argument('--out', type=Path, default=Path('findings.json_line'))
    parser.add_argument('--sequential', type=bool, default=False, help='Do not use parallel search. (False)')
    primary_args: Namespace = parser.parse_known_args()[0]

    schema: SearchSchema = load_schema(primary_args.schema)

    parser.add_argument('location', type=schema.source.config.location_type())
    args: Namespace = parser.parse_args()

    search_: Search = partial(search, schema.evaluation_adapter(), schema.create_deduction(), schema.create_threshold())

    source_adapter: SourceAdapter = schema.source_adapter()

    search_style: SearchPattern = cast(SearchPattern, partial(
        parallel_search, processes=args.processes
    )) if not primary_args.sequential else sequential_search

    with open(args.out, 'w', encoding='utf-8', errors='surrogateescape') as out:
        for result in search_style(InputData.from_json(args.input_data), search_, source_adapter(args.location)):
            dump(result, out, ensure_ascii=False, default=str)
            out.write('\n')


def _add_field_as_argument(parser: ArgumentParser, category: str, field_: Field):
    flag: str = f'--{category}-{field_.name}'.replace('_', '-')
    default: Any = field_.default
    required: bool = default == MISSING and field_.default_factory is MISSING
    if field_.type is bool:
        parser.add_argument(flag, required=required, default=default, action=BooleanOptionalAction)
        return
    if isinstance(field_.default, Iterable):
        parser.add_argument(flag, required=required, default=None, action='append')
        return
    parser.add_argument(flag, required=required, default=default)


def _add_category_as_argument(parser: ArgumentParser, category: str, factory: Factory[Any, Any]):
    for field_ in fields(factory.config_type):
        _add_field_as_argument(parser, category, field_)


def _parse_config(config_type: type[Config], category: str, args: Namespace) -> Config:
    return config_type.from_dict(
        dict(
            (k.removeprefix(f'{category}_'), v)
            for k, v in vars(args).items()
            if v is not None and v is not MISSING
        )
    )

_T = TypeVar('_T')


def _parse_subcategory(
        subparser,
        category: str,
        selection: str,
        args: list[str],
        factory_map: FactoryMap[_T],
        sub_parser: list[ArgumentParser],
        **overrides: Any
) -> _T:
    factory: Factory[_T, Any] = factory_map[selection]
    category_parser = subparser.add_parser(category, add_help=False)
    sub_parser.append(category_parser)
    _add_category_as_argument(category_parser, category, factory)
    sub_args = category_parser.parse_known_args(args)
    for key, value in overrides.items():
        setattr(sub_args[0], key, value)
    return factory.from_config(_parse_config(factory.config_type, category, sub_args[0]))


def schemaless_main() -> None:
    parser: ArgumentParser = ArgumentParser('', add_help=False)
    parser.add_argument('input_data', type=Path, help='JSON file with input data')
    parser.add_argument('location')
    parser.add_argument('--help', default=False, help='Print this help message')

    parser.add_argument(
        '--tokenizer', default=TOKENIZER_FACTORIES.default(), choices=TOKENIZER_FACTORIES.choices()
    )
    parser.add_argument(
        '--deduction', default=DEDUCTION_FACTORIES.default(), choices=DEDUCTION_FACTORIES.choices()
    )
    parser.add_argument(
        '--similarity', default=SIMILARITY_FACTORIES.default(), choices=SIMILARITY_FACTORIES.choices()
    )
    parser.add_argument(
        '--source', default=SOURCE_FACTORIES.default(), choices=SOURCE_FACTORIES.choices()
    )
    parser.add_argument(
        '--evaluation', default=EVALUATION_FACTORIES.default(), choices=EVALUATION_FACTORIES.choices()
    )
    parser.add_argument(
        '--threshold', default=THRESHOLD_FACTORIES.default(), choices=THRESHOLD_FACTORIES.choices()
    )
    parser.add_argument('--processes', default=cpu_count())
    parser.add_argument('--sequential', action=BooleanOptionalAction, default=True)
    parser.add_argument('--out', default=Path('result.json_line'), type=Path)
    initial_args, remaining_argv = parser.parse_known_args()

    subparser = parser.add_subparsers()
    sub_parser: list[ArgumentParser] = list()

    tokenizer: Tokenizer = _parse_subcategory(
        subparser, 'tokenizer', initial_args.tokenizer, remaining_argv, TOKENIZER_FACTORIES, sub_parser
    )
    similarity: Similarity = _parse_subcategory(
        subparser, 'similarity', initial_args.similarity, remaining_argv, SIMILARITY_FACTORIES, sub_parser
    )
    source: SourceAdapter = _parse_subcategory(
        subparser, 'source', initial_args.source, remaining_argv, SOURCE_FACTORIES, sub_parser,
        tokenizer=tokenizer
    )
    evaluation: EvaluationAdapter = _parse_subcategory(
        subparser, 'evaluation', initial_args.evaluation, remaining_argv, EVALUATION_FACTORIES,
        sub_parser, similarity=similarity
    )
    deduction: DeduceScore = _parse_subcategory(
        subparser, 'deduction', initial_args.deduction, remaining_argv, DEDUCTION_FACTORIES, sub_parser
    )
    threshold: ThresholdFilter = _parse_subcategory(
        subparser, 'threshold', initial_args.threshold, remaining_argv, THRESHOLD_FACTORIES, sub_parser
    )

    if initial_args.help:
        with StringIO() as help_buffer:
            parser.print_help(help_buffer)
            for parser in sub_parser:
                with StringIO() as buffer:
                    parser.print_help(file=buffer)
                    buffer.seek(0)
                    for line in filter(None, map(str.rstrip, buffer.readlines())):
                        if line[0].isspace():
                            help_buffer.write(f'  {line.strip()}\n')
            print(help_buffer.getvalue())
            exit(0)

    search_: Search = partial(search, evaluation, deduction, threshold)
    search_style: SearchPattern = cast(SearchPattern, partial(
        parallel_search, processes=initial_args.processes
    )) if not initial_args.sequential else sequential_search

    with open(initial_args.out, 'w', encoding='utf-8', errors='surrogateescape') as out:
        for result in search_style(
                InputData.from_json(initial_args.input_data), search_, source(initial_args.location)
        ):
            dump(result, out, ensure_ascii=False, default=str)
            out.write('\n')

    print(f"Results written to {initial_args.out}.")

