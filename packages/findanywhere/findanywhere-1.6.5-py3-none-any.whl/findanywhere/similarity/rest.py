from dataclasses import dataclass, field
from functools import partial

from requests import get
from toolz import get_in

from findanywhere.types.factory import as_factory, Config
from findanywhere.types.similarity import Similarity


@dataclass(frozen=True)
class RestAPIConfig(Config):
    """

    """
    url: str = 'http://localhost:8080'
    left_parameter_name: str = 'left'
    right_parameter_name: str = 'right'
    result_path: list[str | int]  = field(default_factory=list)
    verify_ssl: bool = True
    headers: dict[str, str] = field(default_factory=dict)


def rest_endpoint_similarity(
        config: RestAPIConfig,
        left: str,
        right: str
) -> float:
    """

    """
    with get(
            config.url,
            headers=config.headers,
            verify=config.verify_ssl,
            params={config.left_parameter_name: left, config.right_parameter_name: right}
    ) as response:
        if response.status_code == 200:
            return float(get_in(config.result_path, response.json()))
        else:
            raise ConnectionError(f'HTTP {response.status_code}: {response.text}')


@as_factory('rest', using=rest_endpoint_similarity)
def rest_endpoint_similarity_with(config: RestAPIConfig) -> Similarity[str]:
    return partial(rest_endpoint_similarity, config)