import warnings
from io import BytesIO
from typing import TYPE_CHECKING, Union

from fused.warnings import FusedImportWarning

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd


def parquet_to_df(b: bytes) -> Union["pd.DataFrame", "gpd.GeoDataFrame"]:
    try:
        import pandas as pd

        try:
            import geopandas as gpd

            return gpd.read_parquet(BytesIO(b))

        except:  # noqa: E722
            df = pd.read_parquet(BytesIO(b))

            if (
                "geometry" in df.columns
                and bytes in df["geometry"].apply(type).unique()
            ):
                warnings.warn(
                    FusedImportWarning(
                        "`geopandas` package is not installed so geometries are displayed as bytes instead of parsed shapes"
                    )
                )

            return df

    except ImportError:
        raise ModuleNotFoundError(
            "`pandas` package is not installed. Please install `pandas` to run this UDF."
        )
