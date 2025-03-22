from cao.sources.base import BaseSource
from cao.registry import ConverterRegistry
import geopandas as gpd

class GeoDataSource(BaseSource):
    def extract(self, path):
        gdf = gpd.read_file(path)
        return {"type": "geodataframe", "data": gdf}

    @classmethod
    def supported_extensions(cls):
        return ["geojson", "shp", "parquet"]
    
    @classmethod
    def data_type(cls):
        return "geodataframe"

for ext in GeoDataSource.supported_extensions():
    ConverterRegistry.register_source(ext, GeoDataSource)
