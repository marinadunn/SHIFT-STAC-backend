import rioxarray
import rasterio
from rasterio.transform import Affine
from rasterio.plot import plotting_extent
from rasterio.crs import CRS
import xarray as xr
import numpy as np

import os
import boto3
import s3fs
import glob
import pathlib

import dask.array
import pandas as pd

import geopandas as gpd
import shapely.geometry
from shapely.geometry import box, mapping, Polygon
from shapely.coords import CoordinateSequence
import warnings

import json
import shutil
import tempfile
from datetime import date
from datetime import datetime
from urllib.parse import urlparse
from pprint import pprint

import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.view import ViewExtension

#  Suppress warnings issued by Cartopy when downloading data files
warnings.filterwarnings("ignore")

# Connect to AWS S3 storage
s3 = s3fs.S3FileSystem(anon=False, client_kwargs=dict(region_name="us-west-2"))

# generate catalog for root
catalog = pystac.Catalog(id="SBG-SHIFT", 
                         description="STAC catalog for the SBG-SHIFT AVIRIS-NG campaign", 
                        )

# Create collection for the AVIRIS-NG
dt1 = datetime(2022, 2, 28, 0)
dt2 = datetime(2022, 5, 31, 0)
collection_interval = sorted([dt1, dt2])
temporal_extent = pystac.TemporalExtent(intervals=[collection_interval])
spatial_extent = pystac.SpatialExtent([[705900,  3802100, 825900, 3868100]])
extent = pystac.Extent(spatial_extent, temporal_extent)
collection = pystac.Collection(id='AVIRIS-NG',
                               description='SBG-SHIFT AVIRIS_NG data',
                               license = 'MIT',
                               extent=extent
                              )

collection.providers = [
    pystac.Provider(name="AVIRIS-NG", roles=[pystac.ProviderRole.PRODUCER], url="https://avirisng.jpl.nasa.gov/aviris-ng.html"),
    pystac.Provider(name="SBG", roles=[pystac.ProviderRole.HOST], url="https://sbg.jpl.nasa.gov")
]

# Get all key urls for datasets in S3 bucket.
# From https://alexwlchan.net/2017/07/listing-s3-keys/

def get_s3_keys(bucket, prefix):
    s3 = boto3.client("s3")
    kwargs = {"Bucket": bucket, "Prefix": prefix}
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp["Contents"]:
            yield obj["Key"]

        try:
            kwargs["ContinuationToken"] = resp["NextContinuationToken"]
        except KeyError:
            break


def get_zarrs(Bucket, dataset_date):
    Prefix = f"aviris/{dataset_date}/"
    urls = list(get_s3_keys(bucket=Bucket, prefix=Prefix))
    s3_key = os.path.join(Bucket, Prefix)
    s3_url = os.path.join("s3://", s3_key)
    
    substring = "100-100-100.zarr"
    links = []

    for link in urls:
        if substring in link:
            url = link[:link.index(substring) + len(substring)]
            zarr = url.replace(f"aviris/{dataset_date}/", "")
            links.append(str(zarr))
            
    data_set = set(links)
    data = list(data_set)
    #pprint(data)
    return data

