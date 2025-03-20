import duckdb
import geopandas as gpd
from .utils import register_gdf_to_duckdb, authenticate_duckdb_connection


def _write_parquet_with_metadata(
    con, source_name: str, path: str, partition_by: list[str] = None
):
    """
    Core functionality for writing data to parquet with GeoParquet metadata.

    Args:
        con: DuckDB connection
        source_name: Name of the table/view to write
        path: Path to write the parquet file(s)
        partition_by: Optional list of columns to partition the data by
    """
    # Calculate bbox for Hilbert index
    bbox = con.sql(
        f"""
        SELECT ST_XMin(ST_Extent(geometry)) as xmin,
               ST_YMin(ST_Extent(geometry)) as ymin,
               ST_XMax(ST_Extent(geometry)) as xmax,
               ST_YMax(ST_Extent(geometry)) as ymax
        FROM {source_name}
        """
    ).fetchone()

    # Base COPY options with proper quoting
    copy_options = {"FORMAT": "'PARQUET'", "COMPRESSION": "'ZSTD'"}
    if "s3://" not in path:
        copy_options["OVERWRITE"] = "TRUE"
        authenticate_duckdb_connection(con)

    # Add partition options if specified
    if partition_by:
        partition_cols = ", ".join(partition_by)
        copy_options.update(
            {"PARTITION_BY": f"({partition_cols})", "FILENAME_PATTERN": "'data_{uuid}'"}
        )

    # Convert options to SQL string
    options_str = ", ".join(f"{k} {v}" for k, v in copy_options.items())

    # Note: this + the bbox calculation is slow
    # TODO: give option to avoid it
    # Sort by Hilbert index to improve query performance
    # https://medium.com/radiant-earth-insights/using-duckdbs-hilbert-function-with-geop-8ebc9137fb8a
    con.sql(
        f"""
        COPY (
            SELECT * FROM {source_name}
            ORDER BY ST_Hilbert(
                geometry,
                ST_Extent(
                    ST_MakeEnvelope(
                        {bbox[0]}, {bbox[1]},
                        {bbox[2]}, {bbox[3]}
                    )
                )
            )
        )
        TO '{path}'
        ({options_str})
        """
    )


def save_gdf_to_parquet(
    gdf: gpd.GeoDataFrame, path: str, partition_by: list[str] = None
):
    """
    Save a GeoDataFrame to (partitioned) parquet using DuckDB with GeoParquet metadata.

    Args:
        gdf: GeoDataFrame to save
        path: Path to write the parquet file(s)
        partition_by: Optional list of columns to partition the data by
    """
    con = duckdb.connect()

    try:
        con.install_extension("spatial")
        con.load_extension("spatial")

        # Use shared utility to register GeoDataFrame and create view
        register_gdf_to_duckdb(gdf, con, table_name="temp_table", view_name="temp_view")

        # Use common write functionality
        _write_parquet_with_metadata(con, "temp_view", path, partition_by)

    finally:
        # Clean up
        con.unregister("temp_table")
        con.close()


def write_view_to_parquet(con, view: str, path: str, partition_by: list[str] = None):
    """
    Write a DuckDB view/table to (partitioned) parquet with GeoParquet metadata.

    Args:
        con: DuckDB connection
        view: Name of the view/table to write
        path: Path to write the parquet file(s)
        partition_by: Optional list of columns to partition the data by
    """
    _write_parquet_with_metadata(con, view, path, partition_by)
