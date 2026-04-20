from herbie import FastHerbie
import pandas as pd
import numpy as np
import xarray as xr
import os

# file path for latest dataset
DATA_FILE = "/courses/meteo473/sp26/473_sp26_group6/auto_data/ecmwf_latest.nc"
# downloading lateset run
run = (pd.Timestamp.now() - pd.Timedelta(hours=6)).floor("6h")

H = FastHerbie([run], model="ifs", product="oper", fxx=np.arange(0, 54, 6).tolist(),
    save_dir='/courses/meteo473/sp26/473_sp26_group6/data/', overwrite=True)

# variable strings
ss1 = r":(2t):"
ss2 = r":(gh|t|u|v|sd|10fg|sp|ws|tp|ptype|tprate):"

filepath1 = H.download(ss1)
filepath2 = H.download(ss2)

# if some data does not exsist...
if not filepath1 or not filepath2:
    print("No data available for this run. Skipping...")
    exit()

# open and merge
ds1 = xr.open_mfdataset(filepath1, combine='nested', concat_dim='valid_time')
ds2 = xr.open_mfdataset(filepath2, combine='nested', concat_dim='valid_time',
                        coords='minimal', compat='override')

ds = xr.merge([ds1, ds2], compat='override', combine_attrs='override')

# clean dataset
ds = ds.sortby('valid_time')
ds = ds.sel(latitude=slice(60,20), longitude=slice(-130,-60))

# save latest dataset
ds.to_netcdf(DATA_FILE)

print("Downloaded and saved latest dataset")

# run exsisting script
os.system("/usr/local/anaconda3/envs/custom_envs/meteo473_sp26/bin/python /courses/meteo473/sp26/473_sp26_group6/winter_threat_index.py")