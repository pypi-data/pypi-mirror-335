from argparse import ArgumentParser
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TypeVar, Any, Generic

from dacite import from_dict
from yaml import dump, unsafe_load

from findanywhere.adapters.evaluation import EVALUATION_FACTORIES
from findanywhere.adapters.source import SOURCE_FACTORIES
from findanywhere.ports.evaluation import EvaluationAdapter
from findanywhere.ports.source import SourceAdapter, SourceConfig
from findanywhere.scores import DEDUCTION_FACTORIES, DEFAULT_DEDUCTION
from findanywhere.thresholds import THRESHOLD_FACTORIES, DEFAULT_THRESHOLD
from findanywhere.types.factory import Config, FactoryMap
from findanywhere.types.similarity import DeduceScore, ThresholdFilter

_T = TypeVar('_T')
_C = TypeVar('_C', bound=Config)


@dataclass(frozen=True)
class AdapterConfig(Generic[_C]):
    """
    AdapterConfig is a generic class that represents a configuration for an adapter. It holds the name of the adapter
    and the configuration data.

    Attributes:
        name (str): The name of the adapter.
        config (_C): The configuration data of the adapter.
    """
    name: str
    config: _C

    @classmethod
    def from_name(cls, name: str, factories: FactoryMap) -> 'AdapterConfig':
        """
        Args:
            name: The name of the adapter configuration to retrieve.
            factories: A dictionary that maps adapter names to their corresponding FactoryMap objects.

        Returns:
            An instance of the 'AdapterConfig' class determined by the given name and the corresponding config type from the factories dictionary.

        """
        return cls(name, factories[name].config_type())

    @classmethod
    def from_name_and_config(cls, name: str, config: dict[str, Any], factories: FactoryMap) -> 'AdapterConfig':
        """
        Args:
            name: The name of the adapter.
            config: The configuration parameters for the adapter.
            factories: The map of factory objects for creating adapter configurations.

        Returns:
            AdapterConfig: An instance of the AdapterConfig class based on the specified name, config, and factories.

        """
        return cls(name, from_dict(factories[name].config_type, config))


@dataclass(frozen=True)
class SearchSchema:
    """
    SearchSchema encapsulates the configuration of a search operation. It defines the adapters and configurations
    necessary for executing the search.

    Attributes:
        source: An AdapterConfig object that represents the configuration for the data source adapter.
        evaluation: An AdapterConfig object that represents the configuration for the evaluation adapter.
        deduction: An AdapterConfig object that represents the configuration for the deduction adapter.
        threshold: An AdapterConfig object that represents the configuration for the threshold filter.

    Methods:
        evaluation_adapter: Returns an EvaluationAdapter object based on the evaluation configuration.
        source_adapter: Returns a SourceAdapter object based on the data source configuration.
        create_deduction: Returns a DeduceScore object based on the deduction configuration.
        create_threshold: Returns a ThresholdFilter object based on the threshold configuration.
    """
    source: AdapterConfig[SourceConfig]
    evaluation: AdapterConfig[Config]
    deduction: AdapterConfig[Config]
    threshold: AdapterConfig[Config]

    def evaluation_adapter(self) -> EvaluationAdapter:
        """
        Return an instance of EvaluationAdapter based on the evaluation name and config.

        Returns:
            EvaluationAdapter: An instance of EvaluationAdapter.

        """
        return EVALUATION_FACTORIES[self.evaluation.name].from_config(self.evaluation.config)

    def source_adapter(self) -> SourceAdapter:
        """
        Method: source_adapter

        Description:
        This method returns a SourceAdapter object based on the given source name and configuration. The source name and
        configuration determine which SourceAdapter to use.

        Returns:
        - SourceAdapter: The SourceAdapter object created based on the provided source name and configuration.

        Example Usage:
        source = source_adapter()
        """
        return SOURCE_FACTORIES[self.source.name].from_config(self.source.config)

    def create_deduction(self) -> DeduceScore:
        """
        Create a deduction object based on the given configuration.

        Returns:
            A DeduceScore object representing the deduction.
        """
        return DEDUCTION_FACTORIES[self.deduction.name].from_config(self.deduction.config)

    def create_threshold(self) -> ThresholdFilter:
        """
        Creates a ThresholdFilter based on the provided threshold configuration.

        Returns:
            ThresholdFilter: The created ThresholdFilter object.

        Raises:
            KeyError: If the threshold name is not found in the THRESHOLD_FACTORIES dictionary.
        """
        return THRESHOLD_FACTORIES[self.threshold.name].from_config(self.threshold.config)


def create_schema(
        source_adapter_name: str,
        evaluation_adapter_name: str,
        deduction_name: str,
        threshold_name: str,
) -> SearchSchema:
    """
    Creates a new search schema using the specified adapter names and factory dictionaries.

    Args:
        source_adapter_name (str): The name of the adapter to use for the source data.
        evaluation_adapter_name (str): The name of the adapter to use for evaluation data.
        deduction_name (str): The name of the adapter to use for deduction data.
        threshold_name (str): The name of the adapter to use for threshold data.

    Returns:
        SearchSchema: The newly created search schema object.

    """
    return SearchSchema(
        AdapterConfig.from_name(source_adapter_name, SOURCE_FACTORIES),
        AdapterConfig.from_name(evaluation_adapter_name, EVALUATION_FACTORIES),
        AdapterConfig.from_name(deduction_name, DEDUCTION_FACTORIES),
        AdapterConfig.from_name(threshold_name, THRESHOLD_FACTORIES)
    )


def load_schema(schema_file: Path) -> SearchSchema:
    """
    Args:
        schema_file (Path): The path to the schema file to load.

    Returns:
        SearchSchema: An instance of the SearchSchema class containing the loaded schema.

    """
    with schema_file.open() as src:
        data = unsafe_load(src)
        return SearchSchema(
            AdapterConfig.from_name_and_config(
                data['source']['name'], data['source'].get('config', dict()), SOURCE_FACTORIES
            ),
            AdapterConfig.from_name_and_config(
                data['evaluation']['name'], data['evaluation'].get('config', dict()), EVALUATION_FACTORIES
            ),
            AdapterConfig.from_name_and_config(
                data['deduction']['name'], data['deduction'].get('config', dict()), DEDUCTION_FACTORIES
            ),
            AdapterConfig.from_name_and_config(
                data['threshold']['name'], data['threshold'].get('config', dict()), THRESHOLD_FACTORIES
            )
        )




def main() -> None:
    """
    Main method for creating a search schema.

    This method creates a search schema based on command line arguments. The search schema is used for later use in
    search operations.
    """
    parser: ArgumentParser = ArgumentParser('Create search schema for later use')
    parser.add_argument('source', choices=SOURCE_FACTORIES.choices())
    parser.add_argument('evaluation', choices=EVALUATION_FACTORIES.choices())
    parser.add_argument('--deduce_score', choices=DEDUCTION_FACTORIES.choices(), default=DEFAULT_DEDUCTION)
    parser.add_argument('--threshold', choices=THRESHOLD_FACTORIES.choices(), default=DEFAULT_THRESHOLD)
    parser.add_argument('--out', type=Path, default=Path().joinpath('schema.json'))

    args = parser.parse_args()
    with open(args.out, 'w', encoding='utf-8') as out:
        dump(asdict(create_schema(args.source, args.evaluation, args.deduce_score, args.threshold)), out)




