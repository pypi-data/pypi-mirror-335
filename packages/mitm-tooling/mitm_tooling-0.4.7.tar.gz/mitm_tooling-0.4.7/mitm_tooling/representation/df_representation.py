from collections.abc import Iterable

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import ConceptName
from .intermediate_representation import Header


class MITMDataFrames(Iterable[tuple[str, dict[str, pd.DataFrame]]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    dfs: dict[ConceptName, dict[str, pd.DataFrame]]

    def __iter__(self):
        return iter(self.dfs.items())
