from mitm_tooling.extraction.sql.data_models import SourceDBType
from mitm_tooling.extraction.sql.mapping import ConceptMapping, ForeignRelation
from mitm_tooling.representation import Header, SQLRepresentationSchema


def sql_rep_into_mappings(header: Header, sql_rep_schema: SQLRepresentationSchema) -> list[ConceptMapping]:
    mitm_def = header.mitm_def
    cms = []
    for he in header.header_entries:
        if (type_t := sql_rep_schema.type_tables[he.concept][he.type_name]) is not None:
            concept_properties, relations = mitm_def.get(he.concept)
            cms.append(
                ConceptMapping(
                    mitm=header.mitm,
                    concept=he.concept,
                    base_table=(SourceDBType.OriginalDB, type_t.schema, type_t.name),
                    kind_col='kind' if 'kind' in type_t.columns else None,
                    type_col=concept_properties.typing_concept,
                    identity_columns=list(relations.identity.keys()),
                    inline_relations=list(relations.inline_relations.keys()),
                    foreign_relations={
                        fk_name: ForeignRelation(
                            fk_columns=list(fk_info.fk_relations.keys()),
                            referred_table=(SourceDBType.OriginalDB,
                                            concept_t.schema,
                                            concept_t.name),
                        ) for fk_name, fk_info in relations.foreign.items() if
                        (concept_t := sql_rep_schema.concept_tables.get(fk_info.target_concept)) is not None
                    },
                    attributes=list(he.attributes),
                    attribute_dtypes=list(he.attribute_dtypes),
                )
            )

    return cms
