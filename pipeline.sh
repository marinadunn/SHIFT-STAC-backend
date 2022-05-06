#!/usr/bin/bash

### Run AWS MFA script
source aws_mfa.sh
echo "AWS MFA configured"

### Change to desired location (working directory)
echo "Change to working directory"
read -p folder "Enter folder in /discover/nobackup/projects/SBG-DO/: "
cd /discover/nobackup/projects/SBG-DO/$folder

### Check if virtual environment already exists. If not, create it.
# venv is already loaded as part of NCCS
env = /shift_env
echo "Checking if virtual environment 'shift-env' exists..."
if [ -d "$env" ]; then
    # activate desired venv
    source shift_env/bin/activate
else
    echo "Virtual environment 'shift-env' does not exist, creating now."
    # create venv
    python3 -m venv shift-env
    # activate desired venv
    source shift_env/bin/activate
fi

### Load NCCS Python 3.9 module
module load python/GEOSpyD/Min4.10.3_py3.9
echo "Module python 3.9 loaded"
echo "Using Python: $(which python)"

### Check if requirements file already exists. # If not already present, get from GitHub
FILE = requirements.txt
echo "Checking if requirements.txt exists..."
if [ -f "$FILE" ]; then
    echo "requirements.txt found"
    echo "Installing packages"
    python3 -m pip install -r requirements.txt
else
    echo "requirements.txt not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/requirements.txt?raw=true
    ### Install all the necessary packages
    echo "Installing packages"
    python3 -m pip install -r requirements.txt
fi

### Download flight path data
# If not already present, get data download script from s3
FILE = get_aviris_data.py
echo "Checking if get_aviris_data.py exists..."
if [ -f "$FILE" ]; then
    echo "get_aviris_data.py found"
    echo "Download data now"
    python3 get_aviris_data.py
    echo "Download complete"
else
    echo "get_aviris_data.py not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/get_aviris_data.py?raw=true
    echo "Download data now"
    python3 get_aviris_data.py
    echo "Download complete"
fi

# Check for zarr creation scripts. If not already present, download zarr creation scripts from GitHub
FILE = make_zarr.py
echo "Checking for zarr creation scripts"
if [ -f "$FILE" ]; then
    echo "make_zarr.py found"
else
    echo "make_zarr.py not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/make_zarr.py?raw=true
    echo "make_zarr.py downloaded"
fi

FILE = run_make_zarr_parallel.py
if [ -f "$FILE" ]; then
    echo "run_make_zarr_parallel.py found"
else
    echo "run_make_zarr_parallel.py not found, downloading from Github"
    wget https://github.com/marinadunn/SHIFT-STAC-backend/blob/main/run_make_zarr_parallel.py?raw=true
    echo "run_make_zarr_parallel.py downloaded"
fi

### Automate SLURM job to create georeferenced zarr archives for flight paths
echo "*** Start time: $(date) *** "
# First edit appropriate variables in main() of run_make_zarr_parallel.py
# Automatically writes a bash file for each flight path in dataset list & 
# launches it as a Slurm job
python3 run_make_zarr_parrallel.py
echo "*** End time: $(date) *** "
