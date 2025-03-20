import duckdb
import geopandas as gpd
import os


def register_gdf_to_duckdb(
    gdf: gpd.GeoDataFrame,
    con: duckdb.DuckDBPyConnection,
    table_name: str = "temp_table",
    view_name: str = "base_table",
) -> None:
    """
    Register a GeoDataFrame to a DuckDB connection with proper geometry handling.
    Optionally creates a view with proper geometry type.

    Args:
        gdf: GeoDataFrame to register
        con: DuckDB connection
        table_name: Name for the temporary table (default: "temp_table")
        view_name: Name for the permanent table (default: "base_table")
    """
    # Convert geometry to WKB for DuckDB compatibility
    df_copy = gdf.copy()
    df_copy["geometry_wkb"] = df_copy.geometry.apply(lambda geom: geom.wkb)
    df_copy = df_copy.drop(columns=["geometry"])

    # Register the DataFrame as a temporary table
    con.register(table_name, df_copy)

    # Create a permanent table
    con.sql(
        f"""
        CREATE TABLE {view_name} AS
        SELECT * EXCLUDE (geometry_wkb), ST_GeomFromWKB(geometry_wkb) as geometry
        FROM {table_name}
        """
    )


def authenticate_duckdb_connection(con: duckdb.DuckDBPyConnection) -> None:
    """
    Authenticate a DuckDB connection with necessary extensions and S3 credentials if needed.

    Args:
        con: DuckDB connection to configure
    """

    # Install and load HTTP filesystem extension
    con.install_extension("httpfs")
    con.load_extension("httpfs")

    # Configure S3 settings
    con.execute("SET s3_url_style='path';")
    con.execute(
        """
        CREATE SECRET IF NOT EXISTS secret1 (
            TYPE S3,
            KEY_ID '{}',
            SECRET '{}',
            ENDPOINT '{}'
        );
        """.format(
            os.getenv("AWS_ACCESS_KEY_ID"),
            os.getenv("AWS_SECRET_ACCESS_KEY"),
            os.getenv("AWS_ENDPOINT_URL", "").replace("https://", ""),
        )
    )
