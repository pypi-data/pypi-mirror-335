from typing import Annotated

import pydantic

from . import SupersetDefFile, StrUUID, SupersetVizType, QueryContext, StrUrl
from .core import *




class ChartParams(FormData):
    datasource: str | DatasourceIdentifier
    viz_type: SupersetVizType
    groupby: list[str] = pydantic.Field(default_factory=list)
    adhoc_filters: list[SupersetAdhocFilter] = pydantic.Field(default_factory=list)
    row_limit: int = 10000
    sort_by_metric: bool = True
    color_scheme: ColorScheme = 'supersetColors'
    show_legend: bool = True
    legendType: str = 'scroll'
    legendOrientation: str = 'top'
    extra_form_data: dict[str, Any] = pydantic.Field(default_factory=dict)
    slice_id: SupersetId | None = None
    dashboards: list[SupersetId] = pydantic.Field(default_factory=list)


class PieChartParams(ChartParams):
    viz_type: Literal[SupersetVizType.PIE] = SupersetVizType.PIE
    metric: SupersetAdhocMetric
    show_labels_threshold: int = 5
    show_labels: bool = True
    labels_outside: bool = True
    outerRadius: int = 70
    innerRadius: int = 30
    label_type: str = 'key'
    number_format: str = 'SMART_NUMBER'
    date_format: str = 'smart_date'


class TimeSeriesChartParams(ChartParams):
    metrics: list[SupersetAdhocMetric]
    x_axis: ColumnName
    x_axis_sort_asc: bool = True
    x_axis_sort_series: str = 'name'
    x_axis_sort_series_ascending: bool = True
    x_axis_time_format: str = 'smart_date'
    x_axis_title_margin: int = 15
    y_axis_format: str = 'SMART_NUMBER'
    y_axis_bounds: tuple[float | None, float | None] = (None, None)
    y_axis_title_margin: int = 15
    y_axis_title_position: str = 'Left'
    truncateXAxis: bool = True
    truncate_metric: bool = True
    show_empty_columns: bool = True
    comparison_type: str = 'values'
    rich_tooltip: bool = True
    showTooltipTotal: bool = True
    showTooltipPercentage: bool = True
    tooltipTimeFormat: str = 'smart_date'
    sort_series_type: str = 'sum'
    orientation: str = 'vertical'
    only_total: bool = True
    order_desc: bool = True
    time_grain_sqla: TimeGrain | None = None
    annotation_layers: list[AnnotationLayer] | None = pydantic.Field(default_factory=list)

    #
    # forecastEnabled: bool = False
    # forecastPeriods: int = 10
    # forecastInterval: float = 0.8


class TimeSeriesBarParams(TimeSeriesChartParams):
    viz_type: Literal[SupersetVizType.TIMESERIES_BAR] = SupersetVizType.TIMESERIES_BAR


class TimeSeriesLineParams(TimeSeriesChartParams):
    viz_type: Literal[SupersetVizType.TIMESERIES_LINE] = SupersetVizType.TIMESERIES_LINE
    opacity: float = 0.2
    markerSize: int = 6
    seriesType: str = 'line'


class SupersetChartDef(SupersetDefFile):
    uuid: StrUUID
    slice_name: str
    viz_type: SupersetVizType
    dataset_uuid: StrUUID
    description: str | None = None
    certified_by: str | None = None
    certification_details: str | None = None
    params: ChartParams | None = None
    query_context: QueryContext | None = None

    # query_context: Annotated[pydantic.Json | QueryContext | None, pydantic.PlainSerializer(
    #     lambda x: x.model_dump_json(by_alias=True, serialize_as_any=True, exclude_none=True) if isinstance(x,
    #                                                                                                        pydantic.BaseModel) else x,
    #     return_type=pydantic.Json), pydantic.Field(default=None)]

    cache_timeout: int | None = None
    version: str = '1.0.0'
    is_managed_externally: bool = False
    external_url: StrUrl | None = None

    @property
    def filename(self) -> str:
        return f'{self.slice_name}_{self.dataset_uuid}'