def create_item(dataset_date, zarr):
    
    Bucket = "dh-shift-curated"
    Prefix = f"aviris/{dataset_date}/{zarr}"
    s3_key = os.path.join(Bucket, Prefix)
    s3_url = os.path.join("s3://", s3_key)
    
    # Open flight path zarr
    store = s3fs.S3Map(root=s3_url, s3=s3, check=False)
    ds = xr.open_zarr(store=store, decode_coords="all", consolidated=True)
    print("Zarr read done!")
    # set Easting & Northing as coords for plotting
    ds = ds.set_coords(("Easting", "Northing"))
    
    # Calculate extent, bbox, and footprint using Easting & Northing
    ul = ds.isel(x=0, y=0)  # Upper left corner
    ur = ds.isel(x=-1, y=0) # Upper right corner
    ll = ds.isel(x=0, y=-1) # Lower left corner
    lr = ds.isel(x=-1, y=-1) # Lower right corner
    
    ul2 = (ul.Easting.values, ul.Northing.values)
    ur2 = (ur.Easting.values, ur.Northing.values)
    ll2 = (ll.Easting.values, ll.Northing.values)
    lr2 = (lr.Easting.values, lr.Northing.values)
    extent = Polygon((ul2, ll2, lr2, ur2))
    footprint = mapping(extent)
    
    exterior_coords = list(extent.exterior.coords)
    l = exterior_coords[3]
    b = exterior_coords[4]
    r = exterior_coords[1]
    t = exterior_coords[2]
    
    min_x_coords = l
    minx = min_x_coords[0]
    min_y_coords = b
    miny = min_y_coords[1]

    max_x_coords = r
    maxx = max_x_coords[0]
    max_y_coords = t
    maxy = max_y_coords[1]
    
    # left, bottom, right, top
    bbox = [minx, miny, maxx, maxy]
    BBox = box(minx, miny, maxx, maxy)
    boundary = gpd.GeoDataFrame({"geometry": BBox}, index=[0])
    
    if dataset_date =="20220224":
        dt = datetime(2022, 2, 24, 0)
    elif dataset_date =="20220228":
        dt = datetime(2022, 2, 28, 0)
        
    item = pystac.Item(id=f"{zarr}", 
                    geometry=footprint, 
                    bbox=bbox, 
                    datetime=dt, 
                    properties={})
    
    # Add projection
    proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    # get crs
    crs = ds.rio.crs
    proj_ext.epsg = crs.to_epsg()
    print("Item created!")
    return item

def add_assets(dataset_date, item, zarr):
    print("Adding assets")
    # Add Assets
    item.add_asset(
        key="dataset",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}"
        )
    )

    item.add_asset(
        key=f"{zarr} RGB True Color Reflectance image",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}_RGB_Reflectance_True_Color",
            media_type=pystac.MediaType.JPEG
        )
    )

    item.add_asset(
        key=f"{zarr} RGB Increased Exposure Reflectance image",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}_RGB_Increased_Exposure_Reflectance.jpg",
            media_type=pystac.MediaType.JPEG
        )
    )

    item.add_asset(
        key=f"{zarr} R Band Reflectance image",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}_R_Reflectance.jpg",
            media_type=pystac.MediaType.JPEG
        )
    )

    item.add_asset(
        key=f"{zarr} G Band Reflectance image",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}_G_Reflectance.jpg",
            media_type=pystac.MediaType.JPEG
        )
    )

    item.add_asset(
        key=f"{zarr} B Band Reflectance image",
        asset=pystac.Asset(
            href=f"s3://dh-shift-curated/aviris/{dataset_date}/{zarr}_B_Reflectance.jpg",
            media_type=pystac.MediaType.JPEG
        )
    )

# for 20220228
Bucket = "dh-shift-curated"
dataset_date = "20220228"
data = get_zarrs(Bucket, dataset_date)
for zarr in data:
    item = create_item(dataset_date, zarr)
    add_assets(dataset_date, item, zarr)
    
    # add item to collection
    collection.add_item(item)
    print(f"Item {zarr} added!")

# Repeat for 20220224
Bucket = "dh-shift-curated"
dataset_date = "20220224"
data = get_zarrs(Bucket, dataset_date)
for zarr in data:
    item = create_item(dataset_date, zarr)
    add_assets(dataset_date, item, zarr)
    
    # add item to collection
    collection.add_item(item)
    print(f"Item {zarr} added!")

# Add collection to catalog
catalog.add_child(collection)

# Save catalog to working dir, then upload to s3
catalog.normalize_hrefs('SBG-SHIFT')
catalog.validate_all()
catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
# upload to s3
s3.put('SBG-SHIFT', f"s3://dh-shift-curated/aviris/" + "{}".format('SBG-SHIFT'), recursive=True)
print('S3 upload done!')