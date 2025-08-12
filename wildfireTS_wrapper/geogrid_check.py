
# check_geogrid_text.py
import xarray as xr
import numpy as np
import sys
import os
from pathlib import Path

GEOGRID_FILE = Path("/glade/derecho/scratch/krstulich/workflow/19276074/wps/geogrid/geo_em.d01.nc")
def print_stats(name, data):
    print(f"\n📊 Variable: {name}")
    print(f"  Shape      : {data.shape}")
    print(f"  Min        : {float(np.nanmin(data)):.2f}")
    print(f"  Max        : {float(np.nanmax(data)):.2f}")
    print(f"  Mean       : {float(np.nanmean(data)):.2f}")
    print(f"  Std Dev    : {float(np.nanstd(data)):.2f}")
    zero_pct = np.sum(data == 0) / data.size * 100
    print(f"  % Zeros    : {zero_pct:.2f}%")
    print("  All NaNs   :", np.all(np.isnan(data)))
    print("  Any NaNs   :", np.any(np.isnan(data)))

def ascii_preview(data, varname, width=60, height=20):
    print(f"\n🖼️ ASCII Preview: {varname}")
    downsample = data[::data.shape[0]//height or 1, ::data.shape[1]//width or 1]
    min_val = np.nanmin(downsample)
    max_val = np.nanmax(downsample)
    scale = " .:-=+*#%@"
    levels = len(scale) - 1
    for row in downsample:
        line = ""
        for val in row:
            if np.isnan(val):
                line += " "
            else:
                idx = int((val - min_val) / (max_val - min_val + 1e-10) * levels)
                line += scale[idx]
        print(line)

def main(filename=GEOGRID_FILE):
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found.")
        sys.exit(1)

    ds = xr.open_dataset(filename)
    print(f"✅ Opened: {filename}")
    print(f"🧭 Dimensions: {dict(ds.dims)}")

    vars_to_check = ["HGT_M", "LU_INDEX", "LANDMASK", "SOILHGT"]
    for var in vars_to_check:
        if var not in ds:
            print(f"\n⚠️ Variable missing: {var}")
            continue

        data = ds[var][0].values
        print_stats(var, data)
        ascii_preview(data, var)

if __name__ == "__main__":
    main()

