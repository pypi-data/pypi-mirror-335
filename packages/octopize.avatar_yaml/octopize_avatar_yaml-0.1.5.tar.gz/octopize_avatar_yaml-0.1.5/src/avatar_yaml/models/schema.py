from dataclasses import dataclass
from enum import StrEnum

from avatar_yaml.models.common import Metadata, ModelKind


class ColumnType(StrEnum):
    INT = "int"
    BOOL = "bool"
    CATEGORY = "category"
    NUMERIC = "float"
    DATETIME = "datetime"


@dataclass(frozen=True)
class TableDataInfo:
    volume: str
    file: str


@dataclass(frozen=True)
class ColumnInfo:
    field: str
    type: ColumnType | None = None
    value_type: str | None = None
    identifier: bool | None = None
    primary_key: bool | None = None
    time_series_time: bool | None = None


@dataclass(frozen=True)
class LinkMethod:
    LINEAR_SUM_ASSIGNMENT = "linear_sum_assignment"
    MINIMUM_DISTANCE_ASSIGNMENT = "minimum_distance_assignment"
    SENSITIVE_ORIGINAL_ORDER_ASSIGNMENT = "sensitive_original_order_assignment"
    TIME_SERIES = "time_series"


@dataclass(frozen=True)
class TableLinkInfoSpec:
    """Destination part of a table link."""

    table: str
    field: str


@dataclass(frozen=True)
class TableLinkInfo:
    """A link from a field to a field in another table."""

    field: str
    to: TableLinkInfoSpec
    method: LinkMethod


@dataclass(frozen=False)
class TableInfo:
    name: str
    data: TableDataInfo | None = None
    individual_level: bool = False
    avatars_data: TableDataInfo | None = None
    columns: list[ColumnInfo] | None = None
    links: list[TableLinkInfo] | None = None


@dataclass(frozen=True)
class SchemaSpec:
    tables: list[TableInfo]
    schema_ref: str | None = None


@dataclass(frozen=True)
class Schema:
    kind: ModelKind
    metadata: Metadata
    spec: SchemaSpec


def get_schema(name: str, tables: list[TableInfo], schema_ref: str | None = None) -> Schema:
    return Schema(
        kind=ModelKind.SCHEMA,
        metadata=Metadata(name=name),
        spec=SchemaSpec(
            tables=tables,
            schema_ref=schema_ref,
        ),
    )
