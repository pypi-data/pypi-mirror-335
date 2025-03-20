from mitm_tooling.extraction.sql.data_models import DBMetaInfo
from mitm_tooling.extraction.sql.data_models.db_meta import DBMetaInfoBase
from mitm_tooling.extraction.sql.db import connect_and_reflect
from .common import SupersetDBConnectionInfo
from .common import _mk_engine, SQLiteFileOrEngine
from .definition_bundles import SupersetDatasourceBundle, SupersetMitMDatasetBundle
from .definitions.mitm_dataset import MitMDatasetIdentifier
from .factories.database import mk_database
from .factories.dataset import mk_dataset
from .factories.mitm_dataset import mk_mitm_dataset
from ...definition import MITM


def db_meta_into_superset_datasource_bundle(db_meta: DBMetaInfoBase,
                                            db_conn_info: SupersetDBConnectionInfo) -> SupersetDatasourceBundle:
    sqlalchemy_uri = db_conn_info.sql_alchemy_uri
    db_name = db_conn_info.db_name
    dialect = db_conn_info.dialect_cls()

    database = mk_database(name=db_name, sqlalchemy_uri=sqlalchemy_uri, uniquify_name=True)

    database_uuid = database.uuid
    datasets = []
    for schema_name, schema_tables in db_meta.db_structure.items():
        for table_name, tm in schema_tables.items():
            datasets.append(mk_dataset(tm, database_uuid, dialect=dialect))

    return SupersetDatasourceBundle(database=database, datasets=datasets)


def db_meta_into_mitm_dataset_bundle(db_meta: DBMetaInfoBase,
                                     db_conn_info: SupersetDBConnectionInfo,
                                     dataset_identifier: MitMDatasetIdentifier,
                                     mitm: MITM) -> SupersetMitMDatasetBundle:
    datasource_bundle = db_meta_into_superset_datasource_bundle(db_meta, db_conn_info)
    mitm_dataset = mk_mitm_dataset(dataset_identifier.dataset_name, mitm, uuid=dataset_identifier.uuid,
                                   database_uuid=datasource_bundle.database_uuid,
                                   table_uuids=datasource_bundle.dataset_uuids)
    return SupersetMitMDatasetBundle(mitm_dataset=mitm_dataset, datasource_bundle=datasource_bundle)


def db_into_superset_datasource_bundle(arg: SQLiteFileOrEngine,
                                       db_conn_info: SupersetDBConnectionInfo) -> SupersetDatasourceBundle:
    engine = _mk_engine(arg)

    meta, _ = connect_and_reflect(engine, allowed_schemas=[db_conn_info.schema_name])
    db_meta = DBMetaInfo.from_sa_meta(meta, default_schema=db_conn_info.schema_name)

    return db_meta_into_superset_datasource_bundle(db_meta, db_conn_info)


def db_into_mitm_dataset_bundle(arg: SQLiteFileOrEngine,
                                db_conn_info: SupersetDBConnectionInfo,
                                dataset_identifier: MitMDatasetIdentifier,
                                mitm: MITM) -> SupersetMitMDatasetBundle:
    datasource_bundle = db_into_superset_datasource_bundle(arg, db_conn_info)
    mitm_dataset = mk_mitm_dataset(dataset_identifier.dataset_name, mitm, uuid=dataset_identifier.uuid,
                                   database_uuid=datasource_bundle.database_uuid,
                                   table_uuids=datasource_bundle.dataset_uuids)
    return SupersetMitMDatasetBundle(mitm_dataset=mitm_dataset, datasource_bundle=datasource_bundle)
