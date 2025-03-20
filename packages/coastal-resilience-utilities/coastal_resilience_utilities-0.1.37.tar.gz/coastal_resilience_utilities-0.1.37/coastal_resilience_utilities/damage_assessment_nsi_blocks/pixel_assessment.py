import rioxarray as rxr
import requests, os
from coastal_resilience_utilities.utils.dataset import makeSafe_rio
from coastal_resilience_utilities.utils.get_features import get_features_with_z_values, get_osm
from coastal_resilience_utilities.damage_assessment.nsi_assessment import get_nsi_damages_generic
from coastal_resilience_utilities.utils import geo
from glob import glob
from typing import Callable
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import warnings
import xarray as xr
import numpy as np
from enum import Enum
from typing import OrderedDict


class RunMode(Enum):
    NORMAL = "normal"
    DEBUG = "debug"


def get_building_pixel_frequencies(buildings, flooding, field, **rasterize_kwargs):
    buildings_rasterized = geo.rasterize_zones(buildings, flooding, field=field, **rasterize_kwargs)
    unique, counts = np.unique(buildings_rasterized, return_counts=True)
    return buildings_rasterized, dict(zip(unique, counts))


def normalize_by_size(idx, frequencies):
    if np.isnan(idx):
        return np.nan
    return 1 / frequencies[idx]


def flooddepth_to_percent_damages(idx, buildings, min_flood_depth=0.1):
    flooddepth, building_idx = idx
    if np.isnan(flooddepth):
        return np.nan
    if building_idx == -9999:
        return np.nan
    building_info = buildings[buildings.idx == building_idx]
    
    depth_cols = [i for i in building_info if i.startswith("m") and i != "man_made"]
    depth_vals = OrderedDict()
    for i in depth_cols:
        depth_vals[i] = float(i[1:])
    if flooddepth <= min_flood_depth:
        return 0
    prev_val = building_info[depth_cols[0]].values[0]
    prev_depth = 0
    val_found = False
    for k, v in depth_vals.items():
        this_val = building_info[k].values[0]
        this_depth = v
        if flooddepth < v:
            return np.interp(flooddepth, [prev_depth, this_depth], [prev_val, this_val])
    return 1


def get_nsi_damages_pixel(
    flooding: xr.DataArray, 
    buildings: gpd.GeoDataFrame, 
    index_field: str, 
    value_field: str, 
    resolution_upsample: int = 2, 
    mode: RunMode = RunMode.NORMAL,
    min_flood_depth: float = 0.1
):
    """
    Get NSI damages for a pixel
    """
    # Upsample the flooding to the resolution of the buildings
    flooding = flooding.rio.reproject("EPSG:4326")
    flooding_upsampled = flooding.interp(
        x=np.linspace(float(flooding.x.min()), float(flooding.x.max()), flooding.sizes['x'] * resolution_upsample),
        y=np.linspace(float(flooding.y.min()), float(flooding.y.max()), flooding.sizes['y'] * resolution_upsample),
        method='nearest'
    )
    flooding_upsampled.name = "flooding"
    
    buildings_normalized_value = geo.distribute_zonal_value_to_pixels(
        da=flooding_upsampled,
        gdf=buildings,
        column_to_distribute=value_field,
        dtype="float32",
        fill=np.nan
    )
    
    buildings_rasterized = geo.rasterize_zones(buildings, flooding_upsampled, field=index_field, dtype="int32", fill=-9999)
    buildings_rasterized.name = "buildings"
    combined_dataarray = xr.merge([flooding_upsampled, buildings_rasterized]).to_array()
    damage_percents = xr.apply_ufunc(
        flooddepth_to_percent_damages, 
        combined_dataarray, 
        kwargs={"buildings": buildings, "min_flood_depth": min_flood_depth}, 
        input_core_dims=[["variable"]], 
        vectorize=True
    )
    damage_values = damage_percents * buildings_normalized_value
    
    if mode == RunMode.DEBUG:
        return (buildings_rasterized,
            buildings_normalized_value, 
            damage_percents,
            damage_values
        )
        
    elif mode == RunMode.NORMAL:
        return damage_values
