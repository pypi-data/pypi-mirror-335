# CAO — Convert Anything Offline

**CAO** is a modular, offline-first command-line tool that lets you convert files between dozens (eventually hundreds) of formats — images, text, geospatial, and more. Designed to be **clean**, **extensible**, and completely **offline**, CAO also includes plugin support for community-driven converters.

---

## Features

- Convert files across many format families (image, text, geospatial, etc.)
- Auto-discovery of sources and targets
- Plugin system with install/remove/reload support
- Built-in support for common geospatial formats (GeoJSON, Shapefile, GeoParquet, CSV with lat/lon)
- Architecture designed for scale — clean interfaces and grouping
- Easy to test and extend
- Fully offline — no internet required to use

---

## Installation

CAO is currently distributed via GitHub.

```bash
git clone https://github.com/jackmcnulty/cao.git
cd cao
pip install -e .
```

You’ll need:

- Python 3.8+
- pip
- Basic packages: `click`, `Pillow`, `geopandas`, `pandas`, `shapely`, `fiona`, `pyarrow` (check setup.py for full list)

---

## Usage

### Convert files

```bash
cao convert input.png output.jpg
cao convert input.txt output.png
cao convert data.geojson output.csv
```

CAO will determine what type of content you're converting and route it to the right source and target.

---

### See what a format can convert to

```bash
cao from png
cao from geojson
cao from csv
```

Outputs something like:

```
You can convert 'geojson' into:
- csv
- shp
- parquet
```



---

## Plugin System

CAO supports installable converters and features via plugins.

### List installed plugins

```bash
cao plugin list
```

### Install a plugin

```bash
cao plugin install ./my_plugin.py
cao plugin install ./plugin_bundle.zip
```

### Remove a plugin

```bash
cao plugin remove my_plugin
```

### Reload all plugins (dev-time hotload)

```bash
cao plugin reload
```

### Bundle all installed plugins into a ZIP

```bash
cao plugin bundle my_plugins.zip
```

---

## Creating Your Own Converter

### Create a Source

```python
from cao.sources.base import BaseSource
from cao.registry import ConverterRegistry

class HelloSource(BaseSource):
    def extract(self, path):
        return {"type": "text", "data": "Hello from source"}

    @classmethod
    def supported_extensions(cls):
        return ["hello"]

    @classmethod
    def data_type(cls):
        return "text"

ConverterRegistry.register_source("hello", HelloSource)
```

### Create a Target

```python
from cao.targets.base import BaseTarget
from cao.registry import ConverterRegistry

class UpperTextTarget(BaseTarget):
    def write(self, data, path):
        with open(path, "w") as f:
            f.write(data["data"].upper())

    @staticmethod
    def accepts_type(data_type):
        return data_type == "text"

ConverterRegistry.register_target("txt", lambda ext: UpperTextTarget())
```

---

## 📁 Project Structure

```
cao/
├── cao/
│   ├── cli.py
│   ├── engine.py
│   ├── registry.py
│   ├── sources/
│   │   ├── image/
│   │   ├── geospatial/
│   ├── targets/
│   │   ├── text/
│   │   ├── image/
│   │   ├── geospatial/
│   ├── plugins/
├── README.md
├── setup.py
├── pyproject.toml
```

---

## Contributing

Want to contribute?

- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add new converters
- Keep things modular — one class per source/target, grouped by format type
- Follow naming conventions and interface expectations
- PRs are welcome!

---

## License

MIT License — free to use, modify, and share.

---

## Roadmap

- Lots of new converters