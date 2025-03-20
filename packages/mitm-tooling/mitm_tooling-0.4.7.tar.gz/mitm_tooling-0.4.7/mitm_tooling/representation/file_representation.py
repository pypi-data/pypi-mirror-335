import pandas as pd

from mitm_tooling.data_types.convert import convert_df
from mitm_tooling.definition import MITM, ConceptName
from mitm_tooling.utilities.io_utils import DataSink, DataSource, use_for_pandas_io, FilePath, ensure_directory_exists
from .common import guess_k_of_header_df
from .common import mk_header_file_columns, mk_concept_file_header


def write_header_file(df: pd.DataFrame, sink: DataSink) -> None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    df.to_csv(sink, header=True, index=False, sep=';')


def write_data_file(df: pd.DataFrame, sink: DataSink, append: bool = False) -> None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    df.to_csv(sink, header=not append, index=False, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z')


def read_header_file(source: DataSource, normalize: bool = False) -> pd.DataFrame:
    with use_for_pandas_io(source) as f:
        df = pd.read_csv(f, sep=';')
        if normalize:
            k = guess_k_of_header_df(df)
            df = df.astype(pd.StringDtype()).reindex(columns=mk_header_file_columns(k))
        return df


def read_data_file(source: DataSource, target_mitm: MITM | None = None, target_concept: ConceptName | None = None,
                   normalize: bool = False) -> pd.DataFrame:
    with use_for_pandas_io(source) as f:
        df = pd.read_csv(f, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z', low_memory=False)
        if normalize and target_mitm and target_concept:
            k = guess_k_of_header_df(df)
            cols, column_dts = mk_concept_file_header(target_mitm, target_concept, k)
            df = df.reindex(columns=cols)
            convert_df(df, column_dts, inplace=True)
        return df
