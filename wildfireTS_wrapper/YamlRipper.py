"""
This program makes copies from one master yaml file and edits fields according to fire id.

All fires are split by fire id for ease of running in parallel
"""
import yaml
import os
from pathlib import Path
from constants import *

class YamlRipper:
    def __init__(self, fireid: int):
        self.fireid = str(fireid)
        self.master_yaml_path = WRF_YAML_DIR
        self.geogrid_yaml_path = GEOGRID_YAML_DIR
        self.output_dir = CONFIG_DIR
        self.wrf_output_path = self.output_dir / f"{self.fireid}_wrf.yaml"
        self.geogrid_output_path = self.output_dir / f"{self.fireid}_geogrid.yaml"
        self.wrf_config = {}
        self.geogrid_config = {}

    def __str__(self):
        output_str = "GEOGRID\n"
        for key, value in sorted(self.geogrid_config.items()):
            output_str += f"{key}: {value}\n"

        output_str += "WRF\n"

        for key, value in sorted(self.wrf_config.items()):
            output_str += f"{key}: {value}\n"
        return output_str

    def _load_master_config(self):
        if not self.master_yaml_path.exists():
            raise FileNotFoundError(f"Master YAML file not found: {self.master_yaml_path}")
        with open(self.master_yaml_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_geogrid_config(self):
        if not self.geogrid_yaml_path.exists():
            raise FileNotFoundError(f"Master YAML file not found: {self.master_yaml_path}")
        with open(self.geogrid_yaml_path, 'r') as f:
            return yaml.safe_load(f)

    def _edit_one_yaml(self, config: dict) -> dict:
        # edit download directory
        grib_dir = HRRR_DIR / self.fireid
        grib_dir.mkdir(parents=True, exist_ok=True)
        config['grib_dir'] = str(grib_dir)

        # edit tempalate directory
        template_dir = TEMPLATE_DIR / self.fireid
        template_dir.mkdir(parents=True, exist_ok=True)
        config['template_dir'] = str(template_dir)

        # edit wps run directory
        wps_run_dir = SCRATCH_DIR / self.fireid / 'wps'
        wps_run_dir.mkdir(parents=True, exist_ok=True)
        config['wps_run_dir'] = str(wps_run_dir)

        # edit wrf run directory
        wrf_run_dir = SCRATCH_DIR / self.fireid / 'wrf'
        wrf_run_dir.mkdir(parents=True, exist_ok=True)
        config['wrf_run_dir'] = str(wrf_run_dir)
        return config


    def edit_geogrid(self):
        self.geogrid_config = self._edit_one_yaml(self._load_geogrid_config())

    def save_geogrid(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.geogrid_output_path, 'w') as f:
            yaml.safe_dump(self.geogrid_config, f)


    def edit(self):
        self.wrf_config = self._edit_one_yaml(self._load_master_config())

    def save(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.wrf_output_path, 'w') as f:
            yaml.safe_dump(self.wrf_config, f)


    def remove(self):
        if os.path.exists(self.wrf_output_path):
            os.remove(self.wrf_output_path)

        if os.path.exists(self.geogrid_output_path):
            os.remove(self.geogrid_output_path)

if __name__ == "__main__":
    fireid = 12345678
    yr = YamlRipper(fireid)
    yr.edit()
    print(yr)
    yr.save()
    yr.remove()
