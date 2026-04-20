DATA_FILE   = "/courses/meteo473/sp26/473_sp26_group6/ecmwf_update5.nc"
OUTPUT_DIR  = "/courses/meteo473/sp26/473_sp26_group6/website/images"

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

from herbie import Herbie, FastHerbie
import pandas as pd, numpy as np, xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap, BoundaryNorm

#open data set
ds_test = xr.open_dataset(DATA_FILE)

# defining time functions
def get_time_slice(ds, time_index):
    ds_t = ds.isel(valid_time=time_index)
    init_time = pd.to_datetime(ds.valid_time.values[0])
    valid_time = pd.to_datetime(ds.valid_time.values[time_index])
    init_str = init_time.strftime("%HZ %d %b %Y")
    valid_str = valid_time.strftime("%HZ %d %b %Y")
    return ds_t, init_str, valid_str

def get_time_strings(ds, time_index):
    init_time = pd.to_datetime(ds.valid_time.values[0])
    valid_time = pd.to_datetime(ds.valid_time.values[time_index])
    init_str = init_time.strftime("%HZ %d %b %Y")
    valid_str = valid_time.strftime("%HZ %d %b %Y")
    return init_str, valid_str

# calculating wind chill
def compute_wind_chill(ds, time_index):
    wind_gust = ds['fg10'].isel(valid_time=time_index).values
    t2m = ds['t2m'].isel(valid_time=time_index).values
    # convert temperature to F
    t2m_F = (t2m - 273.15) * 9/5 + 32
    # convert wind speed to mph
    V_mph = wind_gust * 2.237
    # wind chill formula
    wind_chill = (35.74 + 0.6215 * t2m_F - 35.75 * (V_mph ** 0.16) + 0.4275 * t2m_F * (V_mph ** 0.16))
    # apply validity mask
    wind_chill = np.where((t2m_F <= 50) & (V_mph >= 3), wind_chill, t2m_F)
    return wind_chill

# wind chill index contribution
def wind_chill_contribution(wind_chill):
    WC_contribution = np.clip(
        1.0
        - 0.1 * np.clip((wind_chill + 20) / 10, 0, 1)   # -20 → -10
        - 0.1 * np.clip((wind_chill + 10) / 10, 0, 1)   # -10 → 0
        - 0.3 * np.clip((wind_chill - 0) / 20, 0, 1)    # 0 → 20
        - 0.5 * np.clip((wind_chill - 20) / 20, 0, 1),  # 20 → 40
        0, 1
    )
    return WC_contribution * 10

# precip rate contribution
tprate = ds_test['tprate'].values
tprate_in = tprate*141.73

def precip_rate_contribution(tprate_in):
    contribution = np.clip(
        0.0
        + 0.2 * np.clip((tprate_in - 0.1) / 0.2, 0, 1)
        + 0.4 * np.clip((tprate_in - 0.3) / 0.3, 0, 1)
        + 0.2 * np.clip((tprate_in - 0.5) / 0.2, 0, 1)
        + 0.2 * np.clip((tprate_in - 0.8) / 0.2, 0, 1),
        0, 1
    )
    return contribution * 10

# precip type contribution
def precip_type_contribution(ptype):
    ptype_scale = {
        0: 0,  # None
        1: 1,  # Rain
        7: 2,  # Rain/snow mix
        8: 3,  # Ice pellets
        5: 4,  # Snow
        12: 5, # Freezing drizzle
        6: 6,  # Wet snow
        3: 7   # Freezing rain
    }
    # Convert ptype to ranked severity
    ptype_rank = np.vectorize(ptype_scale.get)(ptype)
    contribution = np.clip(
        0.0
        + 0.25 * np.clip((ptype_rank - 1) / 2, 0, 1)   # Rain → Mix
        + 0.25 * np.clip((ptype_rank - 3) / 2, 0, 1)   # Ice → Snow
        + 0.25 * np.clip((ptype_rank - 5) / 1, 0, 1)   # fzdz → Wet snow
        + 0.25 * np.clip((ptype_rank - 6) / 1, 0, 1),  # Wet snow → fzra
        0, 1
    )
    return contribution * 10

