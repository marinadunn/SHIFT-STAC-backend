#!/usr/bin/bash

### Run AWS MFA script
source aws_mfa.sh
echo "AWS MFA configured"

### Change to desired location (working directory)
echo "Change to working directory"
read -p varname "Enter folder in /discover/nobackup/projects/SBG-DO/: "
cd /discover/nobackup/projects/SBG-DO/sbg-do/$varname
pwd

### Load NCCS Python 3.9 module
module load wget/1.20.3
module load python/GEOSpyD/Min4.10.3_py3.9
echo "Modules loaded"

### Check if virtual environment already exists. If not, create it.
# venv is already loaded as part of NCCS
function try()
{ # try
    echo "Checking if virtual environment exists..."
    # activate desired venv
    source shift_env/bin/activate
} ||
{ # catch
    echo "Virtual environment does not exist, creating now."
    # create venv
    python3 -m venv shift-env
    # activate desired venv
    source shift_env/bin/activate
}

### Check if requirements file already exists. # If not already present, get from GitHub
function try()
{ # try
    echo "Checking if requirements.txt exists..."
    ls requirements.txt
    echo "File Found"
    echo "Installing packages"
    python3 -m pip install -r requirements.txt
} ||
{ # catch
    echo "File not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/requirements.txt?raw=true
    ### Install all the necessary packages
    echo "Installing packages"
    python3 -m pip install -r requirements.txt
}

### Download flight path data
# If not already present, get data download script from s3
{ # try
    echo "Checking if get_aviris_data.py exists..."
    ls get_aviris_data.py
    echo "File Found"
    echo "Downloading data"
    python3 get_aviris_data.py
    echo "Download Complete"
} ||
{ # catch
    echo "File not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/get_aviris_data.py?raw=true
    echo "Downloading data"
    python3 get_aviris_data.py
    echo "Download Complete"
}

echo "Using Python: $(which python)"
# Check for zarr creation scripts. If not already present, download zarr creation scripts from GitHub
{ # try
    echo "Checking for zarr creation scripts"
    ls make_zarr.py
    echo "File 1 Found"
} ||
{ # catch
    echo "File 1 not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/make_zarr.py?raw=true
    echo "File 1 Downloaded"
}
{ # try
    echo "Checking for zarr creation scripts"
    ls run_make_zarr_parallel.py
    echo "File 2 Found"
} ||
{ # catch
    echo "File 2 not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/run_make_zarr_parallel.py?raw=true
    echo "File 2 Downloaded"
}

### Automate SLURM job to create georeferenced zarr archives for flight paths
echo "*** Start time: $(date) *** "
# First edit appropriate variables in main() of run_make_zarr_parallel.py
# Automatically writes a bash file for each flight path in dataset list & 
# launches it as a Slurm job
python3 run_make_zarr_parrallel.py
echo "*** End time: $(date) *** "

# Remove zarr files to free space
echo "Removing Zarrs locally"
rm -r aviris/20220228/*.zarr
