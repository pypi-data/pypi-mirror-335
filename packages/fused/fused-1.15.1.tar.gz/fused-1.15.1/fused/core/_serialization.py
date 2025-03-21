from __future__ import annotations

import json
import warnings
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Optional

from fused._environment import infer_display_method
from fused._options import options as OPTIONS
from fused.warnings import FusedWarning

if TYPE_CHECKING:
    import pandas as pd


def deserialize_tiff(content: bytes):
    import rasterio
    import rioxarray
    import xarray as xr

    with NamedTemporaryFile(
        dir=OPTIONS.temp_directory, prefix="udf_result", suffix=".tiff"
    ) as ntmp:
        with open(ntmp.name, "wb") as f:
            f.write(content)
        with rasterio.open(ntmp.name) as dataset:
            rda = rioxarray.open_rasterio(
                dataset,
                masked=True,
            )
            metadata = dataset.tags(ns="fused")
        orig_type = metadata.get("orig_type")
        if orig_type == "numpy.ndarray":
            data = rda.values
            if len(json.loads(metadata["shape"])) < rda.ndim:
                data = data.squeeze()
            if "bounds" in metadata:
                bounds = json.loads(metadata["bounds"])
                data = (data, bounds)
        elif orig_type == "xarray.DataArray":
            data = rda
        else:
            key = metadata.get("key") or "image"
            data = xr.Dataset({key: rda})
    return data


def deserialize_png(content: bytes):
    import xarray as xr
    from PIL import Image

    display_method = infer_display_method(None, None)
    if display_method.show_widget:
        from IPython.display import Image as IPythonImage
        from IPython.display import display

        display(IPythonImage(data=content, format="png"))

    image = Image.open(BytesIO(content))
    width, height = image.size
    if len(image.getbands()) == 1:
        image_data = list(image.getdata())
        image_data = [
            image_data[i : i + width] for i in range(0, len(image_data), width)
        ]
        data_array = xr.DataArray(image_data, dims=["y", "x"])
    else:
        image_data = []
        for band in range(len(image.getbands())):
            band_data = list(image.getdata(band=band))
            band_data = [
                band_data[i : i + width] for i in range(0, len(band_data), width)
            ]
            image_data.append(band_data)
        data_array = xr.DataArray(image_data, dims=["band", "y", "x"])

    # Create the dataset with image, latitude, and longitude data
    dataset = xr.Dataset({"image": data_array})

    return dataset


def deserialize_parquet(content: bytes):
    import pyarrow.parquet as pq

    output_df: Optional[pd.DataFrame] = None

    res_buf = BytesIO(content)

    meta = pq.read_metadata(res_buf)
    if b"geo" in meta.metadata:
        try:
            import geopandas as gpd

            output_df = gpd.read_parquet(res_buf)
        except ValueError as e:
            warnings.warn(
                f"Result has geo metadata but could not be loaded in GeoPandas: {e}",
                FusedWarning,
            )
    if output_df is None:
        import pandas as pd

        output_df = pd.read_parquet(res_buf)

    # Force all column names to be strings
    output_df.columns = [str(x) for x in output_df.columns]

    return output_df


def deserialize_json(content: bytes):
    if content == b"":
        return None

    # TODO: Read X-Fused-Orig-Type header here too
    return json.loads(content)
