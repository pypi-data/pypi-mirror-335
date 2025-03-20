import os
import logging
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
import pandas as pd
from glob import glob
from utils.geo import clip_dataarray_by_geometries
import numpy as np
from xrspatial import zonal_stats
import rasterio
from rasterio.features import rasterize
import matplotlib.pyplot as plt
from copy import deepcopy



def spatial_join_nearest(left_gdf, right_gdf, right_id):
    if left_gdf.crs != right_gdf.crs:
        right_gdf = right_gdf.to_crs(left_gdf.crs)
    joined_gdf = left_gdf.sjoin_nearest(right_gdf[[right_id, 'geometry']], how='left', distance_col='distance')
    # assert left_gdf.shape[0] == joined_gdf.shape[0], f"left_gdf.shape[0] = {left_gdf.shape[0]} != joined_gdf.shape[0] = {joined_gdf.shape[0]}"
    return joined_gdf.drop(columns=['distance'])


def summary_stats(gdf: gpd.GeoDataFrame, ds: xr.Dataset):
    data = clip_dataarray_by_geometries(ds, gdf)
    
    def safe_stats(grid):
        _ds = xr.where(grid == 1, ds, np.nan)
        return {
            "max": _ds.max().to_array().to_dataframe(name="max"),
            "sum": _ds.sum().to_array().to_dataframe(name="sum"),
            "mean": _ds.mean().to_array().to_dataframe(name="mean"),
            "count": grid.sum().to_array().to_dataframe(name="count"),
        }
    
    data = [safe_stats(d) for idx, d in data]
    
    df_buff = []
    for idx, d in data:
        series_buff = []
        for k in ('max', 'sum', 'mean', "count"):
            v = d[k].reset_index()
            cols = v.index
            logging.info(cols)
            v['idx'] = idx
            v = v.pivot(index='idx', columns='variable', values=k)
            v = v.rename(columns={c: f'{c}_{k}' for c in v.columns})
            series_buff.append(v)
            
        merged_df =pd.concat(series_buff, axis=1)
        df_buff.append(merged_df)
    
    return pd.concat([gdf, pd.concat(df_buff)], axis=1)


def summary_stats2(gdf: gpd.GeoDataFrame, ds: xr.Dataset, stats_to_perform = ["sum", "count"], resolution_upsample=1):
    gdf = gdf.reset_index()
    init_gdf = deepcopy(gdf)
    gdf = gdf.to_crs(ds.rio.crs)
    gdf = gdf[['geometry', 'index']]
    gdf['area'] = gdf.geometry.area
    gdf = gdf.sort_values(by='area', ascending=True).drop(columns=['area'])
    # Create an empty canvas with the same dimensions as the raster
    
    
    _ds = ds.copy()
    _ds = _ds.interp(
        x=np.linspace(float(_ds.x.min()), float(_ds.x.max()), _ds.sizes['x'] * resolution_upsample),
        y=np.linspace(float(_ds.y.min()), float(_ds.y.max()), _ds.sizes['y'] * resolution_upsample),
        method='nearest'
    )
    transform = rasterio.transform.from_bounds(*_ds.rio.bounds(), _ds.rio.width, _ds.rio.height)
    out_shape = (_ds.rio.height, _ds.rio.width)
    _ds = xr.where(_ds == _ds.rio.nodata, np.nan, _ds)
    _ds.rio.write_crs(ds.rio.crs, inplace=True)
    _ds.rio.set_nodata(_ds.rio.nodata, inplace=True)

    # Rasterize the zones GeoDataFrame
    shapes = ((geom, value) for geom, value in zip(gdf.geometry, gdf.index))
    zones = rasterize(shapes=shapes, out_shape=out_shape, transform=transform, fill=np.nan, dtype='float32')
    zone_raster = _ds.copy()
    zone_raster.data = zones
    
    # +1 accounts for the nan values
    unique_zones = np.unique(zone_raster)
    unique_ids = np.unique(gdf.index)
    assert (
        len(unique_zones) == len(unique_ids)+1, 
        f"Non-unique zone_raster, make sure your features don't overlap and try a higher resolution_upsample, {len(unique_zones)} zones != {len(unique_ids)+1} ids"
    )
    
    _ds = _ds.astype(zone_raster.dtype)
    
    # Compute zonal statistics (sum of pixels within each zone)
    buff = []
    stats = zonal_stats(
        zone_raster, 
        _ds, 
        stats_funcs=stats_to_perform
    )

    # Display the results
    merged_stats = pd.merge(init_gdf, stats, left_on="index", right_on="zone", how="left")
    merged_stats.index = merged_stats['index']
    merged_stats = merged_stats.drop(columns=['index', "zone"])
    return merged_stats


def prep(gdf: gpd.GeoDataFrame):
    return gdf.drop(columns=[i for i in ["index_right", "index_left"] if i in gdf.columns])


def summary_stats_nearest(gdf: gpd.GeoDataFrame, stats_geographies: gpd.GeoDataFrame, stats_geographies_id: str, columns_to_stat: list, stats: list):    
    gdf = prep(gdf)
    
    assert len(stats_geographies[stats_geographies_id].unique()) == len(stats_geographies[stats_geographies_id]), "Non-unique stats_geographies_id"
        
    stats_geographies = prep(stats_geographies)
    gdf_with_attribs = spatial_join_nearest(gdf, stats_geographies, stats_geographies_id)
    gdf_grouped = gdf_with_attribs.groupby(stats_geographies_id)
    
    stats_dict = {
        "sum": lambda x: x.sum(),
        "mean": lambda x: x.mean(),
        "max": lambda x: x.max(),
        "count": lambda x: x.count()
    }
    
    output = []
    for s in stats:
        for c in columns_to_stat:
            f = stats_dict[s]
            output.append(f(gdf_grouped[c]).rename(f'{c}_{s}'))
    to_return = pd.concat(output, axis=1)
    to_return.index = f(gdf_grouped[c]).index
    to_return = stats_geographies.merge(to_return, left_on=stats_geographies_id, right_index=True, how="left")
    return to_return

