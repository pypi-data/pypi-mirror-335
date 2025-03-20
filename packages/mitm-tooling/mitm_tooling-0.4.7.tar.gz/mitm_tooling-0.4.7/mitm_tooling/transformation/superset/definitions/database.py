from typing import Any

import pydantic

from mitm_tooling.transformation.superset.definitions import SupersetDefFile, StrUrl, StrUUID


class SupersetDatabaseDef(SupersetDefFile):
    database_name: str
    sqlalchemy_uri: StrUrl
    uuid: StrUUID
    # verbose_name : str | None = None
    cache_timeout: str | None = None
    expose_in_sqllab: bool = True
    allow_run_async: bool = False
    allow_ctas: bool = False
    allow_cvas: bool = False
    allow_dml: bool = False
    allow_file_upload: bool = False
    extra: dict[str, Any] = pydantic.Field(default_factory=lambda: {
        'allows_virtual_table_explore': True
    })
    impersonate_user: bool = False
    version: str = '1.0.0'
    ssh_tunnel: None = None

    @property
    def filename(self):
        return self.database_name
