"""
Created by Marina Dunn
Creates a STAC Catalog of Zarr datasets for the SBG-SHIFT AVIRIS-NG campaign. 
Kept on AWS S3 bucket.
"""
import rioxarray
import xarray as xr
import numpy as np

import os
os.environ["AWS_NO_SIGN_REQUEST"] = "true"
import glob
import pathlib
import pandas as pd
import json
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import s3fs
import shutil
import tempfile
from typing import Any, Dict, Generic, Iterable, List, Optional, TypeVar, Union, cast
from datetime import datetime
from pprint import pprint

import geopandas as gpd
from shapely.geometry import box, mapping, Polygon
import warnings
warnings.filterwarnings("ignore")

import satstac
import stackstac

import pystac
from pystac import Catalog, get_stac_version, Collection, Item, STACObject, CatalogType, Link
from pystac.stac_io import DefaultStacIO, StacIO
from pystac.extensions.projection import AssetProjectionExtension, ProjectionExtension
from pystac_client import Client, CollectionClient
from pystac_client.item_search import ItemSearch
from pystac_client.stac_api_io import StacApiIO

Bucket = "dh-shift-curated"
href = "https://dh-shift-curated.s3.us-west-2.amazonaws.com"
s3 = boto3.client('s3', region_name='us-west-2')

class CustomStacIO(DefaultStacIO):
    def __init__(self):
        self.s3 = boto3.resource("s3")

    def read_text(
        self, source: Union[str, Link], *args: Any, **kwargs: Any
        ) -> str:
        parsed = urlparse(uri)
        if parsed.scheme == "s3":
            bucket = parsed.netloc
            key = parsed.path[1:]

            obj = self.s3.Object(bucket, key)
            return obj.get()["Body"].read().decode("utf-8")
        else:
            return super().read_text(source, *args, **kwargs)

    def write_text(
        self, dest: Union[str, Link], txt: str, *args: Any, **kwargs: Any
        ) -> None:
        parsed = urlparse(uri)
        if parsed.scheme == "s3":
            bucket = parsed.netloc
            key = parsed.path[1:]
            self.s3.Object(bucket, key).put(Body=txt, ContentEncoding="utf-8")
        else:
            super().write_text(dest, txt, *args, **kwargs)

StacIO.set_default(CustomStacIO)

# Create root STAC catalog
catalog_url = os.path.join(href, "/aviris/SBG-SHIFT-Catalog/catalog.json")

catalog = pystac.Catalog(id="SBG-SHIFT", 
                         description="STAC catalog for the SBG-SHIFT AVIRIS-NG campaign",
                         title="SBG SHIFT STAC Catalog",
                         stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'],
                         href = catalog_url,
                         catalog_type = 'ABSOLUTE_PUBLISHED'
                        )

# Create collection for AVIRIS-NG
# should include AVIRIS-NG-”raw”, (Eventually) AVIRIS-NG-mosaic, Distance to roads, NAIP imagery, DEM
dt1 = datetime(2022, 2, 28, 0) # first flight date
dt2 = datetime(2022, 5, 31, 0) # last day of study
collection_interval = sorted([dt1, dt2])

temporal_extent = pystac.TemporalExtent(intervals=[collection_interval])
spatial_extent = pystac.SpatialExtent([[705900,  3802100, 825900, 3868100]]) # covers all SHIFT fields
extent = pystac.Extent(spatial_extent, temporal_extent)

collection_url = os.path.join(href, "/aviris/SBG-SHIFT-Catalog/collection.json")

collection = pystac.Collection(id='AVIRIS-NG',
                               description='SBG-SHIFT AVIRIS_NG data',
                               href=collection_url,
                               license = 'MIT',
                               extent=extent,
                               stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json']
                              )

collection.providers = [
    pystac.Provider(name="AVIRIS-NG", roles=[pystac.ProviderRole.PRODUCER], url="https://avirisng.jpl.nasa.gov/aviris-ng.html"),
    pystac.Provider(name="SBG", roles=[pystac.ProviderRole.HOST], url="https://sbg.jpl.nasa.gov")
]
# Read in data from S3 bucket
def get_zarrs(Bucket, dataset_date):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    Prefix = f'aviris/{dataset_date}'
    kwargs = {'Bucket': Bucket, 'Prefix': Prefix}
    substring = '100-100-100.zarr'
    links = []
    while True:
        objects = s3.list_objects_v2(**kwargs)
        for obj in objects['Contents']:
            if substring in obj['Key']:
                key = obj['Key']
                url = key[:key.index(substring)+ len(substring)]
                zarr = url.replace(f"aviris/{dataset_date}/", "")
                links.append(str(zarr))
            
        try:
            kwargs['ContinuationToken'] = objects['NextContinuationToken']
        except KeyError:
            break
     
    data_set = set(links)
    data = list(data_set)
    #pprint(data) # see results
    return data

