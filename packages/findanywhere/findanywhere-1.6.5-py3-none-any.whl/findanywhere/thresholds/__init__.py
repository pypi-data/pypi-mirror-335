from findanywhere.thresholds.basic import no_threshold_using, constant_threshold_using
from findanywhere.types.factory import FactoryMap
from findanywhere.types.similarity import ThresholdFilter

THRESHOLD_FACTORIES: FactoryMap[ThresholdFilter] = FactoryMap[ThresholdFilter](
    (no_threshold_using, constant_threshold_using)
)

DEFAULT_THRESHOLD: str = no_threshold_using.name