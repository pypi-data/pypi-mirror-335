from mitm_tooling.representation import Header
from mitm_tooling.transformation.superset.definition_bundles import SupersetDatasourceBundle, \
    SupersetVisualizationBundle


def mk_empty_visualization(header: Header, datasource_bundle: SupersetDatasourceBundle) -> SupersetVisualizationBundle:
    return SupersetVisualizationBundle()