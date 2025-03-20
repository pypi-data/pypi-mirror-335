from enum import StrEnum
from typing import Literal

import pydantic

from . import SupersetDefFile, StrUUID, StrUrl
from .constants import StrUUID

DashboardInternalID = str


class DashboardComponentType(StrEnum):
    CHART = 'CHART'
    HEADER = 'HEADER'
    GRID = 'GRID'
    ROW = 'ROW'
    ROOT = 'ROOT'


class ComponentMeta(pydantic.BaseModel):
    pass


class DashboardComponent(pydantic.BaseModel):
    id: DashboardInternalID
    type: DashboardComponentType
    meta: ComponentMeta | None = pydantic.Field(strict=False, default=None)
    children: list[DashboardInternalID] = pydantic.Field(default_factory=list)


class HeaderMeta(ComponentMeta):
    text: str


class DashboardHeader(DashboardComponent):
    type: Literal[DashboardComponentType.HEADER] = DashboardComponentType.HEADER
    meta: HeaderMeta


class DashboardRoot(DashboardComponent):
    type: Literal[DashboardComponentType.ROOT] = DashboardComponentType.ROOT
    meta: None = None


class DashboardGrid(DashboardComponent):
    type: Literal[DashboardComponentType.GRID] = DashboardComponentType.GRID
    meta: None = None


class RowMeta(ComponentMeta):
    background: str = 'BACKGROUND_TRANSPARENT'


class DashboardRow(DashboardComponent):
    type: Literal[DashboardComponentType.ROW] = DashboardComponentType.ROW
    meta: RowMeta = RowMeta()


class ChartMeta(ComponentMeta):
    uuid: StrUUID
    width: int = pydantic.Field(ge=1, le=12)
    height: int
    chartId: int | None = None
    sliceName: str | None = None


class DashboardChart(DashboardComponent):
    type: Literal[DashboardComponentType.CHART] = DashboardComponentType.CHART
    meta: ChartMeta


DASHBOARD_VERSION_KEY_LITERAL = Literal['DASHBOARD_VERSION_KEY']

DashboardPositionData = dict[DASHBOARD_VERSION_KEY_LITERAL | DashboardInternalID, str | DashboardComponent]


class ControlValues(pydantic.BaseModel):
    enableEmptyFilter: bool = False
    defaultToFirstItem: bool | None = False
    multiSelect: bool | None = True
    searchAllOptions: bool | None = False
    inverseSelection: bool | None = False


class ColName(pydantic.BaseModel):
    name: str


class DatasetReference(pydantic.BaseModel):
    datasetUuid: StrUUID


class ColumnOfDataset(DatasetReference):
    column: ColName


class FilterType(StrEnum):
    FILTER_SELECT = 'filter_select'
    FILTER_TIME_GRAIN = 'filter_timegrain'


class NativeFilterConfig(pydantic.BaseModel):
    id: str
    name: str
    targets: list[DatasetReference | ColumnOfDataset] = pydantic.Field(default_factory=list)
    controlValues: ControlValues = pydantic.Field(default_factory=ControlValues)
    filterType: FilterType = FilterType.FILTER_SELECT
    type: str = 'NATIVE_FILTER'


class DashboardMetadata(pydantic.BaseModel):
    color_scheme: str = 'blueToGreen'
    cross_filters_enabled: bool = True
    native_filter_configuration: list[NativeFilterConfig] = pydantic.Field(default_factory=list)


class SupersetDashboardDef(SupersetDefFile):
    uuid: StrUUID
    dashboard_title: str
    position: DashboardPositionData
    metadata: DashboardMetadata
    description: str | None = None
    css: str | None = None
    slug: str | None = None
    is_managed_externally: bool | None = False
    external_url: StrUrl | None = None
    certified_by: str | None = None
    certification_details: str | None = None
    published: bool | None = False
    version: str = '1.0.0'

    @property
    def filename(self) -> str:
        return f'{self.dashboard_title}_{self.uuid}'
