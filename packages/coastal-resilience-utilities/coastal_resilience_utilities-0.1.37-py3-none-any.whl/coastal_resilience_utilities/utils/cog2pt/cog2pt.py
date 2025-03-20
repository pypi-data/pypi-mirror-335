import os
import logging
import geopandas as gpd
import pandas as pd
import xarray as xr
import rioxarray as rxr
# from vectorize import xr_vectorize
import uuid, json, copy
import numpy as np
import gc
from coastal_resilience_utilities.utils.dataset import get_resolution, open_as_ds, meters_to_degrees
import math
from .geometry_manipulation import generate_beveled_square, generate_squircle, generate_square
from functools import partial
from tqdm import tqdm

import logging
logging.basicConfig()
logging.root.setLevel(logging.INFO)


# GEOM_TYPE="SQUARES"
# GEOM_TYPE="SQUIRCLE"
# GEOM_TYPE="POINTS"
GEOM_TYPE="BEVELED_SQUARES"

geometry_mapping = {
    "POINTS": lambda X, Y, r: [X, Y],
    "SQUARES": generate_square,
    "BEVELED_SQUARES": generate_beveled_square,
    "SQUIRCLES": generate_squircle,
}

geojson_base = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [102.0, 0.5]
        },
        "properties": {
            "prop0": "value0"
        }
    }]
}



def ds_pixels_to_geometry(ds, res, type="BEVELED_SQUARES", args=dict(), filter_to_positive=True):
    init_crs = ds.rio.crs
    ds = ds.copy().stack(point=('x', 'y'))
    if filter_to_positive:
        ds = ds.where(ds > 0, drop=True)
    ds = ds.to_dict()
    gj = copy.deepcopy(geojson_base)
    coords = ds['coords']['point']['data']
    data = {
        k: ds['data_vars'][k]['data'] for k in ds['data_vars'].keys()
    }
    features_buff = []
    for idx, coord in tqdm(enumerate(coords), total=len(coords)):
        properties = {k: data[k][idx] for k in data.keys()}
        properties = {**properties, "x": coord[0], "y": coord[1]}
        features_buff.append({
            "type": "Feature",
            "geometry": {
                "type": "Point" if type == "POINTS" else "Polygon",
                "coordinates": partial(geometry_mapping[type], r=res, **args)(coord[0], coord[1])
            },
            "properties": properties
        })
    gj['features'] = features_buff
    gdf = gpd.read_file(json.dumps(gj), driver='GeoJSON')
    gdf = gdf.set_crs(init_crs, allow_override=True)
    return gdf




def ds_to_pts(ds, output, type="BEVELED_SQUARES", args=dict()):
    """Handle tile requests."""

    res = get_resolution(ds)
    
    xmin, xmax = np.min(ds.x).values, np.max(ds.x).values
    ymin, ymax = np.min(ds.y).values, np.max(ds.y).values
    xstep, ystep = [math.ceil(i * 1000) for i in res]
    logging.info(ds)
    ds.rio.set_spatial_dims(ds.rio.x_dim, ds.rio.y_dim, inplace=True)
    
    for x in np.arange(xmin, xmax, xstep):
        for y in np.arange(ymin, ymax, ystep):
            with ds.rio.clip_box(
                minx=x,
                miny=y,
                maxx=x+xstep,
                maxy=y+ystep,
            ).stack(point=('x', 'y')) as ds_clipped:
                maxvals = [ds_clipped[i].max().values for i in ds_clipped]
                logging.info(maxvals)
                
                if np.any([i > 0 for i in maxvals]):
                    logging.info(f"{x}, {y}")
                    ds_clipped = ds_clipped.compute()
                    ds_clipped = ds_clipped.where(ds_clipped > 0, drop=True)
                    gdf = gpd.read_file(json.dumps(ds_pixels_to_geometry(ds_clipped, res[0], type, args)), driver='GeoJSON')
                    gdf = gdf.set_crs(ds.rio.crs, allow_override=True)
                    gdf = gdf.to_crs("EPSG:4326")
                    fname = f'{str(x)[0:7]}_{str(y)[0:7]}_{str(x+xstep)[0:7]}_{str(y+ystep)[0:7]}.parquet'
                    gdf.to_parquet(os.path.join(output, fname), geometry_encoding="geoarrow")
                else:
                    logging.info("skipping")
            gc.collect()
    
    return output

