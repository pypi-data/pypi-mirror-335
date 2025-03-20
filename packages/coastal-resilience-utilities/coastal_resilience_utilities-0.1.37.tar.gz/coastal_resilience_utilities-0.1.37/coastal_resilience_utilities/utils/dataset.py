from PIL import Image
import numpy as np
import os
import xarray as xr
import rioxarray as rxr
import subprocess
import uuid
import math
from glob import glob
import logging

# import dask.array as da
import gc


TMP_FOLDER='/tmp'


def meters_to_degrees(distance_meters, latitude):
    """
    Translate a distance in meters to degrees, given a latitude.

    Parameters:
        distance_meters (float): Distance in meters.
        latitude (float): Latitude in decimal degrees.

    Returns:
        float: Distance in degrees.
    """
    # Earth radius in meters
    earth_radius = 6378137.0  # approximate radius in meters

    # Convert latitude from degrees to radians
    lat_radians = math.radians(latitude)

    # Calculate the length of a degree of latitude and longitude at the given latitude
    lat_length = math.cos(lat_radians) * 2.0 * math.pi * earth_radius / 360.0

    # Translate the distance from meters to degrees
    distance_degrees = distance_meters / lat_length

    return distance_degrees



def degrees_to_meters(distance_degrees, latitude):
    """
    Translate a distance in degrees to meters, given a latitude.

    Parameters:
        distance_degrees (float): Distance in degrees.
        latitude (float): Latitude in decimal degrees.

    Returns:
        float: Distance in meters.
    """
    # Earth radius in meters
    earth_radius = 6378137.0  # approximate radius in meters

    # Convert latitude from degrees to radians
    lat_radians = math.radians(latitude)

    # Calculate the length of a degree of latitude and longitude at the given latitude
    lat_length = math.cos(lat_radians) * 2.0 * math.pi * earth_radius / 360.0

    # Translate the distance from degrees to meters
    distance_meters = distance_degrees * lat_length

    return distance_meters

def get_resolution(ds):
    return [
        abs(ds.x.values[1] - ds.x.values[0]),
        abs(ds.y.values[1] - ds.y.values[0])
    ]

def get_timestep_as_geo(rds, full_output_path, t_index):

    # Construct the full file path for the input and output

    # Define spacing for the grid
    x_spacing = 0.0005  # Adjust this value as needed
    y_spacing = 0.0005  # Adjust this value as needed

    # Open the dataset with Dask using xarray
    # rds = xr.open_dataset(full_input_path, chunks={time_method: 500})

    # Extract 'globalx', 'globaly', and the selected variable
    globalx = rds['x']
    globaly = rds['y']

    # Perform flattening and index calculations once
    globalx_flat = globalx.values.flatten()
    globaly_flat = globaly.values.flatten()

    print(globalx_flat)
    print(globaly_flat)

    x_min, x_max = np.min(globalx_flat), np.max(globalx_flat)
    y_min, y_max = np.min(globaly_flat), np.max(globaly_flat)
    num_points_x = int((x_max - x_min) / x_spacing) + 1
    num_points_y = int((y_max - y_min) / y_spacing) + 1
    print(num_points_x * num_points_y)

    x_indices = ((globalx_flat - x_min) / x_spacing).astype(int)
    y_indices = ((globaly_flat - y_min) / y_spacing).astype(int)
    valid_indices = (x_indices >= 0) & (x_indices < num_points_x) & (y_indices >= 0) & (y_indices < num_points_y)

    # Create a template grid
    template_grid = np.full((num_points_y, num_points_x), np.nan, dtype=float)

    # Copy the template grid for current timestep
    grid_values = template_grid.copy()

    # Extract data for the current timestep and flatten
    timestep_flattened = rds.isel({"timemax": t_index}).values.flatten()

    # Populate grid_values using pre-calculated indices
    grid_values[y_indices[valid_indices], x_indices[valid_indices]] = timestep_flattened[valid_indices]

    # Replace NaN values with -1000 (or another value if needed)
    grid_values[np.isnan(grid_values)] = -1000

    # Define dimensions
    dims = ('y', 'x')

    # Define coordinates
    coords = {
        'x': np.interp(range(0, num_points_x), [0, grid_values.shape[1]], [x_min, x_max]),
        'y': np.interp(range(0, num_points_y), [0, grid_values.shape[0]], [y_min, y_max])
    }

    # Create the DataArray
    new_data_array = xr.DataArray(grid_values, dims=dims, coords=coords)
    return new_data_array



