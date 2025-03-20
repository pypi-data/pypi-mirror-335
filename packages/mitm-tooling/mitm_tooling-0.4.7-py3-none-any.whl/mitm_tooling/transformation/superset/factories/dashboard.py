from uuid import UUID

from mitm_tooling.representation import ColumnName
from mitm_tooling.transformation.superset.definitions import SupersetChartDef
from mitm_tooling.transformation.superset.factories.utils import mk_uuid, mk_short_uuid_str
from ..definitions.dashboard import *


def mk_filter_config(name: str, target_cols: list[tuple[ColumnName, UUID]], ft: FilterType = FilterType.FILTER_SELECT,
                     control_values: ControlValues = ControlValues()) -> NativeFilterConfig:
    return NativeFilterConfig(
        id=f'NATIVE_FILTER-{mk_short_uuid_str()}',
        name=name,
        filterType=ft,
        controlValues=control_values,
        targets=[
            ColumnOfDataset(column=ColName(name=c), datasetUuid=ds_uuid) for c, ds_uuid in (target_cols or [])
        ]
    )


def mk_dashboard_base(header_text: str, row_ids: list[DashboardInternalID]) -> DashboardPositionData:
    return {
        'DASHBOARD_VERSION_KEY': 'v2',
        'HEADER_ID': DashboardHeader(id='HEADER_ID', meta=HeaderMeta(text=header_text)),
        'ROOT_ID': DashboardRoot(id='ROOT_ID', children=['GRID_ID']),
        'GRID_ID': DashboardGrid(id='GRID_ID', children=row_ids),
    }


def mk_dashboard_row(children_ids: list[DashboardInternalID], id: DashboardInternalID | None = None) -> DashboardRow:
    return DashboardRow(id=id or f'ROW-{mk_short_uuid_str()}', children=children_ids)


def mk_dashboard_chart(chart_uuid: UUID, width: int, height: int, slice_name: str | None = None,
                       id: DashboardInternalID | None = None) -> DashboardChart:
    return DashboardChart(id=id or f'CHART-{mk_short_uuid_str()}',
                          meta=ChartMeta(uuid=chart_uuid, width=width, height=height, sliceName=slice_name))


def chart_def_into_dashboard_chart(chart_def: SupersetChartDef, width: int, height: int) -> DashboardChart:
    return mk_dashboard_chart(chart_uuid=chart_def.uuid, width=width, height=height)


def mk_dashboard_position_data(header_text: str, chart_grid: list[list[DashboardChart]]) -> DashboardPositionData:
    row_ids = []
    elements = {}
    for row in chart_grid:
        within_row_ids = []
        for chart in row:
            # mk_dashboard_chart()
            elements[chart.id] = chart
            within_row_ids.append(chart.id)
        row = mk_dashboard_row(within_row_ids)
        elements[row.id] = row
        row_ids.append(row.id)
    position_base = mk_dashboard_base(header_text=header_text, row_ids=row_ids)

    res = position_base | elements
    return res


def mk_dashboard_metadata(native_filters: list[NativeFilterConfig]) -> DashboardMetadata:
    return DashboardMetadata(native_filter_configuration=native_filters)


def mk_dashboard_def(dashboard_title, chart_grid: list[list[DashboardChart]], native_filters: list[NativeFilterConfig],
                     description: str | None = None, uuid: UUID | None = None) -> SupersetDashboardDef:
    position_data = mk_dashboard_position_data(dashboard_title, chart_grid)
    dashboard_metadata = mk_dashboard_metadata(native_filters=native_filters)
    return SupersetDashboardDef(
        dashboard_title=dashboard_title,
        position=position_data,
        metadata=dashboard_metadata,
        description=description,
        uuid=uuid or mk_uuid(),
    )
