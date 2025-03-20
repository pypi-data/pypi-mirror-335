from typing import Any

from findanywhere.adapters.evaluation.string_distance import evaluate_by_similarity, evaluate_by_similarity_using
from findanywhere.ports.evaluation import EvaluationAdapter
from findanywhere.types.factory import FactoryMap

EVALUATION_FACTORIES: FactoryMap[EvaluationAdapter[Any]] = FactoryMap((evaluate_by_similarity_using,))
