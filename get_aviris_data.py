import os
'''
For SHIFT data, for a singular date, there are multiple flight paths, all of which 
have files that are required to make a Zarr archive. For L1 files, we need the igm,
igm.hdr, rdn, & rdn.hdr files. For L2a files, we need rfl & rfl.hdr.
'''
date = input("Enter date of format YYYYMMDD: ")
flight_path = input("Enter flight path of format angYYYYMMDDtHHNNSS, or 'all' for all flight paths: ")
data = input("Download 'all' data, 'L1' data only, or 'L2' data only? [all/L1/L2]: ")

def get_L1(flight_path, date):
    igm_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/{flight_path}_rdn_igm"
    rdn_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/{flight_path}_rdn_v2z4_clip"
    igm_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/{flight_path}_rdn_igm.hdr"
    rdn_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/{flight_path}_rdn_v2z4_clip.hdr"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_hdr_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_hdr_url)
    
def get_L2(flight_path, date):
    rfl_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/{flight_path}_rfl"
    rfl_hdr_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/{flight_path}_rfl.hdr"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_hdr_url)

def get_all(date):
    igm_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/"
    rdn_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/"
    rfl_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_url)

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

data_20220308 = ['ang20220308t183206',
                 'ang20220308t184127',
                 'ang20220308t185140',
                 'ang20220308t190523',
                 'ang20220308t191151',
                 'ang20220308t192816',
                 'ang20220308t194253',
                 'ang20220308t195648',
                 'ang20220308t201508',
                 'ang20220308t202617',
                 'ang20220308t204043',
                 'ang20220308t205512',
                 'ang20220308t211733',
                 'ang20220308t213310',
                 'ang20220308t214629'
                 ]

data_20220316 = ['ang20220316t183443',
                 'ang20220316t184402',
                 'ang20220316t185139',
                 'ang20220316t190239',
                 'ang20220316t191705',
                 'ang20220316t193240',
                 'ang20220316t194717',
                 'ang20220316t200240',
                 'ang20220316t202123',
                 'ang20220316t203318',
                 'ang20220316t204811',
                 'ang20220316t210303',
                 'ang20220316t211819'
                 ]

data_20220322 = ['ang20220322t192924',
                 'ang20220322t193854',
                 'ang20220322t194447',
                 'ang20220322t195241',
                 'ang20220322t200335',
                 'ang20220322t201228',
                 'ang20220322t202643',
                 'ang20220322t203801',
                 'ang20220322t204749',
                 'ang20220322t205950',
                 'ang20220322t210856',
                 'ang20220322t212712',
                 'ang20220322t215548',
                 'ang20220322t220619',
                 'ang20220322t221256'
                 ]

data_20220405 = ['ang20220405t185108',
                 'ang20220405t190223',
                 'ang20220405t191148',
                 'ang20220405t192935',
                 'ang20220405t193603',
                 'ang20220405t194236',
                 'ang20220405t195821',
                 'ang20220405t201359',
                 'ang20220405t202743',
                 'ang20220405t204007',
                 'ang20220405t205228',
                 'ang20220405t210448',
                 'ang20220405t211706',
                 'ang20220405t212916',
                 'ang20220405t214144',
                 'ang20220405t215533'
                ]

data_20220412 = ['ang20220412t185410',
                 'ang20220412t190510',
                 'ang20220412t192034',
                 'ang20220412t193109',
                 'ang20220412t194550',
                 'ang20220412t195932',
                 'ang20220412t201217',
                 'ang20220412t202627',
                 'ang20220412t203940',
                 'ang20220412t205405',
                 'ang20220412t210701',
                 'ang20220412t212151',
                 'ang20220412t215642'
                 ]

dates = ['20220224', '20220228', '20220308', '20220316', '20220322', '20220405', '20220412']

if date in dates and flight_path == 'all' and data == 'L1':    
    igm_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/igm/"
    rdn_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L1/rdn/"
    
    # wget: retrieve recursively, send to background, do not save in directories, don't ascend to parent directory
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %igm_url)
    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rdn_url)

elif date in dates and flight_path == 'all' and data == 'L2':   
    rfl_url = f"https://avng.jpl.nasa.gov/pub/SHIFT/v0/{date}/L2a/"

    os.system('wget -b -nc -nd -nH -r -np --reject html %s' %rfl_url)

elif date in dates and flight_path == 'all' and data == 'all':   
    get_all(date)

elif date in dates and flight_path != 'all' and data == 'L1':
    get_L1(flight_path, date)

elif date in dates and flight_path != 'all' and data == 'L2':
    get_L2(flight_path, date)

elif date in dates and flight_path != 'all' and data == 'all':
    get_L1(flight_path, date)
    get_L2(flight_path, date)
else:
    print("Data not found") # will add additional dates later as they become available
    exit

    