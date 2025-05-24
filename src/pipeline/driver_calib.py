from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys
from hamilton_sdk import adapters
import yaml

from src.pipeline import features_calib
from src.tools import mytools
import logging

localconfig = mytools.read_local_config()


def main(tracker: bool = False, fcd: bool = False):
    import argparse
    parser = argparse.ArgumentParser(description="Calibration Discrete Pipeline")
    parser.add_argument('--tracker', action='store_true', help='Enable HamiltonTracker adapter')
    parser.add_argument('--fcd', action='store_true', help='Enable Calculate FCD')

    parser.add_argument('--config', type=str, help='Path to YAML config file')
    parser.add_argument('--log-level', type=str, default='INFO', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args, _ = parser.parse_known_args()
    tracker = args.tracker
    fcd = args.fcd
    log_level = args.log_level

    #if args.config:
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    #else:
    #    config = _base_config()

   
    postfix = f"calib_{config['detector']}"
    mytools.setup_logging(postfix, log_level=log_level)
    logger = logging.getLogger("calib")
    logger.info("-------------------------------------------------------")
    logger.info(f"date: {config['date']}, detector: {config['detector']}, iteration: {config['iteration']}, "+
    f"init_number: {config['init_number']}, base_estimator: {config['base_estimator']}, "+
    f"acq_func: {config['acq_func']}, n_initial_points: {config['n_initial_points']}, name: {config['name']}")
    logger.info("-------------------------------------------------------")

    builder = (
        driver.Builder()
        .with_config(config)
        .with_modules(features_calib)
        .with_adapters(base.DictResult)
        .with_adapters(base)
    )

    if tracker:
        tracker_adapter = adapters.HamiltonTracker(
            project_id=localconfig.get("project_id", "default_project"),
            username="kaveh",
            dag_name=f"calibration_{config['date']}_{config['detector']}_{config['init_number']}",
            tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
        )
        builder = builder.with_adapters(tracker_adapter)

    dr = builder.build()
    if fcd:
        result = dr.execute(["calibrated_data_FCD"])

    else:
        result = dr.execute(["calibrated_data"])

if __name__ == "__main__":
    main()
