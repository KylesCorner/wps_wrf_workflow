"""
move_wrf.py
Author: Kyle Krstulich

this file will move wrfout files and organize them by fireid
"""
from constants import *
import os
import shutil

def comp_dates(date1, date2):
    return date1[:-3] == date2[:-3]


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


if __name__ == "__main__":
    test_dir = SCRATCH_DIR / "20777571" / "wrf" / "20170708_00"
    wrf_files = get_wrfout_files(test_dir)
    print(wrf_files)
    print(len(wrf_files))
