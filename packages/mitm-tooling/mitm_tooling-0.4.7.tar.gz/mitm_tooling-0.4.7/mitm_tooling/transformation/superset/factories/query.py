from ..definitions import QueryObject, QueryContext, DatasourceIdentifier, SupersetAdhocMetric, \
    QueryObjectFilterClause, FormData, FilterValues, FilterOperator, SupersetPostProcessing, \
    SupersetAdhocColumn
from mitm_tooling.representation import ColumnName


def mk_query_object_filter_clause(col: ColumnName, op: FilterOperator,
                                  val: FilterValues | None = None, **kwargs) -> QueryObjectFilterClause:
    return QueryObjectFilterClause(col=col, op=op, val=val, **kwargs)


def mk_empty_query_object_time_filter_clause() -> QueryObjectFilterClause:
    return mk_query_object_filter_clause('time', FilterOperator.TEMPORAL_RANGE)


def mk_query_object(columns: list[ColumnName | SupersetAdhocColumn],
                    metrics: list[SupersetAdhocMetric],
                    filters: list[QueryObjectFilterClause],
                    orderby: list[tuple[SupersetAdhocMetric, bool]] | None = None,
                    post_processing: list[SupersetPostProcessing] | None = None,
                    row_limit: int | None = 10_000,
                    **kwargs) -> QueryObject:
    if orderby is None:
        orderby = [(metrics[0], 0)]
    if post_processing is None:
        post_processing = []
    return QueryObject(columns=columns, metrics=metrics, filters=filters, orderby=orderby,
                       post_processing=post_processing,
                       row_limit=row_limit, **kwargs)


def mk_query_context(datasource: DatasourceIdentifier, queries: list[QueryObject], form_data: FormData,
                     **kwargs) -> QueryContext:
    return QueryContext(datasource=datasource, queries=queries, form_data=form_data, **kwargs)
