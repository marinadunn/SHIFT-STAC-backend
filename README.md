# SHIFT-STAC-backend
Repo for the Surface Biology and Geology (SBG) SHIFT AVIRIS-NG campaign

Includes pipeline for zarr archive creation, and STAC Catalog creation/addition for [AVIRIS-NG campaign(Airborne Visible InfraRed Imaging Spectrometer)](https://avirisng.jpl.nasa.gov). [More info on AVIRIS-NG data products](https://avirisng.jpl.nasa.gov/dataportal/)

Files include:

-`requirements.txt`: the complete list of required packages

-`get_aviris_data.py`: the script to download AVIRIS data from https://avng.jpl.nasa.gov/pub/SHIFT/v0/ given a user-specified date

-`make_zarr.py`: the script for creating Zarr archives 

-`run_make_zarr_parallel.py`: the script for submitting a SLURM job to create a Zarr archive for a specified flight path.

## Pipeline

The pipeline is currently set up to be run on the NASA CENTER FOR CLIMATE SIMULATION (NCCS) high-performance supercomputing cluster ["Discover"](https://www.nccs.nasa.gov/systems/discover). After logging into the cluster, it can be run by executing the bash script `pipeline.sh`. 

This does the following steps:
1. Runs a specific AWS MFA script, prompting user for MFA code to connect to SHIFT's AWS S3 buckets.
2. Changes to the desired working directory based on user input
3. Loads the Python 3.9 & wget 1.20.3 modules (already on NCCS)
4. Checks if the virtual environment `shift-env` already exists. If so, activates it. If not, creates it then activates it.
6. Checks for the `requirements.txt` file. If not already present, downloads from GitHub.
7. Installs all the necessary packages from requirements.txt
8. Checks for SHIFT AVIRIS data download script `get_aviris_data.py`. If not already present, downloads from GitHub.
9. Downloads flight path data.
10. Checks for Zarr creation scripts `make_zarr.py` and `run_make_zarr_parallel.py`. If not already present, downloads them from GitHub.
11. Runs SLURM job to create desired Zarr archives and plots.
12. Uploads zarr archives and plots to the AWS s3://dh-shift-curated/ S3 bucket.

## STAC
The SpatioTemporal Asset Catalog (STAC) specifies a standard language for structuring and querying geospatial data and metadata. The STAC specification is designed around the extensibility & flexibility of JSON, and is comprised of Catalogs, Collections, Items, and the API.

STAC Catalog: JSON object that contains list of STAC Items, or other child STAC Catalogs. Can be further extended to include additional metadata. No restictions for organization; typically uses ‘sub-catalog’ groupings. [More about STAC Catalog Specification](https://github.com/radiantearth/stac-spec/tree/master/catalog-spec)

STAC Collection: JSON object containing additional info describing the spatial and temporal extents of data; extension of Catalog. Can be further extended to include additional metadata. [More about STAC Collection Specification](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md)

STAC Item: a GeoJSON feature with descriptive attributes that define its time range and assets; a collection of inseparable data & metadata. Represented in a flexible JSON format. Can indlude additonal fields & JSON structures for further customizing data searches. [More about STAC Item Specification](https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md)

The SBG-SHIFT STAC Catalog is grouped into the following hierarchy:
```
SBG-SHIFT STAC Catalog 
│
└─── AVIRIS-NG (Collection)
│   │
│   └─── <flight line> (Item)
```
where <flight line> is a STAC item of date form `YYYYMMDD` (see below). For each of these items, there are assets/datasets of form `angYYYYMMDDtHHNNSS.zarr`, a GeoJSON file of the flight outline, and an RGB composite image. 
```  
YYYY:  The year of the airborne flight run.
MM:    The month of the airborne flight run (i.e. 05 represents May).
DD:    The day of the airborne flight run (22 is the 22nd day of the month).
HH:    UTC hour at the start of acquisition
NN:    UTC minute at the start of acquisition
SS:    UTC second at the start of acquisition
```  
