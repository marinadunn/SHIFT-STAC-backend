import rioxarray
import xarray as xr
import numpy as np

import os
import s3fs
import glob
import pathlib

import dask.array
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import geopandas as gpd
from shapely.geometry import box, mapping, Polygon
import warnings
warnings.filterwarnings("ignore")

import json
import shutil
import tempfile
from datetime import date, datetime

# Connect to AWS S3 storage
s3 = s3fs.S3FileSystem(anon=False, client_kwargs=dict(region_name="us-west-2"))

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

def make_plots(dataset_date, zarr):  

    print("Starting plots")
    Prefix = f"aviris/{dataset_date}/{zarr}"
    s3_key = os.path.join(Bucket, Prefix)
    s3_url = os.path.join("s3://", s3_key)
    
    # Open flight path zarr
    store = s3fs.S3Map(root=s3_url, s3=s3, check=False)
    ds = xr.open_zarr(store=store, decode_coords="all", consolidated=True)
    # set Easting & Northing as coords for plotting
    ds = ds.set_coords(("Easting", "Northing"))
    
    ## Make Plots    
    # Select best bands for RGB composite 
    R = ds.isel(wavelength=59).Reflectance
    G = ds.isel(wavelength=35).Reflectance
    B = ds.isel(wavelength=14).Reflectance
    rgb = ds.isel(wavelength=[50,35,14]).Reflectance
    
    # The RGB array for the true color image
    RGB = np.dstack([R, G, B])
    # The RGB for the true color image
    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot()
    ax.imshow(RGB)
    ax.set_title(f"{zarr} RGB Reflectance True Color", fontsize=12)
    ax.set_axis_off()
    plt.savefig(f"{zarr}_RGB_Reflectance_True_Color.jpg")

    # The RGB for the higher-exposure reflectance
    norm_reflectance = rgb / 0.7
    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot()
    ax.imshow(norm_reflectance)
    ax.set_title(f"{zarr} RGB Increased Exposure Reflectance", fontsize=12)
    ax.set_axis_off()
    plt.savefig(f"{zarr}_RGB_Increased_Exposure_Reflectance.jpg")

    # R plot
    fig, ax = plt.subplots(figsize=(10, 6))
    R.plot.pcolormesh("Easting", "Northing", robust=True, add_colorbar=False)
    plt.xlabel("Easting (m)")
    plt.ylabel("Northing (m)")
    ax.set_title(f"{zarr} R Reflectance, 672.6 nm", fontsize=12)
    plt.savefig(f"{zarr}_R_Reflectance.jpg")
    
    # G plot
    fig, ax = plt.subplots(figsize=(10, 6))
    G.plot.pcolormesh("Easting", "Northing", robust=True, add_colorbar=False)
    plt.xlabel("Easting (m)")
    plt.ylabel("Northing (m)")
    ax.set_title(f"{zarr} G Reflectance, 552.4 nm", fontsize=12)
    plt.savefig(f"{zarr}_G_Reflectance.jpg")
    
    # B plot
    fig, ax = plt.subplots(figsize=(10, 6))
    B.plot.pcolormesh("Easting", "Northing", robust=True, add_colorbar=False)
    plt.xlabel("Easting (m)")
    plt.ylabel("Northing (m)")
    ax.set_title(f"{zarr} B Reflectance, 447.2 nm", fontsize=12)
    plt.savefig(f"{zarr}_B_Reflectance.jpg")
    print("Plots done!")
    
    # Upload jpegs to s3
    s3.put(f"{zarr}_RGB_Reflectance_True_Color.jpg", f"s3://dh-shift-curated/aviris/{dataset_date}/" + "{}".format(f"{zarr}_RGB_Reflectance_True_Color.jpg"))
    s3.put(f"{zarr}_RGB_Increased_Exposure_Reflectance.jpg", f"s3://dh-shift-curated/aviris/{dataset_date}/" + "{}".format(f"{zarr}_RGB_Increased_Exposure_Reflectance.jpg"))
    s3.put(f"{zarr}_R_Reflectance.jpg", f"s3://dh-shift-curated/aviris/{dataset_date}/" + "{}".format(f"{zarr}_R_Reflectance.jpg"))
    s3.put(f"{zarr}_G_Reflectance.jpg", f"s3://dh-shift-curated/aviris/{dataset_date}/" + "{}".format(f"{zarr}_G_Reflectance.jpg"))
    s3.put(f"{zarr}_B_Reflectance.jpg", f"s3://dh-shift-curated/aviris/{dataset_date}/" + "{}".format(f"{zarr}_B_Reflectance.jpg"))
    print("S3 upload done!")

# Change dataset_date 
Bucket = "dh-shift-curated"
dataset_date = "20220228"
data = get_zarrs(Bucket, dataset_date)
for zarr in data:
    item = make_plots(dataset_date, zarr)