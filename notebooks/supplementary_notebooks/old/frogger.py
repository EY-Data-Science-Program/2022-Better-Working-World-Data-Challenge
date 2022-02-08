# Data science tools
import pandas as pd
import numpy as np

# GIS tools
import geopandas as gpd
from shapely.geometry import Point, Polygon
import xarray as xr
import rasterio as rio

# API tools
import requests
import json

# Import Planetary Computer tools
import stackstac
import pystac
import pystac_client
import planetary_computer


def get_frogs(bbox, query_params, crs = {'init':'epsg:4326'}, orderKey="952", verbose=False):
    # Set query parameters
    min_lon, min_lat, max_lon, max_lat = bbox
    limit = 300
    offset = 0
    parameters = {
        **query_params,
        "orderKey":orderKey, # The order Anura (frogs) is indicated by key 952
        "decimalLatitude":f"{min_lat},{max_lat}", # Latitude range
        "decimalLongitude":f"{min_lon},{max_lon}", # Longitude range
        "limit":limit,
        "offset":offset
    }
    
    # Query API
    frogs = pd.DataFrame()
    while True:
        # Fetch results
        parameters['offset'] = offset
        response = requests.get("https://api.gbif.org/v1/occurrence/search", params = parameters).json()
        total = response['count']
        
        # Print progress
        print(f"{offset} of {total}") if verbose else None
        
        # Add results to dataframe
        frogs = frogs.append(
            pd.DataFrame(response['results'])
            [["decimalLatitude", "decimalLongitude"]]
            .assign(
                occurrenceStatus = '1'
            )
        )
        if response['endOfRecords']:
            break
        offset += limit
        
    geo_frogs = gpd.GeoDataFrame(
        frogs.reset_index(drop=True), 
        geometry=gpd.points_from_xy(frogs.decimalLongitude, frogs.decimalLatitude),
        crs=crs
    )
        
    return geo_frogs


def get_frog_absence(geo_frogs, bbox, crs = {'init':'epsg:4326'}, granularity=(50, 50), seed=420):
    # bbox definition
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Specify granularity of grid (50x50)
    grid = np.array(granularity)

    # Calculate the step required to achieve granularity
    step = np.array([max_lat - min_lat, max_lon - min_lon])/grid

    # Define unit vectors
    up = np.array([0, 1])
    right = np.array([1, 0])

    # Bottom corner of entire bounding box
    bbox_bottom_corner = np.array([min_lon, min_lat])
    
    # bottom corner of grid unit
    bottom_corner = bbox_bottom_corner
    non_frogs = pd.DataFrame()
    for i in range(grid[0]):
        for j in range(grid[1]):

            # Define grid unit
            coords = [
                tuple(bottom_corner), 
                tuple(bottom_corner + step*up), 
                tuple(bottom_corner + step), 
                tuple(bottom_corner + step*right)
            ]
            grid_unit = Polygon(coords)

            # count all frogs that intersect with this region
            num_frogs = sum(geo_frogs.intersects(grid_unit))

            if num_frogs == 0:
                midpoint = bottom_corner + step/2
                non_frogs = non_frogs.append({'decimalLatitude':midpoint[1], 'decimalLongitude':midpoint[0]}, ignore_index=True)

            # move bottom corner to next grid unit
            bottom_corner = bbox_bottom_corner + step*np.array([i, j])
    
    np.random.seed(seed)
    non_frogs = (
        non_frogs
        # Take as many non-frogs as there are frogs
        .sample(len(geo_frogs))
        # Assign new columns
        .assign(
            occurrenceStatus = '0'
        )
        [[ "decimalLatitude", "decimalLongitude", "occurrenceStatus"]]
    )
    
    geo_non_frogs = gpd.GeoDataFrame(
        non_frogs, 
        geometry=gpd.points_from_xy(non_frogs.decimalLongitude, non_frogs.decimalLatitude),
        crs=crs
    )
    
    return geo_frogs.append(geo_non_frogs)




def get_JRC(bbox):
    
    # Get the JRC item
    stac = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    search = stac.search(
        bbox=bbox,
        collections=["jrc-gsw"]
    )
    item = list(search.get_items())[0]
    signed_item = planetary_computer.sign(item).to_dict()
        
    # Define the pixel resolution for the final product
    # Define the scale according to our selected crs, so we will use degrees
    resolution = 10  # meters per pixel 
    scale = resolution / 111320.0 # degrees per pixel for crs=4326 
    
    data = (
        stackstac.stack(
            signed_item,
            epsg=4326, # Use common Lat-Lon coordinates
            resolution=scale, # Use degrees for crs=4326
            bounds_latlon = bbox,
            resampling=rio.enums.Resampling.average, # Average resampling method (only required when resolution >10)
            chunksize=4096,  
        )
    )
    
    data = data.persist()[0]
    
    return data


def get_S2(bbox, date_range="2020-01-01/2020-12-31"):
    
    stac = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    search = stac.search(
        bbox=bbox,
        datetime=date_range,
        collections=["sentinel-2-l2a"],
        limit=500,  # fetch items in batches of 500
        query={"eo:cloud_cover": {"lt": 20}},
    )

    items = list(search.get_items())
    signed_items = [planetary_computer.sign(item).to_dict() for item in items]

    # Define the pixel resolution for the final product
    # Define the scale according to our selected crs, so we will use degrees
    resolution = 100  # meters per pixel 
    scale = resolution / 111320.0 # degrees per pixel for crs=4326 
    
    data = (
        stackstac.stack(
            signed_items,
            epsg=4326, # Use common Lat-Lon coordinates
            resolution=scale, # Use degrees for crs=4326
            bounds_latlon = bbox,
    #        resampling=rasterio.enums.Resampling.average, # Average resampling method (only required when resolution >10)
            assets=["B04", "B03", "B02", "B08"],  # Red, Green, Blue, NIR
            chunksize=4096,  
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )
    
    data = data.persist()
    
    # Median Composite
    median = data.median(dim="time").compute()
    
    return median




def get_pc(product, bbox, assets={"image/tiff"}, resolution=10, pc_query=None, date_range=None):
    # Query the planetary computer
    stac = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    search = stac.search(
        bbox=bbox,
        datetime=date_range,
        collections=[product],
        limit=500,  # fetch items in batches of 500
        query=pc_query
    )
    items = list(search.get_items())
    print('This is the number of scenes that touch our region:',len(items))
    signed_items = [planetary_computer.sign(item).to_dict() for item in items]

    # Define the scale according to our selected crs, so we will use degrees
    scale = resolution / 111320.0 # degrees per pixel for crs=4326 
        
    # Stack up the items returned from the planetary computer
    data = (
        stackstac.stack(
            signed_items,
            epsg=4326, # Use common Lat-Lon coordinates
            resolution=scale, # Use degrees for crs=4326
            bounds_latlon = bbox,
            resampling=rio.enums.Resampling.average, # Average resampling method (only required when resolution >10)
            chunksize=4096,
            assets=assets
        )
    )
    
    # Median Composite
    median = data.median(dim="time").compute()
    
    return median