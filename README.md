# SHIFT-STAC
Repo for the Surface Biology and Geology (SBG) SHIFT AVIRIS-NG campaign

Includes pipeline for zarr archive creation, and STAC Catalog creation/addition for [AVIRIS-NG campaign(Airborne Visible InfraRed Imaging Spectrometer)](https://avirisng.jpl.nasa.gov). Examples are provided in mainly Python, with some R examples.

[Data products portal](https://avirisng.jpl.nasa.gov/dataportal/)

## Pipeline
The complete list of required packages is provided in `requirements.txt`.

The pipeline is currently set up to be run on the NASA CENTER FOR CLIMATE SIMULATION (NCCS) high-performance supercomputing cluster ["Discover"](https://www.nccs.nasa.gov/systems/discover). After logging into the cluster, it can be run by executing the bash script `pipeline.sh`. 


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
