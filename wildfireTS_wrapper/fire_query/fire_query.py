import argparse
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from cartopy.io import shapereader
from shapely.geometry import Point
from pathlib import Path


ALL_FIRES_CSV = Path("/glade/u/home/krstulich/wps_wrf_workflow/wildfireTS_wrapper/fire_query/all_fires.csv")

def plot_fire_locations(state_filter=None, output_path=None):
    # Load fire points
    csv_path = ALL_FIRES_CSV
    df = pd.read_csv(csv_path)
    required_cols = {"fire_id", "lat", "lon"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326"
    )

    # Load US state polygons
    shpfilename = shapereader.natural_earth(
        resolution="110m", category="cultural", name="admin_1_states_provinces"
    )
    states_gdf = gpd.read_file(shpfilename)
    states_gdf = states_gdf[states_gdf["admin"] == "United States of America"]

    if state_filter:
        state_geom = states_gdf[states_gdf["name"].str.lower() == state_filter.lower()]
        if state_geom.empty:
            raise ValueError(f"State '{state_filter}' not found.")
        # Filter points inside state polygon
        gdf = gdf[gdf.geometry.within(state_geom.iloc[0].geometry)]
        if gdf.empty:
            print(f"No fires found in state: {state_filter}")
            return

        # Save filtered CSV
        if not output_path:
            output_path = f"filtered_fires.csv"
        gdf.drop(columns="geometry").to_csv(output_path, index=False)

    # Plot
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-125, -65, 24, 50], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.STATES.with_scale("50m"), edgecolor="gray")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    for _, row in gdf.iterrows():
        lat, lon = row["lat"], row["lon"]
        fire_id = str(row["fire_id"])
        ax.plot(
            lon,
            lat,
            marker="o",
            color="red",
            markersize=5,
            transform=ccrs.PlateCarree(),
        )
        ax.text(lon + 0.2, lat + 0.2, fire_id, fontsize=8, transform=ccrs.PlateCarree())

    title = "Fire Locations"
    if state_filter:
        title += f" in {state_filter.title()}"
    plt.title(title)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot fire locations and export filtered CSV."
    )
    parser.add_argument("--state", help="Filter by U.S. state name (e.g. Washington)")
    args = parser.parse_args()

    plot_fire_locations(args.state)

