from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters
from hamilton import dataflows, driver

from . import features_sim
from ..tools import mytools
myconfig = mytools.read_config()


def _base_config() -> Dict[str, str]:
        """Return base configuration parameters for the simulation."""
        return {
            "date": "2020-01-01",
            "detector": "e2w_in",
            "path": "data/sim_intermediate_data/",
            "pathout": "data/sim_data/",
            "pathin": "data/calibration_data/",
            "init_number" : 0,
            "number": 0,
            "network_file": "data/map/Hornsgatan.net.xml",
            "hornsgatan_home": "/home/kaveh/Hornsgatan/"
        }
config = _base_config()

tracker = adapters.HamiltonTracker(
project_id= myconfig["project_id"],  # modify this as needed
username="kaveh",
dag_name=f"simulation_{config['date']}_{config['detector']}_{config['init_number']}",
tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
)


dr = (
    driver.Builder()
    .with_config(config)  # we don't have any configuration or invariant data for this example.
    .with_modules(features_sim)  # we need to tell hamilton where to load function definitions from
    .with_adapters(base.DictResult)  # we want a pandas dataframe as output
    .with_adapters(tracker)
    .build()
)

dr.display_all_functions(
"diagram/diag_simulation.png"
)  
  
result = dr.execute(["run_sumo"])
print("Done!!!")
print(result)
