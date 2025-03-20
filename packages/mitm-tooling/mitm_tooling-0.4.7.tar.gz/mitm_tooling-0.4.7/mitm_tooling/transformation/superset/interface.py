from mitm_tooling.representation import Header
from mitm_tooling.transformation.superset.definition_bundles import SupersetDatasourceBundle, \
    SupersetVisualizationBundle, SupersetMitMDatasetBundle
from mitm_tooling.transformation.superset.from_intermediate import header_into_superset_mitm_dataset_bundle
from mitm_tooling.transformation.superset.from_intermediate import header_into_superset_visualization_bundle
from .common import SupersetDBConnectionInfo
from .definitions.mitm_dataset import MitMDatasetIdentifier
from .from_intermediate import header_into_superset_datasource_bundle


def mk_superset_datasource_bundle(header: Header, db_conn_info: SupersetDBConnectionInfo) -> SupersetDatasourceBundle:
    return header_into_superset_datasource_bundle(header, db_conn_info)


def mk_superset_visualization_bundle(header: Header,
                                     superset_datasource_bundle: SupersetDatasourceBundle) -> SupersetVisualizationBundle:
    return header_into_superset_visualization_bundle(header, superset_datasource_bundle)


def mk_superset_mitm_dataset_bundle(header: Header, dataset_identifier: MitMDatasetIdentifier, db_conn_info: SupersetDBConnectionInfo,
                                    include_visualizations: bool = False) -> SupersetMitMDatasetBundle:
    return header_into_superset_mitm_dataset_bundle(header, db_conn_info, dataset_identifier, include_visualizations=include_visualizations)
