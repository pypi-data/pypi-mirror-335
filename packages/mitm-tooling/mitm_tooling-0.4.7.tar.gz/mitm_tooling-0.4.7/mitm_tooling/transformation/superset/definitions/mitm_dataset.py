from mitm_tooling.definition import MITM
from mitm_tooling.representation import Header
from mitm_tooling.transformation.superset.definitions import SupersetDefFile, StrUUID, BaseSupersetDefinition, \
    SupersetId


class MitMDatasetIdentifier(BaseSupersetDefinition):
    dataset_name: str
    id: SupersetId | None = None
    uuid: StrUUID | None = None


class RelatedTable(BaseSupersetDefinition):
    table_id: SupersetId | None = None
    table_uuid: StrUUID


class RelatedSlice(BaseSupersetDefinition):
    slice_id: SupersetId | None = None
    slice_uuid: StrUUID


class RelatedDashboard(BaseSupersetDefinition):
    dashboard_id: SupersetId | None = None
    dashboard_uuid: StrUUID


class SupersetMitMDatasetDef(SupersetDefFile):
    uuid: StrUUID
    dataset_name: str
    mitm: MITM
    mitm_header: Header | None = None
    database_uuid: StrUUID
    tables: list[RelatedTable] | None = None
    slices: list[RelatedSlice] | None = None
    dashboards: list[RelatedDashboard] | None = None
    version: str = '1.0.0'

    @property
    def filename(self) -> str:
        return self.dataset_name
