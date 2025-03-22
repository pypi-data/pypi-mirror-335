from cao.targets.base import BaseTarget
from cao.registry import ConverterRegistry

class GeoCSVTarget(BaseTarget):
    def __init__(self, format):
        self.format = format.lower()

    def write(self, data, path):
        gdf = data["data"]
        df = gdf.copy()

        if gdf.geometry.geom_type.isin(["Point"]).all():
            # Extract lat/lon and keep WKT
            df["longitude"] = gdf.geometry.x
            df["latitude"] = gdf.geometry.y
            df["geometry"] = gdf.geometry.to_wkt()
        else:
            # Non-point geometries — only include WKT
            df["geometry"] = gdf.geometry.to_wkt()

        df.to_csv(path, index=False)

    @staticmethod
    def accepts_type(data_type):
        return data_type == "geodataframe"

ConverterRegistry.register_target("csv", lambda ext: GeoCSVTarget(ext))
