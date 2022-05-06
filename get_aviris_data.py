import os
import sys
import boto3

'''
For SHIFT data, for a singular date, there are multiple flight paths, all of which 
have files that are required to make a Zarr archive. For L1 files, we need the igm,
igm.hdr, rdn, & rdn.hdr files. For L2a files, we need rfl & rfl.hdr.
'''

def get_L1(flight_path, dataset_date):
    igm_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L1/igm/{flight_path}_rdn_igm"
    rdn_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L1/rdn/{flight_path}_rdn_v2z4_clip"
    igm_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L1/igm/{flight_path}_rdn_igm.hdr"
    rdn_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L1/rdn/{flight_path}_rdn_v2z4_clip.hdr"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_hdr_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_hdr_url)
    
def get_L2(flight_path, dataset_date):
    rfl_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L2a/{flight_path}_rfl"
    rfl_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{dataset_date}/L2a/{flight_path}_rfl.hdr"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_hdr_url)

dates = ['20220224', '20220228', '20220308', '20220316', '20220322', '20220405', '20220412']
dataset_date = sys.argv[1]
flight_path = sys.argv[2]
data = sys.argv[3]

s3 = boto3.client('s3')
Bucket = "dh-shift-curated"
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
            item_name = zarr[:zarr.index(substring)-1]
            links.append(str(item_name))

    try:
        kwargs['ContinuationToken'] = objects['NextContinuationToken']
    except KeyError:
        break
data_set = set(links)
aviris_data = list(data_set)

if dataset_date in dates:
    if flight_path == 'all':
        if data == 'L1':
            for item_name in aviris_data:
                get_L1(item_name, dataset_date)

        elif data == 'L2':
            for item_name in aviris_data:
                get_L2(item_name, dataset_date)

        elif data == 'all':
            for item_name in aviris_data:  
                get_L1(item_name, dataset_date)
                get_L2(item_name, dataset_date)

    elif flight_path != 'all':
        if data == 'L1':
            get_L1(flight_path, dataset_date)

        elif data == 'L2':
            get_L2(flight_path, dataset_date)

        elif data == 'all':
            get_L1(flight_path, dataset_date)
            get_L2(flight_path, dataset_date)
else:
    print("Data not found")
    exit

    