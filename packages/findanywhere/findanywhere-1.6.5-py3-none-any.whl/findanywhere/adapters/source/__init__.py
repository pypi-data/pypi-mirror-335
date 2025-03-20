from typing import Any

from findanywhere.adapters.source.jsonlike import load_jsonlike_source_using
from findanywhere.adapters.source.text import load_text_source_using
from findanywhere.adapters.source.tabular import load_tabular_source_using
from findanywhere.adapters.source.website import load_html_source_using
from findanywhere.adapters.source.xmllike import load_xml_source_using
from findanywhere.ports.source import SourceAdapter
from findanywhere.types.factory import FactoryMap

SOURCE_FACTORIES: FactoryMap[SourceAdapter[Any, Any, Any]] = FactoryMap(
    (
        load_text_source_using, load_tabular_source_using, load_jsonlike_source_using, load_xml_source_using,
        load_html_source_using
    )
)
