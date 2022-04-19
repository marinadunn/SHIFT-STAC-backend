import rioxarray
from rasterio.crs import CRS
import rasterio
import xarray as xr
import argparse
import numpy as np
import geopandas as gpd
import os
import zarr
import s3fs
import warnings
warnings.filterwarnings("ignore")

def make_zarr(item, chunking, data_path, store_path):

    print('\tProcessing igm file...', flush=True)
    # Read the igm file
    # NOTE: this path works if original data downloaded is not in folder_name == 'aviris_data'
    # If downloaded data is stored in folder_name == 'aviris_data' or similar, change path to 
    # igm_path = os.path.join(data_path, f"{item}_rdn_igm")
    igm_path = f"{item}_rdn_igm"
    igm = xr.open_dataset(igm_path, engine='rasterio')

    # Define easting, northing, elevation
    easting_data = igm.band_data[0].data
    northing_data = igm.band_data[1].data
    elevation_data = igm.band_data[2].data

    # Make new dataset 
    new_igm = xr.Dataset(
        {
            'Easting': (('y', 'x'), easting_data),
            'Northing': (('y', 'x'), northing_data),
            'Elevation': (('y', 'x'), elevation_data),
        },
        coords = {
            'y': ('y', igm.y.data),
            'x': ('x', igm.x.data)
        }
    )

    print('\tProcessing rfl file...', flush=True)
    # Read the rfl file under L2a/
    # NOTE: this path works if original data downloaded is not in folder_name == 'aviris_data'
    # If downloaded data is stored in folder_name == 'aviris_data' or similar, change path to 
    # rfl_path = os.path.join(data_path, f"{item}_rfl")
    rfl_path = f"{item}_rfl"
    rfl = xr.open_dataset(rfl_path, engine='rasterio')

    # Swap to be able to select based on wavelength
    rfl = rfl.swap_dims({'band': 'wavelength'})

    # Define reflectance 
    rfl = rfl.rename({'band_data': 'Reflectance'})

    # Combine rfl and igm data
    merged = rfl.merge(new_igm)

    print('\tProcessing rdn file...', flush=True)
    # Read the rdn file under L1/
    # NOTE: this path works if original data downloaded is not in folder_name == 'aviris_data'
    # If downloaded data is stored in folder_name == 'aviris_data' or similar, change path to 
    # rdn_path = os.path.join(data_path, f"{item}_rdn_v2z4_clip")
    rdn_path = f"{item}_rdn_v2z4_clip"
    rdn = xr.open_dataset(rdn_path, engine='rasterio')

    # Swap to be able to select based on wavelength
    rdn = rdn.swap_dims({'band': 'wavelength'})
    
    # Define radiance 
    rdn = rdn.rename({'band_data': 'Radiance'})

    print('\tMerging files...', flush=True)
    # Combine all data
    merged = merged.merge(rdn)
    merged = merged.transpose('x', 'y', 'wavelength')

    # Add CRS and define spatial dimensions
    merged = merged.rio.write_crs(32610, inplace=True)
    merged = merged.rio.set_spatial_dims("x", "y", inplace=True)
    
    print('\tChunk and write Zarr...', flush=True)
    # Chunk data
    if chunking is not None:
        merged = merged.chunk({'x':chunking[0], 'y':chunking[1], 'wavelength':chunking[2]})

    # Save to local store
    merged.to_zarr(store=store_path, mode='w', consolidated=True)

def setup_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, default='mmdunn1', help='username')
    # If wanting to save zarr archives in separate folder within working directory, modify folder_name and dataset_date
    parser.add_argument('--folder_name', type=str, default='', help='data folder')
    parser.add_argument('--dataset_date', type=str, default='', help='dataset date')
    parser.add_argument('--x_chunk', type=int, default=100, help='chunk size in x, set 0 for no chunking')
    parser.add_argument('--y_chunk', type=int, default=100, help='chunk size in y, set 0 for no chunking')
    parser.add_argument('--wavelength_chunk', type=int, default=100, help='chunk size in wavelength, set 0 for no chunking')
    parser.add_argument('--item', type=str, help='name of flight path')
    return parser.parse_args()

def main(opts):
    username = opts.username
    folder_name = opts.folder_name
    dataset_date = opts.dataset_date
    data_path = os.path.join(folder_name, dataset_date)
    item = opts.item
    chunking_strategy = (opts.x_chunk, opts.y_chunk, opts.wavelength_chunk)
    chunking = None if chunking_strategy==(0, 0, 0) else chunking_strategy  # If using default/no chunking, set to None

    print(f'Making zarr for dataset: {dataset_date}, item: {item}...', flush=True)
    if chunking is None:
        zarr_filepath = f'{item}_default.zarr'
    else:
        zarr_filepath = f'{item}_{chunking[0]:03d}-{chunking[1]:03d}-{chunking[2]:03d}.zarr'
    store_path = f'/discover/nobackup/projects/SBG-DO/sbg-do/{username}/{folder_name}/{dataset_date}/{zarr_filepath}'
    print(f'Store path: {store_path}', flush=True)

    make_zarr(item, chunking, data_path, store_path)
    
    # Upload zarr to s3
    s3 = s3fs.S3FileSystem(anon=False, client_kwargs=dict(region_name='us-west-2'))
    
    bucket = 'dh-shift-curated'
    key = f'testing/aviris/{dataset_date}'
    s3_key = os.path.join(bucket, key)
    s3_path = f's3://{s3_key}'
    
    zarr_files = glob.glob('*.zarr*')
    for f in zarr_files:
        s3.put(file, s3_path + '{}'.format(file), recursive=True)
        
    print("S3 move done\n")

if __name__ == '__main__':
    opts = setup_opts()
    main(opts)
    print('Done!')
