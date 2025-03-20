# Standard library imports
import logging
import os
import shutil
import sys
import uuid
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Any
import s3fs

# Third-party imports
import geopandas as gpd
import numpy as np
import numcodecs
import pandas as pd
import rioxarray as rxr
import xarray as xr
from osgeo import gdal
from shapely.geometry import Polygon
from tqdm import tqdm
from joblib import Parallel, delayed as joblib_delayed
import zarr
import json

# ODC imports
from odc.geo.geobox import GeoBox, GeoboxTiles
from odc.geo.xr import xr_zeros

# Local imports
from coastal_resilience_utilities.utils.geo import transform_point
from coastal_resilience_utilities.summary_stats.summary_stats import summary_stats2
from . import storage


# Configure logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s : %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("My Personal")
logger.propagate = True
logger.setLevel(logging.DEBUG)


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    JOBLIB = "joblib"
    DASK = "dask"

    def __getstate__(self):
        return self.value

    def __setstate__(self, state):
        self = ExecutionMode(state)  # noqa: F841

@dataclass
class DataCube:
    def __init__(
        self,
        dx: float,
        epsg: int,
        bounds: tuple[float, float, float, float],
        chunk_size: int,
        path: str,
        varnames: list[str],
        nodata: float = np.nan,
        dtype: str = "<f8",
        store_active_idxs: bool = True,
    ):
        self.dx = dx
        self.epsg = epsg
        self.bounds = bounds
        self.chunk_size = chunk_size
        self.path = path
        self.storage = storage.PlainOlZarrStore(path)
        self.varnames = varnames
        self.nodata = nodata
        self.dtype = dtype
        self.store_active_idxs = store_active_idxs
        self.__post_init__()

    def __post_init__(self):
        to_store = ["dx", "epsg", "bounds", "chunk_size", "path", "varnames", "nodata", "dtype", "store_active_idxs"]
        self.storage.save_metadata("rasterops_config", json.dumps({k: v for k, v in self.__dict__.items() if k in to_store}))

    @classmethod
    def from_zarr(cls, path: str):
        to_store = ["dx", "epsg", "bounds", "chunk_size", "path", "varnames", "nodata", "dtype", "store_active_idxs"]
        
        prefix = path.replace('s3://', '')
        s3 = s3fs.S3FileSystem(
            key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
            client_kwargs={'endpoint_url': os.getenv("AWS_ENDPOINT_URL")},
            asynchronous=True,
        )
        store = zarr.storage.FsspecStore(
            s3,
            path=prefix
        )
        conf = json.loads(zarr.group(store=store).attrs["rasterops_config"])
        conf = {k: v for k, v in conf.items() if k in to_store}

        if "id" in conf:
            del conf["id"]

        if "execution_mode" in conf:
            del conf["execution_mode"]

        return cls(**conf)

    def set_execution_mode(self, execution_mode: ExecutionMode, njobs: int = 1):
        self.execution_mode = execution_mode
        self.n_jobs = njobs

    @property
    def crs(self) -> str:
        return f"epsg:{self.epsg}"

    @property
    def geobox(self) -> GeoBox:
        return GeoBox.from_bbox(self.bounds, crs=self.crs, resolution=self.dx)

    @property
    def chunk_shape(self) -> tuple[int, int]:
        return (self.chunk_size, self.chunk_size)

    @property
    def tiles(self) -> GeoboxTiles:
        return GeoboxTiles(self.geobox, self.chunk_shape)

    def tiles_by_bounds(
        self, left: float, bottom: float, right: float, top: float
    ) -> GeoboxTiles:
        """
        Filter tiles to given bounds, and return the tile indexes
        """
        for idx in self.tiles._all_tiles():
            tile = self.tiles[idx]
            bbox = tile.boundingbox
            if not (
                bbox.left < right
                and bbox.right > left
                and bbox.bottom < top
                and bbox.top > bottom
            ):
                continue
            yield idx

    def get_idxs(self, var, group=None):
        if group is None:
            return self.storage.root_group.attrs["stored_idxs"][var]

        return self.storage.root_group.attrs["stored_idxs"][f"{group}/{var}"]

    def tiles_for_da(self, da: xr.DataArray):
        """
        Convenience function to reproject a DataArray
        and get the tiles associated with the bounds
        """

        # Get the bounds in the native CRS
        da_bounds = da.rio.bounds()
        da_bl = transform_point(da_bounds[0], da_bounds[1], da.rio.crs, self.crs)
        da_tr = transform_point(da_bounds[2], da_bounds[3], da.rio.crs, self.crs)

        # Get the tiles that intersect with the data array
        return self.tiles_by_bounds(da_bl.x, da_bl.y, da_tr.x, da_tr.y)


    def get_data_layout(self, varnames: list[str] = []):
        if len(varnames) > 0:
            ds = (
                xr_zeros(self.geobox, chunks=self.chunk_shape, dtype=np.float32)
                .expand_dims(
                    {
                        "var": varnames,
                    }
                )
                .rename({"longitude": "x", "latitude": "y"})
            )
            return xr.full_like(ds, self.nodata).to_dataset("var")

        else:
            ds = xr_zeros(self.geobox, chunks=self.chunk_shape, dtype=np.float32).rename(
                {"longitude": "x", "latitude": "y"}
            )
            return xr.full_like(ds, self.nodata)
        

    def get_extents(self) -> None:
        """ """
        for idx in self.tiles._all_tiles():
            tile = self.tiles[idx]
            bbox = tile.boundingbox
            extent = bbox.left, bbox.right, bbox.bottom, bbox.top
            yield idx, extent

    def get_covering_polygons(
        self, idxs: list[tuple[int, int]] = []
    ) -> gpd.GeoDataFrame:
        idxs = [tuple(i) for i in idxs]
        buff = []
        x = []
        y = []
        for idx, extent in self.get_extents():
            if len(idxs) > 0 and idx not in idxs:
                continue

            buff.append(
                Polygon(
                    [
                        (extent[0], extent[2]),
                        (extent[1], extent[2]),
                        (extent[1], extent[3]),
                        (extent[0], extent[3]),
                    ]
                )
            )
            x.append(idx[0])
            y.append(idx[1])

        return gpd.GeoDataFrame(
            pd.DataFrame({"x": x, "y": y}), geometry=buff, crs="EPSG:4326"
        )

    def geobox_to_rxr(self, geobox: GeoBox) -> xr.DataArray:
        # Create a dummy data array with the same shape as the Geobox
        data = np.full((geobox.height, geobox.width), self.nodata)
        data_array = xr.DataArray(data, dims=("y", "x"))
        data_array.rio.write_crs(self.crs, inplace=True)
        data_array.rio.write_transform(geobox.transform, inplace=True)

        # Set the x and y coordinates based on the Geobox
        x_coords = (
            np.arange(geobox.width) * geobox.resolution.x
            + geobox.transform.c
            + self.dx / 2.0
        )
        y_coords = (
            np.arange(geobox.height) * geobox.resolution.y
            + geobox.transform.f
            - self.dx / 2.0
        )
        data_array = data_array.assign_coords({"x": x_coords, "y": y_coords})
        data_array = data_array.rio.set_spatial_dims(x_dim="x", y_dim="y")
        data_array.rio.write_nodata(self.nodata, inplace=True)
        # Create a dataset from the data array
        return data_array

    def set_data(
        self,
        var: str,
        idx: tuple[int, int],
        ds: xr.DataArray,
        group: str = None,
    ):
        src = self.storage.get_group(group)[var]
        if ds.y[0] < ds.y[-1]:
            ds = ds.reindex(y=ds.y[::-1])

        xy_slice = self.get_xy_slice(ds.shape, idx)
        src[xy_slice] = ds.data.astype("float32")
        return idx

    def get_xy_slice(
        self, shape: tuple[int, int], idx: tuple[int, int]
    ) -> tuple[slice, slice]:
        to_return = (
            slice(idx[0] * self.chunk_size, idx[0] * self.chunk_size + shape[0]),
            slice(idx[1] * self.chunk_size, idx[1] * self.chunk_size + shape[1]),
        )
        return to_return

    def get_single_xarray_tile(
        self, var: str, idx: tuple[int, int], group: str = None
    ) -> xr.DataArray:
        src = self.storage.get_group(group)[var]
        tile = self.tiles[tuple(idx)]
        da = self.geobox_to_rxr(tile)
        xy_slice = self.get_xy_slice(da.shape, idx)
        data = src[xy_slice]
        
        # TODO this is very much a hack.
        # I've not been able to get zarr to respect the nodata value
        # when writing the data back out to the store, without running a giant compute and storing all data.
        # So we're just going to set any cells that are all 0 to the nodata value, 
        # which means the first time data is accessed it will be treated as empty.
        if np.min(data) == 0.0 and np.max(data) == 0.0:
            data = np.full_like(data, self.nodata)
        da.data = data
        da.rio.write_nodata(self.nodata, inplace=True)
        da.rio.write_crs(self.epsg, inplace=True)
        return da

    def _store_active_idxs(self, results, group, output):
        logging.info(f"Processed {len(results)} tiles")
        if "stored_idxs" not in self.storage.root_group.attrs:
            self.storage.root_group.attrs["stored_idxs"] = dict()

        results = [i for i in results if i is not None]

        if f"{group}/{output}" in self.storage.root_group.attrs["stored_idxs"]:
            results = (
                self.storage.root_group.attrs["stored_idxs"][f"{group}/{output}"]
                + results
            )
            results = list(set([tuple(i) for i in results]))

        self.storage.root_group.attrs["stored_idxs"] = {
            **self.storage.root_group.attrs["stored_idxs"],
            f"{group}/{output}": results,
        }


@dataclass(frozen=True)
class XArrayAccessor:
    dc: DataCube
    var: str
    group: str = None

    def get_xarray_tiles(self):

        def f(idx):
            da = self.dc.get_single_xarray_tile(self.var, idx, group=self.group)
            if np.min(da) == 0 and np.max(da) == 0:
                da = xr.full_like(da, self.dc.nodata)
            print(self.var)
            print(da.min())
            return da

        return f
