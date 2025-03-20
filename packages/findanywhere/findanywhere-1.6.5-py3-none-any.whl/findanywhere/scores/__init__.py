from findanywhere.scores.deduction import average_score, create_average_score, create_maximum_score
from findanywhere.types.factory import FactoryMap
from findanywhere.types.similarity import DeduceScore

DEDUCTION_FACTORIES: FactoryMap[DeduceScore] = FactoryMap((create_average_score, create_maximum_score))

DEFAULT_DEDUCTION: str = create_average_score.name