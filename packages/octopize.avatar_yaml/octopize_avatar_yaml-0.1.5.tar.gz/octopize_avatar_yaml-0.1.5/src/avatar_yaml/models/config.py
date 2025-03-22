from typing import Any

from avatar_yaml.models.common import Metadata, ModelKind
from avatar_yaml.models.parameters import (
    AvatarizationParameters,
    PrivacyMetricsParameters,
    ReportParameters,
    ReportParametersSpec,
    Results,
    SignalMetricsParameters,
    TimeSeriesParameters,
    create_parameters,
    get_avatarization_parameters,
    get_privacy_metrics_parameters,
    get_signal_metrics_parameters,
)
from avatar_yaml.models.schema import (
    ColumnInfo,
    ColumnType,
    Schema,
    TableDataInfo,
    TableInfo,
    TableLinkInfo,
    TableLinkInfoSpec,
    get_schema,
)
from avatar_yaml.models.volume import Volume, VolumeSpec
from avatar_yaml.yaml_utils import aggregate_yamls, to_yaml
from pydantic import BaseModel

AVATARIZATION_NAME = "avat-name"
NAME = "name"


class Config(BaseModel):
    set_name: str
    volume: Volume | None = None
    results_volume: Volume | None = None
    original_schema: Schema | None = None
    avatar_schema: Schema | None = None
    tables: dict[str, TableInfo] = {}
    avatar_tables: dict[str, TableInfo] = {}
    avatarization: dict[str, AvatarizationParameters] = {}
    time_series: dict[str, TimeSeriesParameters] = {}
    privacy_metrics: dict[str, PrivacyMetricsParameters] = {}
    signal_metrics: dict[str, SignalMetricsParameters] = {}
    results: Results | None = None
    report: ReportParameters | None = None
    seed: int | None = None

    def _schema_name(self):
        return (
            self.original_schema.metadata.name
            if self.original_schema and self.original_schema.metadata.name
            else self.set_name
        )

    def _avatar_schema_name(self):
        return (
            self.avatar_schema.metadata.name
            if self.avatar_schema and self.original_schema.metadata.name
            else self.set_name + "_avatarized"
        )

    def create_schema(self, name: str, tables: list[TableInfo] | None = None):
        if tables is None:
            tables = list(self.tables.values())
        self.original_schema = get_schema(name, tables)

    def create_avatar_schema(self, name: str, tables: list[TableInfo], schema_ref: str):
        if schema_ref is not self._schema_name() or not self.original_schema:
            raise ValueError("Expected schema to be created before setting an avatar schema")
        self.avatar_schema = get_schema(name, tables, schema_ref)

    def create_table(
        self,
        table_name: str,
        original_volume: str,
        original_file: str,
        avatar_volume: str | None = None,
        avatar_file: str | None = None,
        primary_key: str | None = None,
        foreign_keys: list | None = None,
        time_series_time: str | None = None,
        types: dict[str, ColumnType] | None = None,
        individual_level: bool = False,
    ):
        columns_infos = []

        if time_series_time:
            columns_infos.append(
                ColumnInfo(
                    field=time_series_time,
                    time_series_time=True,
                    type=types.get(time_series_time) if types else None,
                )
            )

        if primary_key:
            columns_infos.append(
                ColumnInfo(
                    field=primary_key,
                    primary_key=True,
                    type=types.get(primary_key) if types else None,
                )
            )

        if foreign_keys:
            for foreign_key in foreign_keys:
                columns_infos.append(
                    ColumnInfo(
                        field=foreign_key,
                        identifier=True,
                        type=types.get(foreign_key) if types else None,
                    )
                )

        if types:
            for column_name, column_type in types.items():
                if column_name not in {primary_key, time_series_time, *(foreign_keys or [])}:
                    columns_infos.append(ColumnInfo(field=column_name, type=column_type))

        table_info = TableInfo(
            name=table_name,
            data=TableDataInfo(original_volume, original_file),
            columns=columns_infos,
            individual_level=individual_level,
        )
        self.tables[table_name] = table_info

        if avatar_volume and avatar_file:
            self.create_avatar_table(table_name, avatar_volume, avatar_file)

    def create_avatar_table(self, table_name, avatar_volume, avatar_file):
        if table_name not in self.tables:
            raise ValueError(
                f"Expected table `{table_name}` to be created before setting an avatar table"
            )
        table_info_avatar = TableInfo(
            name=table_name,
            avatars_data=TableDataInfo(avatar_volume, avatar_file),
        )
        self.avatar_tables[table_name] = table_info_avatar

    def create_link(self, parent_table_name, child_table_name, parent_field, child_field, method):
        if parent_table_name not in self.tables:
            raise ValueError(
                f"Expected table `{parent_table_name}` to be created before linking it to `{child_table_name}`"
            )
        if child_table_name not in self.tables:
            raise ValueError(
                f"Expected table `{child_table_name}` to be created before linking it to `{parent_table_name}`"
            )
        if parent_field not in [
            column.field for column in self.tables[parent_table_name].columns if column.primary_key
        ]:
            raise ValueError(
                f"Expected field `{parent_field}` to be the primary key of the table `{parent_table_name}`"
            )
        if child_field not in [
            column.field for column in self.tables[child_table_name].columns if column.identifier
        ]:
            raise ValueError(
                f"Expected field `{child_field}` to be an identifier in table `{child_table_name}`"
            )

        parent_table = self.tables[parent_table_name]
        link_info = TableLinkInfo(
            field=parent_field,
            to=TableLinkInfoSpec(table=child_table_name, field=child_field),
            method=method,
        )

        if parent_table.links is None:
            parent_table.links = [link_info]
        else:
            parent_table.links.append(link_info)

    def create_parameters(
        self,
        table_name: str,
        k: int | None = None,
        ncp: int | None = None,
        use_categorical_reduction: bool | None = None,
        column_weights: dict[str, float] | None = None,
        exclude_variables: dict[str, Any] | None = None,
        imputation: dict[str, Any] | None = None,
        projection: dict[str, Any] | None = None,
        alignment: dict[str, Any] | None = None,
        known_variables: list[str] | None = None,
        target: str | None = None,
        closest_rate_percentage_threshold: float | None = None,
        closest_rate_ratio_threshold: float | None = None,
        categorical_hidden_rate_variables: list[str] | None = None,
    ):
        if table_name not in self.tables:
            raise ValueError(
                f"Expected table `{table_name}` to be created before setting parameters"
            )

        avatarization, time_series, privacy_metrics, signal_metrics = create_parameters(
            k=k,
            ncp=ncp,
            use_categorical_reduction=use_categorical_reduction,
            column_weights=column_weights,
            exclude_variables=exclude_variables,
            imputation=imputation,
            projection=projection,
            alignment=alignment,
            known_variables=known_variables,
            target=target,
            closest_rate_percentage_threshold=closest_rate_percentage_threshold,
            closest_rate_ratio_threshold=closest_rate_ratio_threshold,
            categorical_hidden_rate_variables=categorical_hidden_rate_variables,
        )

        if avatarization:
            self.avatarization[table_name] = avatarization
        if time_series:
            self.time_series[table_name] = time_series
        if privacy_metrics:
            self.privacy_metrics[table_name] = privacy_metrics
        if signal_metrics:
            self.signal_metrics[table_name] = signal_metrics

    def create_volume(self, name, url):
        self.volume = Volume(
            kind=ModelKind.VOLUME,
            metadata=Metadata(name=name),
            spec=VolumeSpec(url=url),
        )

    def create_results_volume(self, name, url):
        self.results_volume = Volume(
            kind=ModelKind.VOLUME,
            metadata=Metadata(name=name),
            spec=VolumeSpec(url=url),
        )

    def create_results(
        self,
        path: str | None = None,
        format: str | None = None,
        name_template: str | None = None,
    ):
        if not self.results_volume:
            raise ValueError("Expected results volume to be created before setting results")
        self.results = Results(
            volume=self.results_volume.metadata.name,
            path=path,
            format=format,
            name_template=name_template,
        )

    def create_report(self, report_name: str | None = None, report_type: str = "basic"):
        report_name = report_name or "report"
        self.report = ReportParameters(
            kind=ModelKind.REPORT,
            metadata=Metadata(name=report_name),
            spec=ReportParametersSpec(report_type=report_type, results=self.results),
        )

    def get_avatarization(self, name: str = "avatarization") -> str:
        if not self.avatarization:
            raise ValueError("No avatarization parameters have been set")
        if not self.results:
            raise ValueError("No results have been set")
        if self.time_series == {}:
            time_series = None
        else:
            time_series = self.time_series

        return get_avatarization_parameters(
            metadata=Metadata(name=name),
            schema_name=self._schema_name(),
            avatarization=self.avatarization,
            time_series=time_series,
            seed=self.seed,
            results=self.results,
        )

    def get_signal_metrics(
        self, name: str = "signal", avatarization_ref: str = "avatarization"
    ) -> str:
        if self.time_series == {}:
            time_series = None
        else:
            time_series = self.time_series
        if self.signal_metrics == {}:
            signal_metrics = None
        else:
            signal_metrics = self.signal_metrics
        return get_signal_metrics_parameters(
            metadata=Metadata(name=name),
            schema_name=self._avatar_schema_name(),
            avatarization_ref=avatarization_ref,
            signal_metrics=signal_metrics,
            time_series=time_series,
            seed=self.seed,
            results=self.results,
        )

    def get_privacy_metrics(
        self, name: str = "privacy", avatarization_ref: str = "avatarization"
    ) -> str:
        if self.time_series == {}:
            time_series = None
        else:
            time_series = self.time_series
        if self.privacy_metrics == {}:
            privacy_metrics = None
        else:
            privacy_metrics = self.privacy_metrics
        return get_privacy_metrics_parameters(
            metadata=Metadata(name=name),
            schema_name=self._avatar_schema_name(),
            avatarization_ref=avatarization_ref,
            privacy_metrics=privacy_metrics,
            time_series=time_series,
            seed=self.seed,
            results=self.results,
        )

    def get_parameters(self) -> str:
        return aggregate_yamls(
            self.get_avatarization(), self.get_privacy_metrics(), self.get_signal_metrics()
        )

    def get_report(self) -> str:
        if self.report is None:
            self.create_report()
        return to_yaml(self.report)  # type: ignore[arg-type]

    def get_schema(self) -> str:
        if self.original_schema is None:
            self.create_schema(self._schema_name(), list(self.tables.values()))
        return to_yaml(self.original_schema)  # type: ignore[arg-type]

    def get_avatar_schema(self) -> str:
        if self.avatar_schema is None:
            self.create_avatar_schema(
                self._avatar_schema_name(),
                list(self.avatar_tables.values()),
                schema_ref=self._schema_name(),
            )
        return to_yaml(self.avatar_schema)  # type: ignore[arg-type]

    def get_volume(self) -> str:
        if not self.volume:
            raise ValueError("No volume has been set")
        return to_yaml(self.volume)

    def get_result_volume(self) -> str:
        if not self.results_volume:
            raise ValueError("No results volume has been set")
        return to_yaml(self.results_volume)

    def get_yaml(self):
        yaml = aggregate_yamls(
            self.get_volume(),
            self.get_result_volume(),
            self.get_schema(),
            self.get_avatar_schema(),
            self.get_parameters(),
            self.get_report(),
        )
        return yaml
