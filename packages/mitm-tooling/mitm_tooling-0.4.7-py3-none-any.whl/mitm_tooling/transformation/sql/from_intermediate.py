from mitm_tooling.extraction.sql.data_models import DBMetaInfo
from mitm_tooling.representation import MITMData
from mitm_tooling.representation.intermediate_representation import Header
from mitm_tooling.representation.sql_representation import mk_sql_rep_schema, SQLRepresentationSchema, \
    SQL_REPRESENTATION_DEFAULT_SCHEMA


def sql_rep_schema_to_db_meta(sql_rep_schema: SQLRepresentationSchema) -> DBMetaInfo:
    return DBMetaInfo.from_sa_meta(sql_rep_schema.meta, default_schema=SQL_REPRESENTATION_DEFAULT_SCHEMA)


def header_into_db_meta(header: Header) -> DBMetaInfo:
    sql_rep_schema = mk_sql_rep_schema(header)
    return sql_rep_schema_to_db_meta(sql_rep_schema)


def mitm_data_into_db_meta(mitm_data: MITMData) -> DBMetaInfo:
    return header_into_db_meta(mitm_data.header)

