# SHIFT-STAC-backend
Repo for the Surface Biology and Geology (SBG) SHIFT AVIRIS-NG campaign data pipeline, including Zarr archive creation, and STAC Catalog creation/addition for [AVIRIS-NG campaign(Airborne Visible InfraRed Imaging Spectrometer)](https://avirisng.jpl.nasa.gov). [More info on AVIRIS-NG data products](https://avirisng.jpl.nasa.gov/dataportal/)

**Files include:**

-`requirements.txt`: complete list of required packages

-`get_aviris_data.py`: script to download SHIFT AVIRIS-NG data from https://avng.jpl.nasa.gov/pub/SHIFT/v0/ 

-`make_zarr.py`: script for creating Zarr archives. Args: `item` (AVIRIS flight path), `chunking` scheme, `data_path` (specified output save directory), and `store_path` (full specified output save directory including Zarr filename). Set up as arguments in the function `main(opts)`. Output: georeferenced Zarr archive, saved to the directory defined by `store_path` in `main(opts)`.

To change Zarr output location: modify `username`, `folder_name`, and `dataset_date` in `setup_opts()`, and `store_path` in the function ` main(opts)`. `dataset_date` should correspond to the date in `YYYYMMDD` format for which there is SHIFT AVIRIS-NG data. 

To change chunking strategy: modify `x_chunk`, `y_chunk`, and `wavelength_chunk` in `setup_opts()`. `item` can also be modified to be explicitly defined in the function `setup_opts()`; or, if using this in combination with `run_make_zarr_parallel.py`, simply leave as is and modify list `aviris_data` in `run_make_zarr_parallel.py`.

-`run_make_zarr_parallel.py`: script for submitting automated SLURM job to create Zarr archive for specified flight paths. Args: `username`, `folder_name`, and `dataset_date` (specifies the output save directory), and an integer value for `x_chunk`, `y_chunk`, and `wavelength_chunk` (defines chunking scheme), and `item` (AVIRIS flight path), all defined in `main()`. This modifies the run template `run_template.sh`, runs Python script `make_zarr.py`, and saves the georeferenced Zarr archive. 

To change Zarr output location: modify `username`, `folder_name`, and `dataset_date` in `main()`. 

To change chunking strategy: modify `x_chunk`, `y_chunk`, and `wavelength_chunk` in `main()`. To change the `item` or flight path, modify `aviris_data` list in `main()`.

-`pipeline.sh`: automated pipeline for downloading AVIRIS-NG data, creating Zarr archives, creating STAC Catalog, and uploading to S3.

-`create_stac.py`: script for creating STAC Catalog of AVIRIS-NG data. STAC Items are Zarr archives from various flight paths.

--------------------------------------------------------------------------------------------------------

## Pipeline

The pipeline is currently set up to be run on the NASA CENTER FOR CLIMATE SIMULATION (NCCS) high-performance supercomputing cluster ["Discover"](https://www.nccs.nasa.gov/systems/discover). It can be run by executing the bash script `pipeline.sh`. 

Prerequisites: AWS credentials configured. Any changes to scripts already completed.

This does the following steps:
1. Runs a specific AWS MFA script, prompting user for MFA code to connect to SHIFT's AWS S3 buckets.
2. Changes to the desired working directory based on user input
3. Loads the Python 3.9 module
4. Checks if the virtual environment `shift-env` already exists. If so, activates it. If not, creates it then activates it.
6. Checks for the `requirements.txt` file. If not already present, downloads from GitHub.
7. Installs all the necessary packages from requirements.txt
8. Checks for SHIFT AVIRIS data download script `get_aviris_data.py`. If not already present, downloads from GitHub.
9. Downloads flight path data.
10. Checks for Zarr creation scripts `make_zarr.py` and `run_make_zarr_parallel.py`. If not already present, downloads them from GitHub.
11. Runs automated SLURM job to create desired Zarr archives and uploads to S3.

--------------------------------------------------------------------------------------------------------

## STAC Specifics
The SpatioTemporal Asset Catalog (STAC) specifies a standard language for structuring and querying geospatial data and metadata. The STAC specification is designed around the extensibility & flexibility of JSON, and is comprised of Catalogs, Collections, Items, and the API.

**STAC Catalog**: JSON object that contains list of STAC Items, or other child STAC Catalogs. Can be further extended to include additional metadata. No restictions for organization; typically uses ‘sub-catalog’ groupings. [More about STAC Catalog Specification](https://github.com/radiantearth/stac-spec/tree/master/catalog-spec)

**STAC Collection**: JSON object containing additional info describing the spatial and temporal extents of data; extension of Catalog. Can be further extended to include additional metadata. [More about STAC Collection Specification](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md)

**STAC Item**: GeoJSON feature with descriptive attributes that define its time range and assets; a collection of inseparable data & metadata. Represented in a flexible JSON format. Can indlude additonal fields & JSON structures for further customizing data searches. [More about STAC Item Specification](https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md)

STAC Catalog hierarchy:
```
SBG-SHIFT STAC Catalog 
│
└─── AVIRIS-NG (Collection)
│   │
│   └─── <flight line> (Item)
```
where each STAC item is a flight line of format `angYYYYMMDDtHHNNSS`, and its asset is the Zarr dataset of format `angYYYYMMDDtHHNNSS.zarr`.

```  
YYYY:  The year of the airborne flight run.
MM:    The month of the airborne flight run (i.e. 05 represents May).
DD:    The day of the airborne flight run (22 is the 22nd day of the month).
HH:    UTC hour at the start of acquisition
NN:    UTC minute at the start of acquisition
SS:    UTC second at the start of acquisition
```  