# wind gust
wgust = ds_test['fg10'] * 1.94384449

# initialize
wind_hazard = xr.zeros_like(wgust)

# middle range: 10–35 kt
mask_mid = (wgust >= 10) & (wgust <= 35)
wind_hazard = wind_hazard.where(
    ~mask_mid,
    10 * ((wgust - 10) / 25.0) ** 2
)

# above 35 kt → cap at 10
wind_hazard = wind_hazard.where(wgust <= 35, 10)

# wind gust contribution
def wind_gust_contribution(ds, time_index):
    # convert m/s to knots
    wgust = ds['fg10'].isel(valid_time=time_index) * 1.94384449
    # initialize
    wind_hazard = xr.zeros_like(wgust)
    # middle range: 10–35 kt
    mask_mid = (wgust >= 10) & (wgust <= 35)
    wind_hazard = wind_hazard.where(
        ~mask_mid,
        10 * ((wgust - 10) / 25.0) ** 2
    )
    # above 35 kt → cap at 10
    wind_hazard = wind_hazard.where(wgust <= 35, 10)
    return wind_hazard

# 2m temp contribution
t2m = ds_test['t2m'].values
t2m_F = (t2m - 273.15) * 9/5 + 32
temp_index = 10 * ((40 - t2m_F) / 30)

# Apply bounds
temp_index = temp_index.clip(min=0, max=10)

def temp_contribution(t2m_F):
    temp_index = 10 * ((40 - t2m_F) / 30)
    # Apply bounds
    temp_index = np.clip(temp_index, 0, 10)
    return temp_index

# individual threat weighting
def compute_threat_index(ptype_idx, prate_idx, gust_idx, wc_idx, temp_idx):
    threat_index = (
        0.275 * ptype_idx +
        0.1 * prate_idx +
        0.2 * gust_idx +
        0.275 * wc_idx +
        0.15  * temp_idx
    )
    return threat_index

# overall index with each individual variable inside
def compute_threat_index_full(ds, time_index):
    # wind chill
    wind_chill = compute_wind_chill(ds, time_index)
    wc_index = wind_chill_contribution(wind_chill)
    # precip rate
    tprate = ds['tprate'].isel(valid_time=time_index).values * 141.732
    prate_index = precip_rate_contribution(tprate)
    # precip type
    ptype = ds['ptype'].isel(valid_time=time_index).values
    ptype_index = precip_type_contribution(ptype)
    # wind gust
    gust_index = wind_gust_contribution(ds, time_index)
    # temperature
    t2m = ds['t2m'].isel(valid_time=time_index).values
    t2m_F = (t2m - 273.15) * 9/5 + 32
    temp_index = temp_contribution(t2m_F)
    # final index
    return compute_threat_index(
        ptype_index,
        prate_index,
        gust_index,
        wc_index,
        temp_index
    )

# plotting prelims
lat = ds_test.latitude.values
lon = ds_test.longitude.values
dataproj = ccrs.PlateCarree()

# basemap
def GeoAxes():
    fig = plt.figure(figsize=(15,9))
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-120,-70,25,50], ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'))
    return fig, ax  

# looping to save figures at each time step
n_times = len(ds_test.valid_time)

for t in range(n_times):
    # compute hazard index for this timestep
    hazard_index = compute_threat_index_full(ds_test, t)
    # time strings
    init_str, valid_str = get_time_strings(ds_test, t)    
    # figure
    fig, ax = GeoAxes() 
    mesh = ax.pcolormesh(
        lon, lat, hazard_index, vmin=0, vmax=10, cmap="rainbow", transform=ccrs.PlateCarree())
    plt.colorbar(mesh, ax=ax, shrink=0.8, label="Hazard Index (0–10)")
    ax.set_title(f"ECMWF Winter Weather Threat Hazard Impact on Energy Demand\n"f"Init: {init_str}  Valid: {valid_str}")    
    # format filename using forecast hour
    lead_hours = t * 6      
    # checking if actually saving
    print(f"Saving: winter_threat_{lead_hours:03d}.png")
    filename = f"winter_threat_{lead_hours:03d}.png"
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close(fig)












