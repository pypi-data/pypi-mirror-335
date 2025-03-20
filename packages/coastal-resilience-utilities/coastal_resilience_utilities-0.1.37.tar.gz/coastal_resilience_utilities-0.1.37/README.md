# Coastal Resilience Utilities
This repository contains utilities for coastal resilience analysis and design.

## Contents
- `damage_assessment`: damage assessments based on earth observation data and National Structure Inventory.
- `damage_assessment_nsi_blocks`: damage assessments based on HAZUS blocks.
- `mosaic`: Mosaicking datasets.
- `summary_stats`: Summarize raster datasets using vector points and polygons.
- `utils`: A variety of functionality for doing geospatial analysis.  Rasterize, vectorize, fetch features from OSM/OpenBuildings/ArcOnline, extract values from rasters.

## Installation
There are a few ways to install and use this code:

**Option 1: Conda**
Use the included conda environment to create a new environment and install the package.
From this directory, run:
```bash
conda env create -f environment.yml
```


**Option 2: Docker and Makefile**
This option is better if you are doing active development, which might include volume mounting of other repos.

From this directory, run:
```bash
make build-and-run
```

There are two env files:
- `.env.publish`, which is used to publish the package to PyPI using Twine and UV
- `.env.data`, which maps files necessary for damage assessment, such as NSI, OpenBuildings, etc.

## Publishing
To publish a new version of the package, run:
```bash
make publisher
pytest
uv build
uv publish
```

We're using a slightly convoluted method of publishing, since we aren't yet set up to publish to Conda.  This means we publish using UV and PyPI, and downstream clients have to install with pip into a conda environment.

Thus it's important to keep the `pyproject.toml` file up to date with the `environment.yml` file.




## Schematic
The Figjam schematic can be found [here](https://git.ucsc.edu/chlowrie/coastal-resilience-utilities/-/blob/main/coastal_resilience_utilities/damage_assessment/damage_assessment.py?ref_type=heads)