def makeSafe_rio(ds):
    id = str(uuid.uuid4())
    tmp_cog1 = f'/tmp/{id}-1.tiff'
    tmp_cog2 = f'/tmp/{id}-2.tiff'
    for p in (tmp_cog1, tmp_cog2):
        if os.path.exists(p):
            os.remove(p)
    ds.rio.to_raster(tmp_cog1)
    bashCommand = f"gdalwarp {tmp_cog1} {tmp_cog2} -of COG"
    process = subprocess.Popen(bashCommand.split(' '), stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line: break
        print(line, flush=True)
    x = rxr.open_rasterio(tmp_cog2).isel(band=0)
    os.remove(tmp_cog1)
    return x


def compressRaster(ds: xr.DataArray | xr.Dataset, output_path, replace=True, statistics=True, print_lines=False):
    id = str(uuid.uuid4())
    if statistics:
        tmp_rast = f"/tmp/{id}.tiff"
    else:
        tmp_rast = output_path
    
    if replace:
        try:
            os.remove(output_path)
        except:
            pass
    
    ds = ds.where(ds != ds.rio.nodata, 0)
    ds.rio.write_nodata(0, inplace=True)
    ds.rio.to_raster(tmp_rast, driver='COG', compress='LZW')
    
    if statistics:
        # Rxr doesn't support statistics properly.  
        # The following lines calculate them, and can be checked for removal with future versions
        # This also impacts the Docker image needed to run
        bashCommand = f"gdalwarp -t_srs EPSG:4326 {tmp_rast} {output_path} -of COG -co COMPRESS=LZW -co STATISTICS=YES"
        # bashCommand = f"gdalwarp {tmp_rast} {output_path} -of COG -co COMPRESS=LZW -co STATISTICS=YES"
        process = subprocess.Popen(bashCommand.split(' '), stdout=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if not line: break
            if print_lines:
                print(line, flush=True)
        os.remove(tmp_rast)
    return output_path

def maskEdge(ds):
    height, width = ds.shape
    edge_mask = (ds.coords[ds.dims[0]] == ds.coords[ds.dims[0]].values[0]) | \
                    (ds.coords[ds.dims[0]] == ds.coords[ds.dims[0]].values[height - 1]) | \
                    (ds.coords[ds.dims[1]] == ds.coords[ds.dims[1]].values[0]) | \
                    (ds.coords[ds.dims[1]] == ds.coords[ds.dims[1]].values[width - 1])
    return ds * (edge_mask.astype(int) * -1 + 1)


def open_as_ds(path, search="*", suffix=".tif"):
    data = glob(os.path.join(path, f"{search}{suffix}"))
    buff = []
    for i in data:
        x = rxr.open_rasterio(i).isel(band=0).rename(i.split('/')[-1].split('.')[0])
        buff.append(x)
        gc.collect()
    
    buff2 = [buff[0]]
    for b in buff[1:]:
        b = b.reindex_like(buff[0], method="nearest")
        buff2.append(b)
    
    to_return = xr.merge(buff2, join='exact')
    logging.debug(to_return)
    return to_return

def merge_datasets(datasets, output):
    id = str(uuid.uuid4())
    tmp_rast = f"/tmp/{id}.tiff"
    
    if os.path.exists(output):
        os.remove(output)
    
    bashCommand = f"gdal_merge.py -n 0 -a_nodata 0 -o {tmp_rast} -co COMPRESS=LZW " + " ".join(datasets)
    process = subprocess.Popen(bashCommand.split(' '), stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line: break
        print(line, flush=True)
    
    if os.path.exists(output):
        os.remove(output)
        
    bashCommand = f"gdal_translate {tmp_rast} {output} -of COG -co COMPRESS=LZW -co SPARSE_OK=YES -co TILING_SCHEME=GoogleMapsCompatible"
    process = subprocess.Popen(bashCommand.split(' '), stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line: break
        print(line, flush=True)
    os.remove(tmp_rast)