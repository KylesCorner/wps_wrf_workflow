"""
move_wrf.py
Author: Kyle Krstulich

this file will move wrfout files and organize them by fireid
"""
from constants import *
import os
import shutil

# === Private Functions ===

def __get_all_wrfout_files():
    """
    Recursively finds all 'wrfout*' files under each fire ID directory.

    Parameters
    ----------
    base_dir : str
        Path to the base directory containing fire ID subfolders.

    Returns
    -------
    list of str
        Full paths to all matching files.
    """
    base_dir = SCRATCH_DIR
    wrfout_files = []
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.startswith("wrfout"):
                wrfout_files.append(os.path.join(root, filename))
    return wrfout_files
def __extract_wrfout_metadata(wrfout_files):
    """
    Given a list of wrfout file paths, extract fire ID and date folder name.

    Parameters
    ----------
    wrfout_files : list of str
        Full paths to wrfout files.

    Returns
    -------
    list of tuple
        Each tuple is (file_path, fire_id, date_str)
        - fire_id : the name of the fire ID directory
        - date_str : the name of the date folder (YYYYMMDD_HH)
    """
    results = []
    for file_path in wrfout_files:
        parts = file_path.split(os.sep)
        try:
            # parts[-2] = date folder
            # parts[-3] = "wrf"
            # parts[-4] = fire ID
            filename = parts[-1]
            date_str = parts[-2]
            fire_id = parts[-4]
            results.append((file_path, fire_id, date_str, filename))
        except IndexError:
            # Skip files that don't match expected structure
            continue
    return results

def __move_wrf_files(metadata):

    for file_path, fireid, fdate, file_name in metadata:
        out_dir = SCRATCH_DIR / "wrfout" / fireid / fdate
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / file_name
        shutil.copy(file_path,out_file)

# === Public Functions ===

def get_wrfout_files(folder_path):
    """
    Returns a list of full paths to files starting with 'wrfout'
    in the given folder.

    Parameters
    ----------
    folder_path : str
        Path to the folder to search.

    Returns
    -------
    list of str
        List of full file paths matching 'wrfout*'
    """
    wrfout_files = []
    for filename in os.listdir(folder_path):
        if filename.startswith("wrfout") and os.path.isfile(os.path.join(folder_path, filename)):
            wrfout_files.append(os.path.join(folder_path, filename))
    return wrfout_files

def move_all_wrfout():
    wrf_files = __get_all_wrfout_files()
    metadata = __extract_wrfout_metadata(wrf_files)
    __move_wrf_files(metadata)


