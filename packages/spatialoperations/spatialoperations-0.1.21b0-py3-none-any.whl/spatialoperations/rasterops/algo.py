from .rasterops import DataCube
import geopandas as gpd
import pandas as pd
import numpy as np
import logging
from coastal_resilience_utilities.summary_stats.summary_stats import summary_stats2


def summary_stats(
    dc: DataCube,
    var: str,
    gdf: gpd.GeoDataFrame,
    group: str = None,
    stats=["sum", "count"],
    return_with_fields: bool = False,
):
    logging.info(f"Running summary stats for {var}")
    tiles = dc.get_xarray_tiles(var, group=group)
    gdf = gdf.reset_index()

    buff = []
    for da, idx, tile in tiles:
        bbox = tile.boundingbox
        extent = bbox.left, bbox.right, bbox.bottom, bbox.top
        _gdf = gdf.cx[extent[0]: extent[1], extent[2]: extent[3]]
        if _gdf.shape[0] == 0:
            continue

        output = summary_stats2(_gdf, da, stats)
        buff.append(output)

    output = (
        pd.concat(buff)
        .groupby(["index", "geometry"])
        .apply(lambda x: x.apply(np.nansum))
        .reset_index()
        .set_index("index")
    )
    if return_with_fields:
        return pd.merge(
            gdf,
            output[[c for c in output.columns if c != "geometry"]],
            left_index=True,
            right_index=True,
            how="left",
        )

    else:
        gdf["dummycolumn"] = 0
        return pd.merge(
            gdf[["dummycolumn"]],
            output[[c for c in output.columns if c != "geometry"]],
            left_index=True,
            right_index=True,
            how="left",
        ).drop(columns=["dummycolumn"])
