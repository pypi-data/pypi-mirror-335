from abc import ABC, abstractmethod
from typing import Any, Self
from uuid import UUID

import pydantic

from .definitions import SupersetDatabaseDef, SupersetMitMDatasetDef, \
    SupersetChartDef, SupersetDashboardDef, SupersetAssetsImport, SupersetDatasetDef, \
    SupersetMitMDatasetImport, SupersetDefFolder, DatasourceIdentifier
from .factories.importable import mk_assets_import, mk_mitm_dataset_import
from ...representation import TableName


class SupersetAssetBundle(SupersetDefFolder, ABC):
    @abstractmethod
    def to_import(self) -> SupersetAssetsImport | SupersetMitMDatasetImport:
        pass

    @property
    def folder_dict(self) -> dict[str, Any]:
        return self.to_import().folder_dict


class SupersetDatasourceBundle(SupersetAssetBundle):
    database: SupersetDatabaseDef
    datasets: list[SupersetDatasetDef] = pydantic.Field(default_factory=list)

    @property
    def database_uuid(self) -> UUID:
        return self.database.uuid

    @property
    def dataset_uuids(self) -> list[UUID]:
        return [ds.uuid for ds in self.datasets]

    @property
    def placeholder_dataset_identifiers(self) -> dict[TableName, DatasourceIdentifier]:
        return {ds.table_name: DatasourceIdentifier(uuid=ds.uuid) for ds in self.datasets}

    def to_import(self) -> SupersetAssetsImport:
        return mk_assets_import(databases=[self.database], datasets=self.datasets)


class SupersetVisualizationBundle(SupersetAssetBundle):
    charts: list[SupersetChartDef] = pydantic.Field(default_factory=list)
    dashboards: list[SupersetDashboardDef] = pydantic.Field(default_factory=list)

    @property
    def chart_uuids(self) -> list[UUID]:
        return [ch.uuid for ch in self.charts]

    @property
    def dashboard_uuids(self) -> list[UUID]:
        return [da.uuid for da in self.dashboards]

    def to_import(self) -> SupersetAssetsImport:
        return mk_assets_import(charts=self.charts, dashboards=self.dashboards)


class SupersetMitMDatasetBundle(SupersetAssetBundle):
    mitm_dataset: SupersetMitMDatasetDef
    datasource_bundle: SupersetDatasourceBundle
    visualization_bundle: SupersetVisualizationBundle = pydantic.Field(default_factory=SupersetVisualizationBundle)

    def with_visualization_bundle(self, visualization_bundle: SupersetVisualizationBundle) -> Self:
        mitm_ds = self.mitm_dataset
        from mitm_tooling.transformation.superset.factories.mitm_dataset import mk_mitm_dataset
        return self.__class__(
            mitm_dataset=mk_mitm_dataset(name=mitm_ds.dataset_name, mitm=mitm_ds.mitm, uuid=mitm_ds.uuid,
                                         database_uuid=self.datasource_bundle.database_uuid,
                                         table_uuids=self.datasource_bundle.dataset_uuids,
                                         slice_uuids=visualization_bundle.chart_uuids,
                                         dashboard_uuids=visualization_bundle.dashboard_uuids),
            datasource_bundle=self.datasource_bundle,
            visualization_bundle=visualization_bundle)

    def to_import(self) -> SupersetMitMDatasetImport:
        base_assets = mk_assets_import(databases=[self.datasource_bundle.database],
                                       datasets=self.datasource_bundle.datasets,
                                       charts=self.visualization_bundle.charts,
                                       dashboards=self.visualization_bundle.dashboards)
        return mk_mitm_dataset_import(mitm_datasets=[self.mitm_dataset], base_assets=base_assets)
