"""
 prepare_data.py
 Author: Kyle Krstulich
 July, 11, 2025

 This script is the entrance point for the WRF section of WildfireTS++. 
 Parameters:

    FireID: string
        - Unique human readable identifier for each fire.
    
    StartDate: datetime
        - The start date for query 

    EndDate: datetime
        - The end date for query

    Lat: float
        - Latitude for centroid.

    Lon: float
        - Longitude for centroid.

TODO: 
    - keep track of dates/locations that have been processed in a csv. To try and stop duplicate entries.

    - i want a running function for the subprocess.run I want to catch errors and check if wrf has completed correctly. WRF never exits gracefully

    - Try and do some terrain smoothing

STABILTY:
    - reduce time step from 6 to 4
    - reduce spacial resolution to 2 km

    
"""
import argparse
import f90nml
import yaml
import pandas as pd
import os
import subprocess
import time
import shutil
import asyncio
import signal
import threading
from datetime import datetime
from pathlib import Path
from constants import *
from move_wrf import move_files
from NmlRipper import NmlRipper
from YamlRipper import YamlRipper
from typing import List
from fire_query.fire_query import plot_fire_locations



RUNNING_SCRIPT = WRF_SCRIPT
rippers = []
semaphore = threading.Semaphore(MAX_WORKERS)
watchdogs = {
        'casper':None,
        'derecho':None,
        }


# === Setup Functions ===

def track_ripper(nr, yr):
    global rippers
    rippers.append((nr,yr))

def remove_old_files():
    global rippers
    for nr, yr in rippers:
        nr.remove()
        yr.remove()

def load_csv(state):
    plot_fire_locations(state_filter=state, output_path=CSV_DIR)
    if not os.path.exists(CSV_DIR):
        print("CSV file not found!")
        return
    return pd.read_csv(CSV_DIR)

# === WPS/WRF Running functions ===

def run_command(cmd_args):
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd_args)}\n{e}")

def worker(command_list, geogrid_command):
    with semaphore:
        try:
            subprocess.run(geogrid_command, check=True)
        except subprocess.CalledProcessError as e1:
            print(f"[ERROR] Geogrid failed: {str(e1)}")
            return

        for cmd in command_list:
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e2:
                print(f"[ERROR] Command failed: {str(e2)}")

def run_fires_async(fire_command_dict, geogrid_command_dict):
    threads = []
    for fireId, cmd in fire_command_dict.items():
        geogrid_command = geogrid_command_dict[fireId]
        t = threading.Thread(target=worker, args=(cmd,geogrid_command))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def run_fires_sync(fire_command_dict, geogrid_command_dict):

    for fireId, cmds in fire_command_dict.items():
        # run geogrid
        geogrid_cmd = geogrid_command_dict[fireId]
        print("Running geogrid")
        subprocess.run(geogrid_cmd, check=True)

        print("Finished geogrid")
        for cmd in cmds:
            # run rest of wps/wrf pipeline
            print("Running wps/wrf")
            subprocess.run(cmd, check=True)
            print("Finished wps/wrf\n")


# === Monitor Functions ===

def attach_monitor():
    pass

def detach_monitor():
    pass


def move_wrf():
    pass

def main():
    parser = argparse.ArgumentParser(
        description = "Run WPS/WRF for fires in a selected US state."
    )
    parser.add_argument("--state","-s", help="Filer by US state name (e.g. Washington)")
    args = parser.parse_args()

    pkl = load_csv(args.state)
    
    process_map = {}
    geogrid_map = {}

    try:
        # run watchdog scripts
        attach_monitor()

        # rip each fire in the pickle
        for index, fire in pkl.iterrows():

            # limit number of fires processed
            if(index > MAX_FIRES - 1):
                break 

            # setup run variables
            nr = NmlRipper(fire)
            fireId = nr.fireId
            yr = YamlRipper(fireId)
            fire_dates = nr.dateRange
            process_map[fireId] = []
            geogrid_map[fireId] = []
            track_ripper(nr,yr)

            # setup and run the geogrid process once per fire id
            yr.edit_geogrid()
            yr.save_geogrid()
            geogrid_path = yr.geogrid_output_path
            geogrid_process = ["bash", str(RUNNING_SCRIPT),fire_dates[0], str(geogrid_path), str(fireId)]
            geogrid_map[fireId] = geogrid_process

            # Create a process map for ease of running by fire Id
            for num_day, fdate in enumerate(fire_dates):

                # change namelist
                nr.edit(fdate)
                nr.save()
                template_dir = nr.output_dir

                # generate yaml
                yr.edit()
                yr.save()
                yaml_path = yr.wrf_output_path

                print(f"Pre-processing fire: {fireId} at {fdate}")
                process = ["bash",str(RUNNING_SCRIPT),fdate,str(yaml_path), str(fireId)]
                process_map[fireId].append(process)

                if(num_day > MAX_DAYS):
                    break


        run_fires_async(process_map, geogrid_map)

    finally:

        # TODO: Move wrfout files
        detach_monitor()
        move_wrf()
        print("Done!")

def test():
    start = pd.Timestamp("2018-07-01 00:00:00")
    end = pd.Timestamp("2018-07-14 00:00:00")
    lat= 40.147918
    lon= -110.832934
    fireid = 21890115
    pkl = load_pickle()



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ABORTED] Keyboard interrupt received. Terminating...")
        #remove_old_files()
        detach_monitor()
        #subprocess.run(['bash', str(STOP_SCRIPT)], check=True)

