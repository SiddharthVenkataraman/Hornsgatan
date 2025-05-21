from hamilton import driver, base
import os
from hamilton_sdk import adapters
from hamilton import driver
import yaml
import logging

from src.pipeline import features_import_data
from src.tools import mytools
myconfig = mytools.read_config()
# Replace with your target path
#os.chdir(".")

# Confirm the current directory
#print("Current directory:", os.getcwd())
"""tracker = adapters.HamiltonTracker(
project_id= myconfig["project_id"],  # modify this as needed
username="kaveh",
dag_name="Import Data",
tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
)
"""

def _base_config():
    return {
        "dataFilename": "test_radar_data",  # or any other file name (without .csv)
        "sensorFilename": "sensor_info"
    }

def main(tracker: bool = False):
    import argparse
    parser = argparse.ArgumentParser(description="Import Data Pipeline")
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

    postfix = config.get("dataFilename", "import_data")
    mytools.setup_logging(postfix, log_level=log_level)
    logger = logging.getLogger("import_data")

    outputs = [
        "transform_raw_data",
        "save_transform_raw_data",
        "split_and_save_daily"
    ]
    builder = (
        driver.Builder()
        .with_config(config)
        .with_modules(features_import_data)
        .with_adapters(base.DictResult)
        .with_adapters(base)
    )
    if tracker:
        tracker_adapter = adapters.HamiltonTracker(
            project_id=myconfig.get("project_id", "default_project"),
            username="kaveh",
            dag_name="Import Data",
            tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
        )
        builder = builder.with_adapters(tracker_adapter)
    dr = builder.build()
    results = dr.execute(outputs)
    print(results["save_transform_raw_data"])
    print(results["split_and_save_daily"])
    #print(results["transform_raw_data"])
    #print(results["transform_raw_data"].head(5))

if __name__ == "__main__":
    main()
