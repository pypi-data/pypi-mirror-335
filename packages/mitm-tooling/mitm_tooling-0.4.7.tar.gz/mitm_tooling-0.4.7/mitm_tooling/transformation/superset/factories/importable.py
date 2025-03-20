from ..definitions import SupersetMetadataDef, SupersetDatabaseDef, SupersetDashboardDef, SupersetDatasetDef, \
    SupersetChartDef, SupersetMitMDatasetDef
from ..definitions.importable import MetadataType, SupersetAssetsImport, SupersetMitMDatasetImport


def mk_metadata(metadata_type: MetadataType) -> SupersetMetadataDef:
    return SupersetMetadataDef(type=metadata_type)


def mk_assets_import(databases: list[SupersetDatabaseDef] = None,
                     datasets: list[SupersetDatasetDef] = None,
                     charts: list[SupersetChartDef] = None,
                     dashboards: list[SupersetDashboardDef] = None,
                     metadata_type: MetadataType = MetadataType.Asset) -> SupersetAssetsImport:
    return SupersetAssetsImport(databases=databases, datasets=datasets, charts=charts, dashboards=dashboards,
                                metadata=mk_metadata(metadata_type))


def mk_mitm_dataset_import(mitm_datasets: list[SupersetMitMDatasetDef],
                           base_assets: SupersetAssetsImport) -> SupersetMitMDatasetImport:
    return SupersetMitMDatasetImport(mitm_datasets=mitm_datasets, base_assets=base_assets,
                                     metadata=mk_metadata(MetadataType.MitMDataset))
