# Install and Configuration
Python-based modular workflow for configuring and running WPS and WRF, and optionally also post-processing programs like UPP. Because of its modular nature, scripts to do additional steps can easily be added if desired.

Before running this Python-based workflow, you need to do the following steps:
 - Have compiled versions of WRF and WPS available (for now, WPS should be compiled with dmpar; later updates may make this workflow compatible with serial-compiled WPS)
 - Have a configured python conda environment. Theres a yaml file located at the root of the project 

```
 conda env update -f environment.yml
```

----

# WildfireTS++ WPS/WRF Processor
A command-line tool for fetching, filtering, and processing wildfire data with flexible options for dataset size, date range, threading, and state-based filtering.

Features
- Max Fires — limit the number of wildfire records processed.

- Date Range — process fires over a specified number of days.

- Multithreading — speed up processing with multiple worker threads.

- State Filter — filter fires to only those within specified U.S. states.

| Argument      | Type      | Description                                                             | Example             |
| ------------- | --------- | ----------------------------------------------------------------------- | ------------------- |
| `--max-fires, -m` | int       | Maximum number of fires to process.                                     | `--max-fires 500`   |
| `--num-days, -n`      | int       | Number of past days to include in the dataset.                          | `--days 30`         |
| `--threads, -t`   | int       | Number of worker threads for processing.                                | `--threads 8`       |
| `--states, -s`    | str, list | Space-separated list of U.S. state names or abbreviations to filter by. | `--states CA WA OR` |
| `--fireids, -f`    | str, list | Space-separated list of fire ids. | `--fireids MT1235 1234098` |
| `--dry-run, -d`    | boolean | Preform a run that does not execute wps/wrf only sets up files. | `-dry-run` |

## Example
```
python3 wildfireTS_wrapper/prepare_data.py -s WA,OR,MT -m 10 -n 31 -t 5
```
