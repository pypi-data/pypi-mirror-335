from cao.sources.base import BaseSource
from cao.registry import ConverterRegistry
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

class GeoCSVSource(BaseSource):
    def extract(self, path):
        df = pd.read_csv(path)
        if "latitude" not in df.columns or "longitude" not in df.columns:
            raise ValueError(
                "CSV must contain 'latitude' and 'longitude' columns.\n"
                "Please rename your columns or preprocess your file accordingly."
            )

        geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        return {"type": "geodataframe", "data": gdf}

    @classmethod
    def supported_extensions(cls):
        return ["csv"]
    
    @classmethod
    def data_type(cls):
        return "geodataframe"

ConverterRegistry.register_source("csv", GeoCSVSource)
