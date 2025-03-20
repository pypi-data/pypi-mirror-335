from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Any, Sequence

import pandas as pd
import pydantic
import sqlalchemy.sql.schema
from pydantic import AnyUrl, ConfigDict
from sqlalchemy import func
from sqlalchemy.pool import StaticPool

from mitm_tooling.definition import RelationName
from mitm_tooling.definition.definition_tools import ColGroupMaps
from mitm_tooling.utilities.sql_utils import create_sa_engine, qualify
from .common import *
from .intermediate_representation import Header, MITMData, TypeName
from .sql.common import *
from ..utilities.io_utils import FilePath
from ..utilities.backports.sqlchemy_sql_views import create_view

if TYPE_CHECKING:
    pass

SQL_REPRESENTATION_DEFAULT_SCHEMA = 'main'

ColumnsDict = dict[RelationName, sa.Column]
ViewsDict = dict[TableName, sa.Table]
ConceptTablesDict = dict[ConceptName, sa.Table]
ConceptTypeTablesDict = dict[ConceptName, dict[TypeName, sa.Table]]

MitMConceptSchemaItemGenerator = Callable[
    [MITM, ConceptName, TableName, ColumnsDict, ColumnsDict | None], Generator[
        sqlalchemy.sql.schema.SchemaItem, None, None]]
MitMConceptColumnGenerator = Callable[
    [MITM, ConceptName], Generator[tuple[str, sa.Column], None, None]]
MitMDBViewsGenerator = Callable[[MITM, ConceptTablesDict, ConceptTypeTablesDict],
Generator[
    tuple[
        TableName, Queryable], None, None]]

ARTIFICIAL_ROW_ID_PREFIX = 'row'


def _get_unique_id_col_name(prefix: str | None = None) -> str:
    return '__' + ((prefix + '_') if prefix else '') + 'id'


def _within_concept_id_col(mitm: MITM, concept: ConceptName) -> str:
    parent_concept = get_mitm_def(mitm).get_parent(concept)
    return _get_unique_id_col_name(parent_concept)


class SQLRepresentationSchema(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    meta: sa.MetaData
    concept_tables: ConceptTablesDict
    type_tables: ConceptTypeTablesDict
    views: ViewsDict


def mk_concept_table_name(mitm: MITM, concept: ConceptName) -> TableName:
    return get_mitm_def(mitm).get_properties(concept).plural


def mk_type_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName) -> TableName:
    return get_mitm_def(mitm).get_properties(concept).key + '_' + type_name.lower()


def mk_link_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName, fk_name: RelationName) -> TableName:
    return mk_type_table_name(mitm, concept, type_name) + '_' + fk_name.lower()


def has_type_tables(mitm: MITM, concept: ConceptName) -> bool:
    return get_mitm_def(mitm).get_properties(concept).permit_attributes


def has_natural_pk(mitm: MITM, concept: ConceptName) -> bool:
    return len(get_mitm_def(mitm).get_identity(concept)) > 0