# Each flight line is its own item; Each Zarr is its own asset, Flight outline as GeoJSON, RGB composite
def create_items_add_assets(Bucket, dataset_date, zarr):
    Prefix = f"aviris/{dataset_date}/{zarr}"
    s3_key = os.path.join(Bucket, Prefix)
    
    # Open flight path zarr
    store = s3fs.S3Map(root=s3_key, s3=s3, check=False)
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

    # save flight outline as GeoJSON and upload to s3
    substring = '_100-100-100.zarr'
    item_name = zarr[:zarr.index(substring)]
    gpd.GeoDataFrame({"geometry": extent}, index=[0]).to_file(f"{item_name}_flight_outline.geojson", driver='GeoJSON')
    kwargs = {'Bucket': Bucket, 'Key': f"aviris/{dataset_date}/{item_name}_flight_outline.geojson"}
    s3.put_object(**kwargs)
    
    exterior_coords = list(extent.exterior.coords)
    l = exterior_coords[3]
    b = exterior_coords[4]
    r = exterior_coords[1]
    t = exterior_coords[2]
    
    minx = l[0]
    miny = b[1]
    maxx = r[0]
    maxy = t[1]
    
    # left, bottom, right, top
    bbox = [minx, miny, maxx, maxy]
    
    # create datetime object from date string
    dt = datetime.datetime.strptime(dataset_date, f"%Y%m%d")
    
    item_url = os.path.join(href, "/aviris/SBG-SHIFT/AVIRIS-NG/{item_name}.json")

    # item should be flight line
    item = pystac.Item(id=f"{item_name}",
                    geometry=footprint, 
                    bbox=bbox, 
                    datetime=dt,
                    href=item_url,
                    stac_extensions=['https://stac-extensions.github.io/projection/v1.0.0/schema.json'],
                    properties={},
                    collection_id = 'AVIRIS-NG'
                      )
    # add instrument metadata
    item.common_metadata.instruments = ['AVIRIS-NG']

    # add projection extension to item
    proj_ext = ProjectionExtension.ext(item, add_if_missing = True)
    proj_ext.epsg = 32610
    print("Item created!")
    
    # Add dataset asset
    print("Adding assets")
    item.add_asset(
        key="dataset",
        asset=pystac.Asset(
            href=os.path.join(href, f"aviris/{dataset_date}/{zarr}")
        )
    )

    # extend the asset with projection extension
    asset_ext = AssetProjectionExtension.ext(item.assets["dataset"])
    asset_ext.epsg = 32610
    asset_ext.bbox = bbox
    asset_ext.geometry = footprint

    # Add flight outline GeoJSON asset
    item.add_asset(
        key="Flight Outline",
        asset=pystac.Asset(
            href=os.path.join(href, f"aviris/{dataset_date}/{item_name}_flight_outline.geojson"),
            media_type=pystac.MediaType.GEOJSON
            )
    )
    print("Assets added!")

# additional dates after 20220412 to be added later
dates = ['20220224', '20220228', '20220308', '20220316', 
        '20220322', '20220405', '20220412'#, 
        #'20220420', '20220429', '20220503'
        ]

for dataset_date in dates:
    data = get_zarrs(Bucket, dataset_date)
    
    for zarr in data:
        # create STAC item and add assets, including Zarr dataset
        item = create_items_add_assets(Bucket, dataset_date, zarr)
        
        # add item to collection
        collection.add_item(item)
        print(f"{item_name} added to collection!")

# Add STAC Collection to STAC catalog
catalog.add_child(collection)
print("Number of Catalog Items:", len(list(catalog.get_items())))
catalog.describe()
catalog.validate_all()

# Save STAC Catalog then upload to s3
catalog.normalize_and_save(catalog_url, 
    catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED, 
    stac_io=StacIO.set_default(CustomStacIO)
    )
print('S3 upload done!')
