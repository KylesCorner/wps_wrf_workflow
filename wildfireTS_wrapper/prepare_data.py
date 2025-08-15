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
import threading
from datetime import datetime
from pathlib import Path
from constants import *
from NmlRipper import NmlRipper
from YamlRipper import YamlRipper
from typing import List
from fire_query.fire_query import plot_fire_locations
from collections import deque
from move_wrf import get_wrfout_files



rippers = []
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

# === Helper Functions ===
def get_wrf_dir(fireid: str, fdate: str):
    return SCRATCH_DIR / fireid / "wrf" / fdate

def get_wps_dir(fireid: str, fdate: str):
    return SCRATCH_DIR / fireid / "wps" / fdate

# === Error Handling ===

def open_log_file(logfile: Path):
    with open(logfile, "r", encoding="utf-8", errors="ignore") as f:
        last_lines = list(deque(f, maxlen=10))  # Only keep last 10 lines
    return last_lines

def display_error(e: str, logfile: Path, fireid=None, fdate=None):
    time.sleep(1) # wait for log file
    log_result = open_log_file(logfile)
    if any("download_hrrr_from_aws_or_gc.py" in line for line in log_result):
        print(f"[ERROR][{fireid}: {fdate}] HRRR data not found.")
    elif any("run_wrf.py" in line for line in log_result) and len(get_wrfout_files(get_wrf_dir(fireid,fdate))) >= 30:
        print(f"[{fireid}: {fdate}]WRF has finished, but did not exit gracefully.")
    else:
        print(f"[ERROR] {fireid} failed at date {fdate}: {str(e)}")
        print(f"Consult {logfile} for more details.")
        print("---------------- LOG FILE SNIPPET --------------------")
        print(log_result)
        print("------------------------------------------------------")


# === WPS/WRF Running functions ===

def run_command(cmd_args):
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd_args)}\n{e}")

def worker(command_list, geogrid_command, semaphore):
    with semaphore:
        fireid = geogrid_command[4]
        try:
            subprocess.run(geogrid_command, check=True)
        except subprocess.CalledProcessError as e1:
            logfile = HOME_DIR / 'logs' / firei / f"{geogrid_command[2].log}"
            display_error(e, logfile, fireid=fireid, fdate=geogrid_command[2])
            return

        for cmd in command_list:
            fdate = cmd[2]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e2:
                logfile = HOME_DIR / 'logs' / fireid / f"{fdate}.log"
                display_error(e2, logfile, fireid=fireid, fdate=fdate)

def run_fires_async(fire_command_dict, geogrid_command_dict, semaphore):
    threads = []
    for fireId, cmd in fire_command_dict.items():
        geogrid_command = geogrid_command_dict[fireId]
        t = threading.Thread(target=worker, args=(cmd,geogrid_command, semaphore))
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

def parse():
    parser = argparse.ArgumentParser(
        description = "Run WPS/WRF for fires in a selected US state."
    )
    parser.add_argument("--states","-s",nargs="+" ,help="Filer by US state name (e.g. Washington)", default=["WA"])
    parser.add_argument("--max-fires", "-m", help="Max fires processed",type=int, default=MAX_FIRES)
    parser.add_argument("--num-days", "-n", help="Number of days to process per fire",type=int, default=MAX_DAYS)
    parser.add_argument("--threads", "-t", help="Number working threads",type=int, default=MAX_WORKERS)
    parser.add_argument("--dry-run", "-d", help="Do a dry run. No WPS/WRF",action="store_true")
    args = parser.parse_args()
    return args
    

def main():

    args = parse()

    if args.dry_run:
        running_script = TEST_SCRIPT
    else:
        running_script = WRF_SCRIPT

    state_csvs = [(state ,load_csv(state)) for state in args.states]

    semaphore = threading.Semaphore(args.threads)
    process_map = {}
    geogrid_map = {}

    try:
        # run watchdog scripts
        attach_monitor()

        for state_name, state_csv in state_csvs:
            # rip each fire in the pickle
            for index, fire in state_csv.iterrows():

                # limit number of fires processed
                if(index > args.max_fires - 1):
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
                geogrid_process = ["bash", str(running_script),fire_dates[0], str(geogrid_path), str(fireId)]
                geogrid_map[fireId] = geogrid_process

                # Create a process map for ease of running by fire Id
                for num_day, fdate in enumerate(fire_dates):
                    if(num_day > args.num_days - 1):
                        break

                    # change namelist
                    nr.edit(fdate)
                    nr.save()
                    template_dir = nr.output_dir

                    # generate yaml
                    yr.edit()
                    yr.save()
                    yaml_path = yr.wrf_output_path

                    print(f"Pre-processing {state_name} fire: {fireId} at {fdate}")
                    process = ["bash",str(running_script),fdate,str(yaml_path), str(fireId)]
                    process_map[fireId].append(process)



        run_fires_async(process_map, geogrid_map, semaphore)

    finally:

        # TODO: Move wrfout files
        detach_monitor()
        move_wrf()
        print("Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ABORTED] Keyboard interrupt received. Terminating...")
        #remove_old_files()
        detach_monitor()
        #subprocess.run(['bash', str(STOP_SCRIPT)], check=True)

