from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters
from hamilton import dataflows, driver
import yaml
import logging

from src.pipeline import features_sim
from src.tools import mytools

localconfig = mytools.read_local_config()


def main(tracker: bool = False):
    import argparse
    parser = argparse.ArgumentParser(description="Simulation Pipeline")
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
        config = {
            "date": "2020-01-01",
            "detector": "w2e_out",
            "path": "data/sim_intermediate_data/",
            "pathout": "data/sim_data/",
            "pathin": "data/calibration_data/",
            "network_file": "data/map/Hornsgatan.net.xml",
            "hornsgatan_home": "/home/kaveh/Hornsgatan/"
        }

    postfix = f"sim_{config.get("detector")}"
    mytools.setup_logging(postfix, log_level=log_level)
    logger = logging.getLogger("sim")
    logger.info("-------------------------------------------------------")
    logger.info(f"date: {config["date"]}, detector: {config["detector"]}, init_number: {config["init_number"]}")
    logger.info("-------------------------------------------------------")

    builder = (
        driver.Builder()
        .with_config(config)
        .with_modules(features_sim)
        .with_adapters(base.DictResult)
        .with_adapters(base)
    )
    if tracker:
        tracker_adapter = adapters.HamiltonTracker(
            project_id=localconfig.get("project_id", "default_project"),
            username="kaveh",
            dag_name=f"simulation_{config['date']}_{config['detector']}"
                if "date" in config and "detector" in config else "simulation",
            tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
        )
        builder = builder.with_adapters(tracker_adapter)
    dr = builder.build()
    dr.display_all_functions(
        "diagram/diag_simulation.png"
    )  
    result = dr.execute(["run_sumo"])
    print("Done!!!")
    print(result)

if __name__ == "__main__":
    main()
