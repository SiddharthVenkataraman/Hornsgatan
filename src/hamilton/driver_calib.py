from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters

from . import features_calib
from ..tools import mytools
myconfig = mytools.read_config()

def _base_config() -> Dict[str, str]:
        """Return base configuration parameters for the simulation."""
        return {
            "date": "2020-01-01",
            "detector": "w2e_in",
            "path": "data/calibration_intermediate_data/",
            "pathout": "data/calibration_data/",
            "pathin": "data/daily_splitted_data/",
            "iteration": 20,
            "init_number" : 100,
            "network_file": "data/map/Hornsgatan.net.xml",
            "hornsgatan_home": "/home/kaveh/Hornsgatan/"
        }
config = _base_config()

tracker = adapters.HamiltonTracker(
project_id=myconfig["project_id"],  # modify this as needed
username="kaveh",
dag_name=f"calibration_{config['date']}_{config['detector']}_{config['init_number']}",
tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
)

# Option 1: Run the entire pipeline with the Hamilton driver
dr = (
    driver.Builder()
    .with_config(config)  # we don't have any configuration or invariant data for this example.
    .with_modules(features_calib)  # we need to tell hamilton where to load function definitions from
    .with_adapters(base.DictResult)  # we want a pandas dataframe as output
    .with_adapters(tracker)
    .build()
)
#dr.display_all_functions(
#"diagram/calibration.png"
#)    
result = dr.execute(["calibrated_data"])
