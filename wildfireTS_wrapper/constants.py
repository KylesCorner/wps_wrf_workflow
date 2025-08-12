"""
constants.py

This file holds all the constants needed for the WRF pipeline.
"""
from pathlib import Path

HOME_DIR = Path("/glade/u/home/krstulich/wps_wrf_workflow/")
SCRATCH_DIR = Path("/glade/derecho/scratch/krstulich/workflow/")
HRRR_DIR = Path("/glade/derecho/scratch/krstulich/data/")
WRAPPER_DIR = HOME_DIR / 'wildfireTS_wrapper'

CSV_DIR = WRAPPER_DIR /  'filtered_fires.csv'
MASTER_TEMPLATE_DIR = HOME_DIR / 'templates' / 'master'
WRF_YAML_DIR = MASTER_TEMPLATE_DIR /  'wrfonly.yaml'
GEOGRID_YAML_DIR = MASTER_TEMPLATE_DIR /  'geogridonly.yaml'
TEMPLATE_DIR = HOME_DIR / 'templates'
CONFIG_DIR = HOME_DIR / 'config'

WRF_SCRIPT = WRAPPER_DIR /  'run.sh'
TEST_SCRIPT = HOME_DIR/ 'wildfireTS_wrapper'/ 'test.sh'
MOVE_SCRIPT = WRAPPER_DIR /  'move_wrf.sh' # TODO: Fix this script
WATCHDOG_SCRIPT = WRAPPER_DIR /  'monitor.py'
STOP_SCRIPT = WRAPPER_DIR /  'stop_jobs.sh'
FIRE_QUERY_SCRIPT = WRAPPER_DIR / 'fire_query' / 'fire_query.py'

MAX_WORKERS = 3
MAX_FIRES = 6
MAX_DAYS = 31

def parse_date(pd_timestamp):

    year = pd_timestamp.year
    month = pd_timestamp.month
    day = pd_timestamp.day
    hour = pd_timestamp.hour

    if month < 10:
        month = f"0{month}"

    if day < 10:
        day = f"0{day}"

    if hour < 10:
        hour = f"0{hour}"

    return f"{year}{month}{day}_{hour}"
