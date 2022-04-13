import os

#for every flight path, download L1 igm & igm.hdr, L1 rdn & rdn.hdr, L2a rfl & rfl.hdr
def get_data(date):
    
    L2_url = "https://avng.jpl.nasa.gov/pub/SHIFT/v0/%s/L2a/" % date
    igm_url = "https://avng.jpl.nasa.gov/pub/SHIFT/v0/%s/L1/igm/" % date
    rdn_url = "https://avng.jpl.nasa.gov/pub/SHIFT/v0/%s/L1/rdn/" % date

    os.system('/usr/local/other/wget/1.20.3/bin/wget -r -np -nc %s 2>&1 | grep -i "Error" && break' %L2_url)
    os.system('/usr/local/other/wget/1.20.3/bin/wget -r -np -nc %s 2>&1 | grep -i "Error" && break' %igm_url)
    os.system('/usr/local/other/wget/1.20.3/bin/wget -r -np -nc %s 2>&1 | grep -i "Error" && break' %rdn_url)

date = input("Enter date of format YYYYMMDD: ")
get_data(date)