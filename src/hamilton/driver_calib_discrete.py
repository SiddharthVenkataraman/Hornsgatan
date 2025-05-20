from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters

from . import features_calib_discrete
from ..tools import mytools
import logging
myconfig = mytools.read_config()

def _base_config() -> Dict[str, str]:
    """Return base configuration parameters for the simulation."""
    return {
        "date": "2020-01-01",
        "detector": "w2e_in",
        "path": "data/calibration_intermediate_data/",
        "pathout": "data/calibration_data/",
        "pathin": "data/daily_splitted_data/",
        "iteration": 30,
        "init_number" : 20,
        "network_file": "data/map/Hornsgatan.net.xml",
        "base_estimator": "ET",   #{"GP", "RF", "ET", "GBRT"}
        "acq_func": "EI", #{"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
        "n_initial_points": 10,
    }
config = _base_config()

if config["init_number"]<1:
    postfix =  f"{config['detector']}_{config['date']}"
else:
    postfix = f"{config['detector']}_{config['date']}_{config['init_number']}"

mytools.setup_logging(postfix)
logger = logging.getLogger("calib")

"""
tracker = adapters.HamiltonTracker(
project_id=myconfig["project_id"],  # modify this as needed
username="kaveh",
dag_name=f"calibration_{config['date']}_{config['detector']}_{config['init_number']}",
tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
)
"""

# Option 1: Run the entire pipeline with the Hamilton driver
dr = (
    driver.Builder()
    .with_config(config)  # we don't have any configuration or invariant data for this example.
    .with_modules(features_calib_discrete)  # we need to tell hamilton where to load function definitions from
    .with_adapters(base.DictResult)  # we want a pandas dataframe as output
    .with_adapters(base)
    .build()
)
#dr.display_all_functions(
#"diagram/calibration.png"
#)    
result = dr.execute(["calibrated_data"])
