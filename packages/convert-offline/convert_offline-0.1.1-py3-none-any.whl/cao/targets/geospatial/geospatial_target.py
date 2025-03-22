from cao.targets.base import BaseTarget
from cao.registry import ConverterRegistry

class GeoDataTarget(BaseTarget):
    def __init__(self, format):
        self.format = format.lower()

    def write(self, data, path):
        gdf = data["data"]

        if self.format == "parquet":
            gdf.to_parquet(path, index=False)
        elif self.format == "geojson":
            gdf.to_file(path, driver="GeoJSON")
        elif self.format == "shp":
            gdf.to_file(path, driver="ESRI Shapefile")
        else:
            raise ValueError(f"Unsupported geo format: {self.format}")

    @staticmethod
    def accepts_type(data_type):
        return data_type == "geodataframe"

GeoFormats = ["geojson", "shp", "parquet"]
for ext in GeoFormats:
    ConverterRegistry.register_target(ext, lambda ext=ext: GeoDataTarget(ext))
