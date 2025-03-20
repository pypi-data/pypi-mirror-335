from __future__ import annotations

from functools import cached_property

import itertools
import logging
import pandas as pd
import pydantic
from collections import defaultdict
from collections.abc import Iterator, Iterable, Sequence, Mapping
from mitm_tooling.data_types.data_types import MITMDataType
from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import ConceptName, MITM, TypeName
from mitm_tooling.utilities.python_utils import take_first
from pydantic import ConfigDict
from typing import Self

from .intermediate.header import HeaderEntry, Header
from .intermediate.deltas import diff_header


class MITMData(Iterable[tuple[ConceptName, pd.DataFrame]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    concept_dfs: dict[ConceptName, pd.DataFrame] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.concept_dfs.items())

    def as_generalized(self) -> Self:
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = defaultdict(list)
        for c, df in self.concept_dfs.items():
            c = mitm_def.get_parent(c)
            dfs[c].append(df)
        dfs = {c: pd.concat(dfs_, axis='rows', ignore_index=True) for c, dfs_ in dfs.items()}
        return MITMData(header=self.header, concept_dfs=dfs)

    def as_specialized(self) -> Self:
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = {}
        for c, df in self:
            if mitm_def.get_properties(c).is_abstract:
                leaf_concepts = mitm_def.get_leafs(c)

                for sub_c_key, idx in df.groupby('kind').groups.items():
                    sub_c = mitm_def.inverse_concept_key_map[str(sub_c_key)]
                    dfs[sub_c] = df.loc[idx]
            else:
                dfs[c] = df
        return MITMData(header=self.header, concept_dfs=dfs)


class StreamingConceptData(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    structure_df: pd.DataFrame
    chunk_iterators: list[Iterator[tuple[pd.DataFrame, list[HeaderEntry]]]] = pydantic.Field(default_factory=list)


class StreamingMITMData(Iterable[tuple[ConceptName, StreamingConceptData]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    data_sources: dict[ConceptName, StreamingConceptData] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.data_sources.items())

    def as_generalized(self) -> Self:
        mitm_def = get_mitm_def(self.mitm)
        combined_data_sources = defaultdict(list)
        for c, ds in self:
            combined_data_sources[mitm_def.get_parent(c)].append(ds)
        data_sources = {}
        for c, ds_list in combined_data_sources.items():
            structure_dfs = [ds.structure_df for ds in ds_list]
            assert all(
                a.equals(b) for a, b in
                zip(structure_dfs[:-1],
                    structure_dfs[1:])), f'concept {c} not generalizable in {self} (structure_dfs differ)'
            data_sources[c] = StreamingConceptData(structure_df=take_first(structure_dfs),
                                                   chunk_iterators=[it for ds in ds_list for it in ds.chunk_iterators])
        return StreamingMITMData(mitm=self.mitm, data_sources=data_sources)
