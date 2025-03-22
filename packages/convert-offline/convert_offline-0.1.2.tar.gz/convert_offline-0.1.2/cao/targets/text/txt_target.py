from cao.targets.base import BaseTarget
from cao.registry import ConverterRegistry

class TXTTarget(BaseTarget):
    def __init__(self, format):
        self.format = format.lower()

    def write(self, data, path):
        if data["type"] == "image":
            img = data["data"]
            info = f"Image size: {img.size}\nMode: {img.mode}"
        elif data["type"] == "text":
            info = data["data"]
        else:
            raise ValueError("TXTTarget only supports image or text")

        with open(path, "w") as f:
            f.write(info)

    @staticmethod
    def accepts_type(data_type):
        return data_type in ["image", "text"]

# Register with the converter registry
ConverterRegistry.register_target("txt", lambda ext: TXTTarget(ext))
