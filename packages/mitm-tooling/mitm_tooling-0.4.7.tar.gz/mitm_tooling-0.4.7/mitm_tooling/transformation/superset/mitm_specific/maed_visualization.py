from mitm_tooling.representation import Header
from ..definition_bundles import SupersetVisualizationBundle, \
    SupersetDatasourceBundle
from .maed_dashboards import mk_maed_dashboard


def mk_maed_visualization(header: Header,
                          superset_datasource_bundle: SupersetDatasourceBundle) -> SupersetVisualizationBundle:
    dashboard, charts = mk_maed_dashboard(header, superset_datasource_bundle)
    return SupersetVisualizationBundle(charts=charts, dashboards=[dashboard])
