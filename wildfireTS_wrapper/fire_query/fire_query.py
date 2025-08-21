"""
This program will plot all the central points for the fires outlined in the WildfireTS dataset. You can query the fires by state and get the according csv file with the following fields:
    - Fire ID
    - Start Date
    - End Date
    - Lat
    - Lon

This csv will be pumped into the WildfireTS_wrapper for wrf weather simuations.

Can also be ran as a standalone module.
"""
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
US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

def plot_fire_locations(state_filter=None, output_path=None, show_plot=False, fire_filter=None):


    if state_filter:
        for index, state in enumerate(state_filter):

            # convert state abbreviation to full name
            if state in US_STATES.keys():
                state_filter[index] = US_STATES[state]

            elif state not in US_STATES.values():
                raise ValueError(f"{state} is not a valid US state.")

    else:
        state_filter = list(US_STATES.values())

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
        if isinstance(state_filter, str):
            state_filter = [state_filter]

        # Lowercase both the dataframe column and the filters
        state_filter = [s.lower() for s in state_filter]
        state_geom = states_gdf[states_gdf["name"].str.lower().isin([s.lower() for s in state_filter])]

        if state_geom.empty:
            raise ValueError(f"State '{state_filters}' not found.")

        # Combine all geometries into one (union of states)
        combined_geom = state_geom.union_all()


        # Filter points inside state polygon
        gdf = gdf[gdf.geometry.within(combined_geom)]
        if gdf.empty:
            print(f"No fires found in state: {state_filter}")
            return

        # Create a column for the state each fire belongs to
        def fire_state(fire_point):
            for _, row in state_geom.iterrows():
                if fire_point.within(row.geometry):
                    return row["name"]  # original state name
            return None

        gdf["state_name"] = gdf.geometry.apply(fire_state)

    # Handle fire ID filtering
    if fire_filter:
        if isinstance(fire_filter, str):
            fire_filter = [fire_filter]

        fire_filter = [f.upper() for f in fire_filter]
        gdf = gdf[gdf["fire_id"].str.upper().isin([fid for fid in fire_filter])]
        if gdf.empty:
            print(f"No fires found with fire IDs: {', '.join(fire_filter)}")
            return

        if gdf.empty:
            print(f"No fires found with fire IDs: {', '.join(fire_filter)}")
            return

    # Save filtered CSV
    if not output_path:
        output_path = f"filtered_fires.csv"
    gdf.drop(columns="geometry").to_csv(output_path, index=False)

    # Plot
    if show_plot:
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
    parser.add_argument("--states","-s",nargs="+" ,help="Filer by US state name (e.g. Washington)", default=None)
    parser.add_argument("--fire-ids","-f",nargs="+" ,help="Filer by Fire ID", default=None)
    parser.add_argument("--show-plot", help="Display the map of fire locations")
    args = parser.parse_args()

    fires = plot_fire_locations(state_filter=args.states, fire_filter=args.fire_ids)

