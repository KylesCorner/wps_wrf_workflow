"""
move_wrf.py
Author: Kyle Krstulich

this file will move wrfout files and organize them by fireid
"""
from constants import *
import os
import shutil
from datetime import datetime
import pandas as pd
from pathlib import Path

def comp_dates(date1, date2):
    return date1[:-3] == date2[:-3]

def extract_datetime_from_filename(filename):
    try:
        parts = filename.split('_')
        timestamp = '_'.join(parts[-2:])  # e.g., "2024-07-11_00:00:00"
        timestamp = pd.to_datetime(timestamp, format="%Y-%m-%d_%H:%M:%S")
        return parse_date(timestamp)
    except Exception:
        return None

def gather_files(startDate: str, wrf_dir: str):
    filenames = []

    if os.path.exists(wrf_dir):
        for fname in os.listdir(wrf_dir):
            if fname.startswith('wrfout'):
                comp_date = extract_datetime_from_filename(fname)
                if comp_dates(comp_date, startDate):
                    filenames.append(fname)

    return filenames

def move_files(startDate: str, fireId: str):
    #FIREID_OUT_DIR
    wrf_dir = WRF_OUT_DIR / startDate
    output_dir = FIREID_OUT_DIR / fireId
    if not os.path.exists(wrf_dir):
        raise FileNotFoundError(f"{wrf_dir} not found!")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)


    files = gather_files(startDate, wrf_dir)

    for f in files:
        src = wrf_dir / f
        dst = output_dir
        shutil.move(src,dst)
