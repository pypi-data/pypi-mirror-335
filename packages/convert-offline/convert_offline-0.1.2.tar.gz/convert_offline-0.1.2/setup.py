from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="convert-offline",
    version="0.1.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "Pillow",
        "geopandas",
        "pandas",
        "shapely",
        "pyarrow",
        "fiona"
    ],
    entry_points={
        "console_scripts": [
            "cao=cao.cli:cli"
        ]
    },
    author="Jack McNulty",
    author_email="jackmcnulty76@gmail.com",
    description="Convert Anything Offline — a modular CLI tool for file format conversion.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
)

