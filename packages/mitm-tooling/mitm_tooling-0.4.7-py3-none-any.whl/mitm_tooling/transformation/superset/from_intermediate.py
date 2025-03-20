from mitm_tooling.representation import Header
from .common import SupersetDBConnectionInfo
from .definition_bundles import SupersetDatasourceBundle, SupersetMitMDatasetBundle, SupersetVisualizationBundle
from .definitions.mitm_dataset import MitMDatasetIdentifier
from .mitm_specific import get_mitm_visualization_factory


def header_into_superset_datasource_bundle(header: Header,
                                           db_conn_info: SupersetDBConnectionInfo) -> SupersetDatasourceBundle:
    from ..sql.from_intermediate import header_into_db_meta
    from .from_sql import db_meta_into_superset_datasource_bundle
    db_meta = header_into_db_meta(header)
    return db_meta_into_superset_datasource_bundle(db_meta, db_conn_info)


def header_into_superset_visualization_bundle(header: Header,
                                              datasource_bundle: SupersetDatasourceBundle) -> SupersetVisualizationBundle:
    return get_mitm_visualization_factory(header.mitm)(header, datasource_bundle)


def header_into_superset_mitm_dataset_bundle(header: Header,
                                             db_conn_info: SupersetDBConnectionInfo,
                                             dataset_identifier: MitMDatasetIdentifier,
                                             include_visualizations: bool = False) -> SupersetMitMDatasetBundle:
    from ..sql.from_intermediate import header_into_db_meta
    from .from_sql import db_meta_into_mitm_dataset_bundle
    db_meta = header_into_db_meta(header)
    mitm_dataset_bundle = db_meta_into_mitm_dataset_bundle(db_meta, db_conn_info, dataset_identifier, header.mitm)
    if include_visualizations:
        mitm_dataset_bundle = mitm_dataset_bundle.with_visualization_bundle(
            header_into_superset_visualization_bundle(header,
                                                      mitm_dataset_bundle.datasource_bundle))

    return mitm_dataset_bundle
