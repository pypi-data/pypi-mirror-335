from setuptools import setup, find_packages

setup(
    name="convert-offline",
    version="0.1.1",
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
    description="Convert Anything Offline – CLI tool for converting files across formats offline.",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)

