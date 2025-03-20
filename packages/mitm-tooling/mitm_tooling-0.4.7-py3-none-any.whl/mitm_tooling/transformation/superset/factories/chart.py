from uuid import UUID

from .utils import mk_uuid
from ..definitions import SupersetChartDef, SupersetVizType, ChartParams, QueryContext


def mk_chart_def(name: str, dataset_uuid: UUID, viz_type: SupersetVizType, params: ChartParams,
                 query_context: QueryContext, uuid: UUID | None = None, **kwargs) -> SupersetChartDef:
    return SupersetChartDef(
        slice_name=name,
        viz_type=viz_type,
        dataset_uuid=dataset_uuid,
        params=params,
        query_context=query_context,
        uuid=uuid or mk_uuid(),
        **kwargs
    )


