from . import rasterops, compute
from osgeo import gdal
import os
import uuid
import shutil
import warnings
import rioxarray as rxr
import boto3


class Export:

    def __init__(
        self,
        dc: rasterops.DataCube,
    ):
        self.dc = dc

    def export_as_tif(
        self,
        var: str,
        output: str | None = None,
        tmp_dir: str | None = None,
        group: str | None = None,
        idxs: list[tuple[int, int]] = [],
        COG = False,
        track_progress = True,
        creation_options = None,
        upload = False,
    ) -> str:
        id = str(uuid.uuid4())
        if tmp_dir is None:
            tmp_dir = f"/tmp/{id}"
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)

        if output is None:
            output = f"/tmp/{id}.tif"

        if creation_options is None:
            if COG:
                creation_options = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]
            else:
                creation_options = ["COMPRESS=LZW", "BIGTIFF=YES"]

        callback = None
        if track_progress:
            def progress_callback(complete, message, data):
                print(f"Export progress: {complete * 100:.1f}% complete")
            callback = progress_callback

        translate_options = gdal.TranslateOptions(
            format="COG" if COG else "GTiff",
            creationOptions=creation_options,
            callback=callback
        )
        tmp_vrt = self.export_as_tif_tiles(var, tmp_dir, group=group, idxs=idxs)
        gdal.Translate(
            output,
            tmp_vrt,
            options=translate_options
        )
        if upload:
            return self._upload_to_s3(output, var)

        return output

    def _upload_to_s3(self, file_path, var) -> str:
        try:
            timestamp = uuid.uuid4()
            filename = os.path.basename(file_path)

            s3_key = f"{var}/{timestamp}_{filename}"

            bucket = os.environ["S3_PUBLIC_EXPORT_BUCKET"]
            print(f"Uploading file to s3://{bucket}/{s3_key}...")
            file_size = os.path.getsize(file_path)
            total_bytes_uploaded = 0

            def upload_progress(bytes_transferred):
                nonlocal total_bytes_uploaded
                total_bytes_uploaded += bytes_transferred
                percentage = total_bytes_uploaded * 100 / file_size
                print(f"Upload progress: {percentage:.1f}% complete")

            s3_client = boto3.client('s3')
            s3_client.upload_file(
                file_path,
                bucket,
                s3_key,
                Callback=upload_progress
            )

            s3_url = f"https://s3-west.nrp-nautilus.io/{bucket}/{s3_key}"
            print(f"File successfully uploaded and available at: {s3_url}")
            return s3_url

        except Exception as e:
            print(f"Failed to upload to S3: {e}. Using local file instead.")
            return file_path

    @classmethod
    def process_tile(
        cls,
        dc: rasterops.DataCube,
        var: str,
        idx: tuple[int, int],
        dir: str,
        group: str = None,
    ):
        da = dc.get_single_xarray_tile(var, idx, group=group)
        if da is None:
            return None

        da.rio.write_crs(dc.epsg, inplace=True)
        da.rio.write_nodata(dc.nodata, inplace=True)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            da.rio.to_raster(f"{dir}/{var}_{idx[0]}_{idx[1]}.tif", compress="LZW")
        return idx

    def export_as_tif_tiles(
        self,
        var: str,
        dir: str,
        group: str = None,
        idxs: list[tuple[int, int]] = [],
    ) -> None:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)

        if len(idxs) == 0:
            if self.dc.store_active_idxs:
                idxs = self.dc.storage.root_group.attrs["stored_idxs"][f"{group}/{var}"]
            else:
                idxs = [i for i in self.dc.tiles._all_tiles()]

        compute_items = [
            compute.Args(args=[self.dc, var, idx, dir, group]) for idx in idxs
        ]

        # Use the parallel execution framework
        self.dc.compute.execute(Export.process_tile, compute_items)
        tmp_vrt = gdal.BuildVRT(
            f"{dir}/vrt.vrt",
            [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith(".tif")],
        )
        return tmp_vrt

    def as_da(self, **kwargs):
        return rxr.open_rasterio(self.export_as_tif(**kwargs))
