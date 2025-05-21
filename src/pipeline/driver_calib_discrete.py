from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters
import yaml

from src.pipeline import features_calib_discrete
from src.tools import mytools
import logging
myconfig = mytools.read_config()

def _base_config() -> Dict[str, str]:
    """Return base configuration parameters for the simulation."""
    return {
        "date": "2020-01-02",
        "detector": "e2w_in",
        "path": "data/calibration_intermediate_data/",
        "pathout": "data/calibration_data/",
        "pathin": "data/daily_splitted_data/",
        "iteration":50,
        "init_number" : 0,
        "network_file": "data/map/Hornsgatan.net.xml",
        "base_estimator": "GP",   # {"GP", "RF", "ET", "GBRT"}
        "acq_func": "LCB", # {"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
        "n_initial_points": 5,
    }

def main(tracker: bool = False):
    import argparse
    parser = argparse.ArgumentParser(description="Calibration Discrete Pipeline")
    parser.add_argument('--tracker', action='store_true', help='Enable HamiltonTracker adapter')
    parser.add_argument('--config', type=str, help='Path to YAML config file')
    parser.add_argument('--log-level', type=str, default='INFO', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args, _ = parser.parse_known_args()
    tracker = args.tracker
    log_level = args.log_level

    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = _base_config()

    if config["init_number"]<1:
        postfix =  f"{config['detector']}_{config['date']}"
    else:
        postfix = f"{config['detector']}_{config['date']}_{config['init_number']}"

    mytools.setup_logging(postfix, log_level=log_level)
    logger = logging.getLogger("calib")

    builder = (
        driver.Builder()
        .with_config(config)
        .with_modules(features_calib_discrete)
        .with_adapters(base.DictResult)
        .with_adapters(base)
    )

    if tracker:
        tracker_adapter = adapters.HamiltonTracker(
            project_id=myconfig.get("project_id", "default_project"),
            username="kaveh",
            dag_name=f"calibration_{config['date']}_{config['detector']}_{config['init_number']}",
            tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
        )
        builder = builder.with_adapters(tracker_adapter)

    dr = builder.build()
    result = dr.execute(["calibrated_data"])

if __name__ == "__main__":
    main()