def pick_table_pk(mitm: MITM, concept: ConceptName, created_columns: ColumnsDict) -> ColumnsDict | None:
    mitm_def = get_mitm_def(mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    prepended_cols = None
    if not has_natural_pk(mitm, concept):
        prepended_cols = lambda: [_within_concept_id_col(mitm, concept)]
    names, mapped_names = map_col_groups(mitm_def, concept, {
        'kind': lambda: 'kind',
        'type': lambda: concept_properties.typing_concept,
        'identity': lambda: list(concept_relations.identity)
    }, prepended_cols=prepended_cols)

    return {n: created_columns[n] for n in names}


def _gen_unique_constraint(mitm: MITM, concept: ConceptName, table_name: TableName, created_columns: ColumnsDict,
                           pk_columns: ColumnsDict | None) -> Generator[
    sa.sql.schema.SchemaItem, None, None]:
    yield sa.UniqueConstraint(*pk_columns.values())


def _gen_pk_constraint(mitm: MITM, concept: ConceptName, table_name: TableName, created_columns: ColumnsDict,
                       pk_columns: ColumnsDict | None) -> Generator[
    sa.sql.schema.SchemaItem, None, None]:
    yield sa.PrimaryKeyConstraint(*pk_columns.values())


def _gen_index(mitm: MITM, concept: ConceptName, table_name: TableName, created_columns: ColumnsDict,
               pk_columns: ColumnsDict | None) -> Generator[
    sa.sql.schema.SchemaItem, None, None]:
    yield sa.Index(f'{table_name}.index', *pk_columns.values(), unique=True)


def _gen_foreign_key_constraints(mitm: MITM, concept: ConceptName, table_name: TableName, created_columns: ColumnsDict,
                                 pk_columns: ColumnsDict | None) -> Generator[
    sa.sql.schema.SchemaItem, None, None]:
    mitm_def = get_mitm_def(mitm)
    _, concept_relations = mitm_def.get(concept)

    # self_fk
    if pk_columns:
        parent_concept = mitm_def.get_parent(concept)
        parent_table = mk_concept_table_name(mitm, parent_concept)
        cols, refcols = zip(
            *((c, qualify(table=parent_table, column=s)) for s, c in pk_columns.items()))
        yield sa.ForeignKeyConstraint(name='parent', columns=cols, refcolumns=refcols)

    for fk_name, fk_info in concept_relations.foreign.items():
        cols, refcols = zip(*fk_info.fk_relations.items())
        fkc = sa.ForeignKeyConstraint(name=fk_name, columns=[created_columns[c] for c in cols], refcolumns=[
            qualify(table=mk_concept_table_name(mitm, fk_info.target_concept), column=c)
            for c in refcols])
        yield fkc


_schema_item_generators: tuple[MitMConceptSchemaItemGenerator, ...] = (
    _gen_unique_constraint, _gen_pk_constraint, _gen_index, _gen_foreign_key_constraints,)


def _gen_within_concept_id_col(mitm: MITM, concept: ConceptName) -> Generator[tuple[str, sa.Column], None, None]:
    n = _within_concept_id_col(mitm, concept)
    yield n, sa.Column(n, sa.Integer, nullable=False, unique=True)


_column_generators: tuple[MitMConceptColumnGenerator, ...] = (_gen_within_concept_id_col,)


def mk_table(meta: sa.MetaData, mitm: MITM, concept: ConceptName, table_name: TableName, col_group_maps: ColGroupMaps,
             additional_column_generators: Iterable[MitMConceptColumnGenerator] | None = (
                     _gen_within_concept_id_col,),
             schema_item_generators: Iterable[MitMConceptSchemaItemGenerator] |
                                     None = (_gen_unique_constraint, _gen_pk_constraint, _gen_index,),
             override_schema: SchemaName | None = None) -> \
        tuple[
            sa.Table, ColumnsDict, ColumnsDict]:
    mitm_def = get_mitm_def(mitm)

    prepended_cols = None
    if additional_column_generators is not None:
        prepended_cols = lambda: [c for generator in additional_column_generators for c in generator(mitm, concept)]

    columns, created_columns = map_col_groups(mitm_def, concept, col_group_maps, prepended_cols=prepended_cols,
                                              ensure_unique=True)

    pk_cols = pick_table_pk(mitm, concept, created_columns)

    schema_items: list[sa.sql.schema.SchemaItem] = []
    if schema_item_generators is not None:
        for generator in schema_item_generators:
            schema_items.extend(generator(mitm, concept, table_name, created_columns, pk_cols))

    return sa.Table(table_name, meta, schema=override_schema if override_schema else SQL_REPRESENTATION_DEFAULT_SCHEMA,
                    *columns,
                    *schema_items), created_columns, pk_cols


def _prefix_col_name(prefix: str, name: str) -> str:
    return f'{prefix}_{name}'


def _gen_denormalized_views(mitm: MITM, concept_tables: ConceptTablesDict, type_tables: ConceptTypeTablesDict) -> \
        Generator[
            tuple[
                TableName, Queryable], None, None]:
    mitm_def = get_mitm_def(mitm)

    for main_concept in mitm_def.main_concepts:
        for concept in mitm_def.get_leafs(main_concept):
            view_name = mk_concept_table_name(mitm, concept) + '_denormalized_view'
            q = None
            if has_type_tables(mitm, concept):
                selections = []

                for leaf_concept in mitm_def.get_leafs(concept):
                    if concept_type_tables := type_tables.get(leaf_concept):
                        col_sets = [{(c.name, str(c.type)) for c in t.columns} for t in concept_type_tables.values()]
                        shared_cols = set.intersection(*col_sets)
                        all_cols = set.union(*col_sets)

                        for type_name, type_t in concept_type_tables.items():
                            selection = []
                            for (col_name, col_type) in all_cols:
                                if (c := type_t.columns.get(col_name)) is not None and str(c.type) == col_type:
                                    selection.append(c)
                                else:
                                    selection.append(sa.null().label(col_name))

                            # selection = (c if (c.name, str(c.type)) in shared_cols else sa.label(_prefix_col_name(type_name, c.name), c)
                            #             for c in type_t.columns)
                            selections.append(sa.select(*selection))

                if selections:
                    q = sa.union_all(*selections).subquery()
            else:
                if (concept_t := concept_tables.get(concept)) is not None:
                    # base_cols = {(c.name, str(c.type)) for c in concept_t.columns}
                    q = sa.select(concept_t)

            if q is not None:
                yield view_name, q

    for parent_concept, subs in mitm_def.sub_concept_map.items():
        if (concept_t := concept_tables.get(parent_concept)) is not None:
            for sub in subs:
                view_name = mk_concept_table_name(mitm, sub) + '_view'
                k = mitm_def.get_properties(sub).key
                q = sa.select(concept_t).where(concept_t.columns['kind'] == k)
                yield view_name, q


_view_generators: tuple[MitMDBViewsGenerator, ...] = (_gen_denormalized_views,)


def mk_sql_rep_schema(header: Header,
                      view_generators: Iterable[MitMDBViewsGenerator] | None = (_gen_denormalized_views,),
                      override_schema: SchemaName | None = None) -> SQLRepresentationSchema:
    schema_name = override_schema if override_schema else SQL_REPRESENTATION_DEFAULT_SCHEMA
    mitm_def = get_mitm_def(header.mitm)
    meta = sa.MetaData(schema=schema_name)

    concept_tables: ConceptTablesDict = {}
    type_tables: ConceptTypeTablesDict = {}
    views: dict[str, sa.Table] = {}

    for concept in mitm_def.main_concepts:
        concept_properties, concept_relations = mitm_def.get(concept)

        table_name = mk_concept_table_name(header.mitm, concept)

        t, t_columns, t_ref_columns = mk_table(meta, header.mitm, concept, table_name, {
            'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
            'type': lambda: (concept_properties.typing_concept, sa.Column(concept_properties.typing_concept,
                                                                          MITMDataType.Text.sa_sql_type,
                                                                          nullable=False)),
            'identity': lambda: [(name, sa.Column(name, dt.sa_sql_type, nullable=False)) for
                                 name, dt in
                                 mitm_def.resolve_identity_type(concept).items()],
            'inline': lambda: [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in
                               mitm_def.resolve_inlined_types(concept).items()],
            'foreign': lambda: [(name, sa.Column(name, dt.sa_sql_type)) for _, resolved_fk in
                                mitm_def.resolve_foreign_types(concept).items() for name, dt in
                                resolved_fk.items()]
        }, additional_column_generators=(_gen_within_concept_id_col,), schema_item_generators=(
            _gen_unique_constraint, _gen_pk_constraint, _gen_index,), override_schema=schema_name)
        concept_tables[concept] = t

    for he in header.header_entries:
        he_concept = he.concept
        if has_type_tables(header.mitm, he_concept):
            concept_properties, concept_relations = mitm_def.get(he_concept)

            table_name = mk_type_table_name(header.mitm, he_concept, he.type_name)

            t, t_columns, t_ref_columns = mk_table(meta, header.mitm, he_concept, table_name, {
                'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
                'type': lambda: (concept_properties.typing_concept, sa.Column(concept_properties.typing_concept,
                                                                              MITMDataType.Text.sa_sql_type,
                                                                              nullable=False)),
                'identity': lambda: [(name, sa.Column(name, dt.sa_sql_type, nullable=False)) for
                                     name, dt in
                                     mitm_def.resolve_identity_type(he_concept).items()],
                'inline': lambda: [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in
                                   mitm_def.resolve_inlined_types(he_concept).items()],
                'foreign': lambda: [(name, sa.Column(name, dt.sa_sql_type)) for _, resolved_fk in
                                    mitm_def.resolve_foreign_types(he_concept).items() for name, dt in
                                    resolved_fk.items()],
                'attributes': lambda: [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in
                                       zip(he.attributes, he.attribute_dtypes)],
            }, additional_column_generators=(_gen_within_concept_id_col,),
                                                   schema_item_generators=(
                                                       _gen_unique_constraint, _gen_pk_constraint, _gen_index,
                                                       _gen_foreign_key_constraints),
                                                   override_schema=schema_name)

            if he_concept not in type_tables:
                type_tables[he_concept] = {}
            type_tables[he_concept][he.type_name] = t

    if view_generators is not None:
        for generator in view_generators:
            for name, queryable in generator(header.mitm, concept_tables, type_tables):
                views[name] = create_view(name, queryable, meta, schema=schema_name)

    return SQLRepresentationSchema(meta=meta, concept_tables=concept_tables, type_tables=type_tables, views=views)


EngineOrConnection = sa.Engine | sa.Connection


@contextmanager
def _nested_conn(bind: EngineOrConnection) -> Generator[sa.Connection, None, None]:
    if isinstance(bind, sa.Engine):
        yield bind.connect()
    elif isinstance(bind, sa.Connection):
        with bind.begin_nested():
            yield bind


def insert_db_schema(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    sql_rep_schema.meta.create_all(bind=bind, checkfirst=False)


def _df_to_records(df: pd.DataFrame, cols: Sequence[str], additional_cols: dict[str, Any] | None = None) -> list[
    dict[str, Any]]:
    if additional_cols:
        df = df.assign(**additional_cols)
    return df[[c for c in cols if c in df.columns]].to_dict('records')


def _df_to_table_records(df: pd.DataFrame, table: sa.Table, additional_cols: dict[str, Any] | None = None) -> list[
    dict[str, Any]]:
    return _df_to_records(df, (c.name for c in table.columns), additional_cols=additional_cols)


def insert_db_instances(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, mitm_data: MITMData) -> None:
    from mitm_tooling.transformation.df import mitm_data_into_mitm_dataframes
    h = mitm_data.header
    mitm = mitm_data.header.mitm
    mitm_def = get_mitm_def(mitm)
    mitm_dataframes = mitm_data_into_mitm_dataframes(mitm_data)
    with _nested_conn(bind) as conn:
        for concept, typed_dfs in mitm_dataframes:
            concept_properties, concept_relations = mitm_def.get(concept)
            for type_name, type_df in typed_dfs.items():

                parent_concept = mitm_def.get_parent(concept)
                t_concept = sql_rep_schema.concept_tables[parent_concept]

                # if not has_natural_pk(mitm, concept):
                # TODO not pretty..
                # ideally, I'd use the returned "inserted_pk"
                # values from the bulk insertion with an autoincrement id col
                # but apparently almost no DBABI drivers support this

                concept_id_col_name = _get_unique_id_col_name(parent_concept)
                max_id = conn.execute(sa.select(func.max(t_concept.columns[concept_id_col_name]))).scalar() or 0
                no_rows_to_insert = len(type_df)
                artificial_ids = pd.RangeIndex(start=max_id + 1, stop=max_id + 1 + no_rows_to_insert,
                                               name=concept_id_col_name)
                type_df[concept_id_col_name] = artificial_ids
                # type_df = type_df.assign({concept_id_col_name : artificial_ids})

                conn.execute(t_concept.insert(), _df_to_table_records(type_df, t_concept))

                if has_type_tables(mitm, concept):
                    # generated_ids = conn.execute(sa.select(t_concept.columns[concept_id_col_name])).scalars()

                    t_type = sql_rep_schema.type_tables[concept][type_name]
                    conn.execute(t_type.insert(), _df_to_table_records(type_df, t_type))

        conn.commit()


def insert_mitm_data(bind: EngineOrConnection, sql_rep_schema, mitm_data: MITMData) -> None:
    insert_db_schema(bind, sql_rep_schema)
    insert_db_instances(bind, sql_rep_schema, mitm_data)


def mk_sqlite(mitm_data: MITMData, file_path: FilePath | None = ':memory:', autoclose: bool = True) -> tuple[
    sa.Engine, SQLRepresentationSchema]:
    engine = create_sa_engine(AnyUrl(f'sqlite:///{str(file_path)}'), poolclass=StaticPool)
    sql_rep_schema = mk_sql_rep_schema(mitm_data.header)
    insert_mitm_data(engine, sql_rep_schema, mitm_data)
    # print([f'{t.name}: {t.columns} {t.constraints}' for ts in sql_rep_schema.type_tables.values() for t in ts.values()])
    if autoclose:
        engine.dispose()
    return engine, sql_rep_schema
