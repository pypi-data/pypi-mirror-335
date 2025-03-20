from typing import Any

import pydantic

from mitm_tooling.transformation.superset.definitions import SupersetDefFile, StrUUID, SupersetMetric, SupersetColumn


class SupersetDatasetDef(SupersetDefFile):
    table_name: str
    schema_name: str = pydantic.Field(alias='schema')
    uuid: StrUUID
    database_uuid: StrUUID
    main_dttm_col: str | None = None
    description: str | None = None
    default_endpoint: str | None = None
    offset: int = 0
    cache_timeout: str | None = None
    catalog: str | None = None
    sql: str | None = None
    params: Any = None
    template_params: Any = None
    filter_select_enabled: bool = True
    fetch_values_predicate: str | None = None
    extra: dict[str, Any] = pydantic.Field(default_factory=dict)
    normalize_columns: bool = False
    always_filter_main_dttm: bool = False
    metrics: list[SupersetMetric] = pydantic.Field(default_factory=list)
    columns: list[SupersetColumn] = pydantic.Field(default_factory=list)
    version: str = '1.0.0'

    @property
    def filename(self):
        return self.table_name
