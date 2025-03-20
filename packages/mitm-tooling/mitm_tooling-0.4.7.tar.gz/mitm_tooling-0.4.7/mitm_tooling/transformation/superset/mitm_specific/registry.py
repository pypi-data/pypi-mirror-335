from typing import Callable

from mitm_tooling.definition import MITM
from mitm_tooling.representation import Header
from .fallback import mk_empty_visualization
from .maed_visualization import mk_maed_visualization
from ..definition_bundles import SupersetDatasourceBundle, SupersetVisualizationBundle

VisualizationBundleFactory = Callable[[Header, SupersetDatasourceBundle], SupersetVisualizationBundle]



mitm_specific_visualization_factories: dict[
    MITM, VisualizationBundleFactory] = {
    MITM.MAED: mk_maed_visualization,
}


def get_mitm_visualization_factory(mitm: MITM) -> VisualizationBundleFactory:
    if factory := mitm_specific_visualization_factories.get(mitm):
        return factory
    else:
        return mk_empty_visualization
