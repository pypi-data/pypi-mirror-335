import duckdb
import logging
import geopandas as gpd
from typing import Union

from .storage import write_view_to_parquet
from .utils import register_gdf_to_duckdb, authenticate_duckdb_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoDuck:
    """
    A class for working with geospatial data using DuckDB.

    Provides an interface for reading, filtering, and writing geospatial data
    with support for cloud storage and partitioned parquet files.
    """

    def __init__(self, source: Union[str, gpd.GeoDataFrame]):
        """
        Initialize a GeoDuck instance.

        Args:
            source: Either a path to parquet file(s) (str) or a GeoDataFrame.
                   Path can be local or S3 path.
        """
        self.con = duckdb.connect()
        # Install and load required extensions
        self.con.install_extension("spatial")
        self.con.load_extension("spatial")

        if isinstance(source, str):
            self.path = (
                source + "/**/*.parquet" if not source.endswith(".parquet") else source
            )

            if "s3://" in self.path:
                authenticate_duckdb_connection(self.con)

            # Create base table from parquet file(s)
            self.con.sql(
                f"""
                CREATE TABLE base_table AS
                SELECT * FROM read_parquet('{self.path}',
                                          hive_partitioning=True,
                                          union_by_name=True)
                """
            )
            # Create the source view from the base table
            self.con.sql("CREATE VIEW source AS SELECT * FROM base_table")

            logger.info(f"Successfully initialized GeoDuck from path: {self.path}")

        elif isinstance(source, gpd.GeoDataFrame):
            # Use shared utility to register GeoDataFrame and create base table
            register_gdf_to_duckdb(
                source, self.con, table_name="temp_table", view_name="base_table"
            )

            # Create the source view from the base table
            self.con.sql("CREATE VIEW source AS SELECT * FROM base_table")

            # Clean up temporary table
            self.con.unregister("temp_table")
            logger.info("Successfully initialized GeoDuck from GeoDataFrame")

        else:
            raise TypeError("source must be either a string path or a GeoDataFrame")

        logger.info("Preview of data:")
        self.get_preview().show()

    def get_preview(self, view: str = "source"):
        """
        Get a preview of the current data view.

        Args:
            view: Name of the view to preview (default: "source")

        Returns:
            DuckDB result object containing all columns from the source view.
        """
        return self.con.sql(f"SELECT * FROM {view}")

    def get_layout(self, view: str = "source"):
        """
        Get the schema of the current data view.

        Args:
            view: Name of the view to get the schema for (default: "source")

        Returns:
            DuckDB result object containing the table schema description.
        """
        return self.con.sql(f"DESCRIBE {view}")

    def filter(self, query, view: str = "source"):
        """
        Filter the data using a SQL WHERE clause.

        Args:
            query: SQL WHERE clause to filter the data
            view: Name of the view to create/replace (default: "source")

        Returns:
            self for method chaining

        Example:
            geoduck.filter("state = 'CA' AND population > 1000000")
        """
        self.con.sql(
            f"""
            CREATE OR REPLACE VIEW {view} AS
            SELECT * FROM base_table
            WHERE {query}
            """
        )
        return self

    def query(self, query):
        """
        Execute a custom SQL query.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object containing the query results
        """
        return self.con.sql(query)

    def get_dataframe(self, view: str = "source"):
        """
        Convert the current view to a GeoDataFrame.

        Args:
            view: Name of the view to convert (default: "source")

        Returns:
            GeoDataFrame containing the data from the specified view
        """
        df = self.con.sql(
            f"SELECT *, ST_AsText(geometry) as geometry_wkt FROM {view}"
        ).df()
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry_wkt"])
        df.drop(columns=["geometry_wkt"], inplace=True)
        return gpd.GeoDataFrame(df, geometry="geometry")

    def write_parquet(
        self, path: str, view: str = "source", partition_by: list[str] = None
    ):
        """
        Write the current view to a geoparquet file/directory.

        Args:
            path: Path to write the parquet file(s)
            view: Name of the view to write (default: "source")
            partition_by: Optional list of columns to partition the data by

        Returns:
            self for method chaining
        """
        write_view_to_parquet(self.con, view, path, partition_by)
        return self
