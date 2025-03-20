from typing import Sequence, Literal, Iterable
from uuid import UUID

from mitm_tooling.definition import MITM
from ..common import name_plus_uuid
from ..definitions import SupersetMitMDatasetDef
from ..definitions.mitm_dataset import RelatedTable, RelatedSlice, RelatedDashboard
from ..factories.utils import mk_uuid


def mk_related_obj(kind: Literal['table', 'slice', 'dashboard'],
                   uuid: UUID) -> RelatedTable | RelatedSlice | RelatedDashboard | None:
    match kind:
        case 'table':
            return RelatedTable(table_uuid=uuid)
        case 'slice':
            return RelatedSlice(slice_uuid=uuid)
        case 'dashboard':
            return RelatedDashboard(dashboard_uuid=uuid)


def mk_related_objs(kind: Literal['table', 'slice', 'dashboard'], uuids: Iterable[UUID]) -> Iterable[RelatedTable] | \
                                                                                            Iterable[RelatedSlice] | \
                                                                                            Iterable[
                                                                                                RelatedDashboard] | None:
    if uuids:
        return [mk_related_obj(kind, uuid) for uuid in uuids]


def mk_mitm_dataset(name: str, mitm: MITM, database_uuid: UUID, table_uuids: list[UUID] | None = None,
                    slice_uuids: Sequence[UUID] | None = None, dashboard_uuids: Sequence[UUID] | None = None,
                    uuid: UUID | None = None, uniquify_name: bool = False) -> SupersetMitMDatasetDef:
    uuid = uuid or mk_uuid()
    if uniquify_name:
        name = name_plus_uuid(name, uuid)
    return SupersetMitMDatasetDef(
        dataset_name=name,
        mitm=mitm,
        uuid=uuid or mk_uuid(),
        database_uuid=database_uuid,
        tables=mk_related_objs('table', table_uuids),
        slices=mk_related_objs('slice', slice_uuids),
        dashboards=mk_related_objs('dashboard', dashboard_uuids),
    )
