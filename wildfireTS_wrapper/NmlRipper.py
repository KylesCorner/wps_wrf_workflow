"""
This program handles all the fortran namelist stuff for WPS/WRF. It also handles the creation of job submission scripts for each step of WPS/WRF.

Each script and namelist is split into directories by fire id for ease of running in parallel.
"""
import f90nml
import pandas as pd
import os
import shutil
from constants import *

class NmlRipper:
    def __init__(self, ps : pd.Series):
        self.ps = ps
        self.startDate = pd.to_datetime(self.ps['start_date'])
        self.endDate = pd.to_datetime(self.ps['end_date'])
        self.hrStartDate = parse_date(self.startDate)
        self.hrEndDate = parse_date(self.endDate)
        self.dateRange =  [parse_date(tm) for tm in list(pd.date_range(start=self.startDate, end=self.endDate, freq='D'))]
        self.lat = self.ps['lat'] 
        self.lon = self.ps['lon']
        self.fireId = self.ps['fire_id']
        self.master_namelist_path= MASTER_TEMPLATE_DIR / 'namelist.wps.hrrr'
        self.namelist = self._load_master_namelist()
        self.output_dir = TEMPLATE_DIR / str(self.fireId)
        self.wps_dir = SCRATCH_DIR / str(self.fireId) / 'wps'
        self.wrf_dir = SCRATCH_DIR / str(self.fireId) / 'wrf'

    def __str__(self):
        output_str = ''
        for section , info in self.namelist.items():
            output_str += f"[{section}]\n"
            for key, value in info.items():
                output_str += f"\t{key} : {value}\n"

        return output_str



    def _load_master_namelist(self):
        return f90nml.read(self.master_namelist_path)

    def edit(self, date:str):
        # generate paths for geogrid
        geogrid_output = self.wps_dir /'geogrid'

        # generate paths for ungrib
        ungrib_prefix = self.wps_dir / date / 'ungrib' / 'HRRR'
        ungrib_prefix.mkdir(parents=True, exist_ok=True)

        # generate paths for metgrid

        metgrid_fg_names = [str(ungrib_prefix)]
        metgrid_output_dir = self.wps_dir / date / 'metgrid'
        metgrid_output_dir.parent.mkdir(parents=True, exist_ok=True)

        # apply to namelist
        self.namelist['share']['opt_output_from_geogrid_path'] = str(geogrid_output)

        self.namelist['geogrid']['ref_lat'] = self.namelist['geogrid']['truelat1'] = self.namelist['geogrid']['truelat2'] = self.lat
        self.namelist['geogrid']['ref_lon'] = self.namelist['geogrid']['stand_lon'] = self.lon

        self.namelist['ungrib']['prefix'] = str(ungrib_prefix)

        self.namelist['metgrid']['fg_name'] = metgrid_fg_names
        self.namelist['metgrid']['opt_output_from_metgrid_path'] = str(metgrid_output_dir)

    def save(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        namelist_file = self.output_dir / 'namelist.wps.hrrr'

        if os.path.exists(namelist_file):
            os.remove(namelist_file)
        self.namelist.write(str(self.output_dir / 'namelist.wps.hrrr'))

        # copy over namelists.input.*
        shutil.copy((MASTER_TEMPLATE_DIR / 'namelist.input.hrrr'), (self.output_dir / 'namelist.input.hrrr.hybr'))
        shutil.copy((MASTER_TEMPLATE_DIR / 'namelist.input.hrrr'), (self.output_dir / 'namelist.input.hrrr.pres'))

        pbs_replacements = {
            "#PBS -q main@desched1": "#PBS -q main",
            "#PBS -q casper": "#PBS -q casper-pbs"
        }

        # copy over job submission scripts
        for master_script in MASTER_TEMPLATE_DIR.glob("submit_*"):

            derecho_path = self.output_dir / f"{master_script.name}.derecho"
            casper_path = self.output_dir / f"{master_script.name}.casper"
            shutil.copy(master_script, casper_path)

            with master_script.open("r") as f:
                lines = f.readlines()

            modified = []
            for line in lines:
                stripped = line.strip()
                if stripped in pbs_replacements:
                    modified.append(pbs_replacements[stripped] + "\n")
                else:
                    modified.append(line)

            with derecho_path.open("w") as f:
                f.writelines(modified)




    def remove(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

if __name__ == "__main__":
    nr = NrmRipper()

    
