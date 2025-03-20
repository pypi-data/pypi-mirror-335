import itertools
from collections import defaultdict
from collections.abc import Sequence, Iterable

import pandas as pd

from mitm_tooling.data_types import convert, MITMDataType
from mitm_tooling.definition import get_mitm_def, MITM, ConceptName
from mitm_tooling.definition.definition_tools import map_col_groups
from mitm_tooling.representation import MITMData, MITMDataFrames, Header
from mitm_tooling.representation import mk_concept_file_header
from mitm_tooling.representation.common import guess_k_of_header_df, mk_header_file_columns


def unpack_concept_table_as_typed_dfs(header: Header, concept: ConceptName, df: pd.DataFrame) -> dict[
    str, pd.DataFrame]:
    mitm_def = get_mitm_def(header.mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    with_header_entry = {}
    if concept_properties.is_abstract:  # e.g. MAED.observation
        for (key, typ), idx in df.groupby(['kind', concept_properties.typing_concept]).groups.items():
            key, type_name = str(key), str(typ)
            specific_concept = mitm_def.inverse_concept_key_map[key]
            he = header.get(specific_concept, type_name)
            assert he is not None, 'missing type entry in header'
            with_header_entry[(specific_concept, type_name)] = (he, df.loc[idx])
    else:
        for typ, idx in df.groupby(concept_properties.typing_concept).groups.items():
            type_name = str(typ)
            he = header.get(concept, type_name)
            assert he is not None, 'missing type entry in header'
            with_header_entry[(concept, type_name)] = (he, df.loc[idx])

    res = {}
    for (concept, type_name), (he, type_df) in with_header_entry.items():
        k = he.get_k()
        base_cols, base_dts = mk_concept_file_header(header.mitm, concept, 0)
        normal_form_cols, _ = mk_concept_file_header(header.mitm, concept, k)
        type_df = type_df.reindex(columns=normal_form_cols)

        unpacked_cols = list(base_cols) + list(he.attributes)
        unpacked_dts = base_dts | dict(zip(he.attributes, he.attribute_dtypes))
        type_df.columns = unpacked_cols

        res[he.type_name] = convert.convert_df(type_df, unpacked_dts)

    return res


def mitm_data_into_mitm_dataframes(mitm_data: MITMData) -> MITMDataFrames:
    mitm_data = mitm_data.as_specialized()
    return MITMDataFrames(header=mitm_data.header,
                          dfs={concept: unpack_concept_table_as_typed_dfs(mitm_data.header, concept, df) for concept, df
                               in
                               mitm_data})
