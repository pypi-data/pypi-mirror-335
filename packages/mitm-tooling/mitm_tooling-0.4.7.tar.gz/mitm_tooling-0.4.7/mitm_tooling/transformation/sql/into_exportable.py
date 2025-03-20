from mitm_tooling.extraction.sql.data_models import TableMetaInfo, VirtualView
from mitm_tooling.extraction.sql.mapping import DataProvider, InstancesProvider, \
    HeaderEntryProvider, Exportable
from mitm_tooling.extraction.sql.mapping.mapping import ColumnContentProvider, InstancesPostProcessor
from mitm_tooling.representation import Header, SQLRepresentationSchema


def sql_rep_into_exportable(header: Header, sql_rep_schema: SQLRepresentationSchema) -> Exportable:
    data_providers = []
    for he in header.header_entries:
        if (type_t := sql_rep_schema.type_tables.get(he.concept, {}).get(he.type_name)) is not None:
            tm = TableMetaInfo.from_sa_table(type_t)
            typing_concept = header.mitm_def.get_properties(he.concept).typing_concept
            data_providers.append(DataProvider(instance_provider=InstancesProvider(
                virtual_view=VirtualView(table_meta=tm, from_clause=type_t, sa_table=type_t)),
                header_entry_provider=
                HeaderEntryProvider(concept=he.concept,
                                    table_meta=tm,
                                    kind_provider=ColumnContentProvider.from_static('kind', he.kind),
                                    type_provider=ColumnContentProvider.from_static(typing_concept,
                                                                                    he.type_name),
                                    attributes=list(he.attributes),
                                    attribute_dtypes=list(he.attribute_dtypes)),
                instance_postprocessor=InstancesPostProcessor())
            )
    return Exportable(mitm=header.mitm, data_providers=data_providers)
