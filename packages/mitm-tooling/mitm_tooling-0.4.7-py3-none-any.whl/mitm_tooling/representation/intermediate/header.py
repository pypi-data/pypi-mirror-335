import itertools
import logging
from collections import defaultdict
from collections.abc import Sequence, Mapping
from functools import cached_property
from typing import Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.data_types.data_types import MITMDataType
from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import ConceptName, MITM, TypeName
from ..common import mk_header_file_columns, ColumnName


class HeaderEntry(pydantic.BaseModel):
    model_config = ConfigDict(frozen=True)

    concept: ConceptName
    kind: str
    type_name: TypeName
    attributes: tuple[ColumnName, ...]
    attribute_dtypes: tuple[MITMDataType, ...]

    @pydantic.model_validator(mode='after')
    def attr_check(self):
        if not len(self.attributes) == len(self.attribute_dtypes):
            raise ValueError('Length of specified attributes and their data types differs.')
        return self

    @classmethod
    def from_row(cls, row: Sequence[str], mitm: MITM) -> Self:
        kind, type_name = row[0], row[1]
        concept = get_mitm_def(mitm).inverse_concept_key_map.get(kind)
        if not concept:
            raise ValueError(f'Encountered unknown concept key: "{kind}".')

        attrs, attr_dts = [], []
        for a, a_dt in zip(row[slice(2, None, 2)], row[slice(3, None, 2)]):
            if pd.notna(a) and pd.notna(a_dt):
                attrs.append(a)
                try:
                    mitm_dt = MITMDataType(a_dt.lower()) if a_dt else MITMDataType.Unknown
                    attr_dts.append(mitm_dt)
                except ValueError as e:
                    raise ValueError(f'Encountered unrecognized data type during header import: {a_dt}.') from e

        return HeaderEntry(concept=concept, kind=kind, type_name=type_name, attributes=tuple(attrs),
                           attribute_dtypes=tuple(attr_dts))

    def get_k(self) -> int:
        return len(self.attributes)

    def to_row(self) -> list[str | None]:
        return [self.kind, self.type_name] + list(
            itertools.chain(*zip(self.attributes, map(str, self.attribute_dtypes))))


class Header(pydantic.BaseModel):
    model_config = ConfigDict(frozen=True)

    mitm: MITM
    header_entries: tuple[HeaderEntry, ...] = pydantic.Field(default_factory=tuple)

    @classmethod
    def from_df(cls, df: pd.DataFrame, mitm: MITM) -> Self:
        return Header(mitm=mitm, header_entries=tuple(
            HeaderEntry.from_row(row, mitm) for row in df.itertuples(index=False)))

    def generate_header_df(self) -> pd.DataFrame:
        k = max(map(lambda he: he.get_k(), self.header_entries), default=0)
        deduplicated = {}
        for he in self.header_entries:
            deduplicated[(he.kind, he.type_name)] = he
        lol = [he.to_row() for he in deduplicated.values()]
        return pd.DataFrame(data=lol, columns=mk_header_file_columns(k))

    def get(self, concept: ConceptName, type_name: TypeName) -> HeaderEntry | None:
        return self.as_dict.get(concept, {}).get(type_name)

    @cached_property
    def mitm_def(self):
        return get_mitm_def(self.mitm)

    @cached_property
    def as_dict(self) -> dict[ConceptName, dict[TypeName, HeaderEntry]]:
        res = defaultdict(dict)
        for he in self.header_entries:
            res[he.concept][he.type_name] = he
        return dict(res)

