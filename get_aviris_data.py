# import requests module
import requests

'''
For SHIFT data, for a singular date, there are multiple flight paths, all of which 
have files that are required to make a Zarr archive. For L1 files, we need the igm,
igm.hdr, rdn, & rdn.hdr files. For L2a files, we need rfl & rfl.hdr.
'''

def get_L1(flight_path, date):
    # Making a get request
    r = requests.get(igm_url, allow_redirects=True)
    open(f'{flight_path}_rdn_igm', 'wb').write(r.content)

    r = requests.get(igm_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rdn_igm.hdr', 'wb').write(r.content)

    r = requests.get(rdn_url, allow_redirects=True)
    open(f'{flight_path}_rdn_v2z4_clip', 'wb').write(r.content)

    r = requests.get(rdn_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rdn_v2z4_clip.hdr', 'wb').write(r.content)
    
def get_L2(flight_path, date):
    # Making a get request       
    r = requests.get(rfl_url, allow_redirects=True)
    open(f'{flight_path}_rfl', 'wb').write(r.content)

    r = requests.get(rfl_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rfl.hdr', 'wb').write(r.content)

def get_all(flight_path, date):
    # Making a get request
    r = requests.get(igm_url, allow_redirects=True)
    open(f'{flight_path}_rdn_igm', 'wb').write(r.content)

    r = requests.get(igm_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rdn_igm.hdr', 'wb').write(r.content)

    r = requests.get(rdn_url, allow_redirects=True)
    open(f'{flight_path}_rdn_v2z4_clip', 'wb').write(r.content)

    r = requests.get(rdn_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rdn_v2z4_clip.hdr', 'wb').write(r.content)

    r = requests.get(rfl_url, allow_redirects=True)
    open(f'{flight_path}_rfl', 'wb').write(r.content)

    r = requests.get(rfl_hdr_url, allow_redirects=True)
    open(f'{flight_path}_rfl.hdr', 'wb').write(r.content)

date = input("Enter date of format YYYYMMDD: ")
flight_path = input("Enter flight path of format angYYYYMMDDtHHNNSS, or 'all' for all flight paths: ")
data = input("Download 'all' data, 'L1' data only, or 'L2' data only? [all/L1/L2]: ")

igm_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/{flight_path}_rdn_igm"
rdn_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/{flight_path}_rdn_v2z4_clip"
rfl_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/{flight_path}_rfl"

igm_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/{flight_path}_rdn_igm.hdr"
rdn_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/{flight_path}_rdn_v2z4_clip.hdr"
rfl_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/{flight_path}_rfl.hdr"

data_20220224 = [
            'ang20220224t195402',
            'ang20220224t200332',
            'ang20220224t201928',
            'ang20220224t203333',
            'ang20220224t204803',
            'ang20220224t210144',
            'ang20220224t211618',
            'ang20220224t213004',
            'ang20220224t214423',
            'ang20220224t215759',
            'ang20220224t221356',
            'ang20220224t223027'
            ]

data_20220228 = ['ang20220228t183924',
                'ang20220228t185150',
                'ang20220228t185720',
                'ang20220228t190702',
                'ang20220228t192104',
                'ang20220228t193333',
                'ang20220228t194708',
                'ang20220228t195958',
                'ang20220228t201833',
                'ang20220228t202944',
                'ang20220228t204228',
                'ang20220228t205624',
                'ang20220228t210940'
            ]

if date == '20220224' or '20220228' and flight_path == 'all':
    if date == '20220224':
        for flight_path in data_20220224:
            get_all(flight_path, date)

    elif date == '20220228':
        for flight_path in data_20220228:
            get_all(flight_path, date)

elif date == '20220224' or '20220228' and flight_path != 'all' and data == 'L1':
    get_L1(flight_path, date)

elif date == '20220224' or '20220228' and flight_path != 'all' and data == 'L2':
    get_L2(flight_path, date)

elif date == '20220224' or '20220228' and flight_path != 'all' and data == 'all':
        get_all(flight_path, date)
else:
    print("Data not found") # will add additional dates later as they become available
    exit