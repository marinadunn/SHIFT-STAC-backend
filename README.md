# SHIFT-STAC-backend
Repo for the Surface Biology and Geology (SBG) SHIFT AVIRIS-NG campaign data pipeline, including Zarr archive creation, and STAC Catalog creation/addition for [AVIRIS-NG campaign(Airborne Visible InfraRed Imaging Spectrometer)](https://avirisng.jpl.nasa.gov). [More info on AVIRIS-NG data products](https://avirisng.jpl.nasa.gov/dataportal/)

**Files include:**

-`requirements.txt`: complete list of required packages

-`get_aviris_data.py`: script to download SHIFT AVIRIS-NG data from https://avng.jpl.nasa.gov/pub/SHIFT/v0/ 

-`make_zarr.py`: script for creating Zarr archives. Args: `item` (AVIRIS flight path), `chunking` scheme, `data_path` (specified output save directory), and `store_path` (full specified output save directory including Zarr filename). Output: georeferenced Zarr archive, saved to the directory defined by `store_path` in `main(opts)`.

To change Zarr output location: modify `store_path` in the function ` main(opts)`.

-`run_make_zarr_parallel.py`: script for submitting automated SLURM job to create Zarr archive. Args: `username`, `folder_name`, and `dataset_date`, and an integer value for `x_chunk`, `y_chunk`, and `wavelength_chunk` (defines chunking scheme), and `item` (AVIRIS flight path), all defined in `main()`. This script modifies the run template `run_template.sh`, runs Python script `make_zarr.py`, and saves the georeferenced Zarr archive. 

To change Zarr output location: modify `folder_name` in `main()`, and `username` and `dataset_date` as input args from `pipeline.sh`.

To change chunking strategy: modify `x_chunk`, `y_chunk`, and `wavelength_chunk` in `main()`. To explicitly change the `item` or flight path, modify `aviris_data` list in `main()`; otherwise, will be changed by `dataset_date` input arg from `pipeline.sh`.

-`pipeline.sh`: automated pipeline for downloading AVIRIS-NG data, creating Zarr archives, creating STAC Catalog, and uploading to S3.

-`create_stac.ipynb`: Jupyter notebook for creating STAC Catalog of AVIRIS-NG data.

-`zarr_validation.ipynb`: Jupyter notebook for quickly validating Easting & Northing values of Zarr archive are corrrect.

--------------------------------------------------------------------------------------------------------

## Pipeline

The Zarr archives were created on the NASA CENTER FOR CLIMATE SIMULATION (NCCS) high-performance supercomputing cluster ["Discover"](https://www.nccs.nasa.gov/systems/discover). However the main data pipeline is not NCCS-specific, and can be run by executing the bash script `pipeline.sh`. 

Prerequisites: AWS credentials configured. Any changes to scripts already completed.

This does the following steps:
1. Runs a specific internal AWS MFA script, prompting user for MFA code to connect to SHIFT's AWS S3 buckets. Ignore this if already connected.
2. Changes to the desired working directory based on user input
3. Checks if the virtual environment `shift-env` already exists. If so, activates it. If not, creates it then activates it.
4. Loads the Python 3.9 module
5. Checks for the `requirements.txt` file. If not already present, downloads from GitHub. Installs necessary packages from requirements.txt
6. Takes dataset date, flight path, and data type (L1, L2, both) as user input args.
7. Checks for SHIFT AVIRIS data download script `get_aviris_data.py`. If not already present, downloads from GitHub.
8. Downloads flight path data.
9. Checks for Zarr creation scripts `make_zarr.py` and `run_make_zarr_parallel.py`. If not already present, downloads them from GitHub.
10. Runs automated SLURM job to create desired Zarr archives
11. Desired files are uploaded to S3.

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
## Future Considerations/Directions
This code was developed as part of a Spring 2022 NASA GSFC internship. Going forward, we hope to make this applicable to other NASA Earth science datasets. In addition, we hope to add a parallel cluster to the SHIFT SMCE environment to prevent the need for using the NCCS HPC cluster.

To apply this code to other similar data, several items will need to be modified:

1. The script `get_aviris_data.py` has been designed to specifically download L1 & L2 data from the [JPL AVIRIS-NG data portal](https://avng.jpl.nasa.gov/pub/SHIFT/v0/) using their designated naming schemes. For alternate data coming from a different source, the urls, dates, and S3 bucket will need to be changed. We used wget for ease using NCCS, but the request package can also be used (and may be preferred).
2. The data paths and chunking schemes can be changed in `make_zarr.py`, as well as the S3 bucket in `run_make_zarr_parallel.py` (or alternatively data items can be explicitly specified).
3. If creating a new STAC Catalog, data paths and Catalog/Collection/Item/Asset details in `create_stac.ipynb` will need to be modified.
4. Modify `pipeline.sh`
