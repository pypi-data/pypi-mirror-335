import sqlalchemy as sa

TableName = str
SchemaName = str
ShortTableIdentifier = tuple[SchemaName, TableName]
QualifiedTableName = str
Queryable = sa.FromClause