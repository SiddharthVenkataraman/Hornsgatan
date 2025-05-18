from hamilton import driver, base
import os
from hamilton_sdk import adapters
from hamilton import driver

from . import features_import_data
from ..tools import mytools
myconfig = mytools.read_config()
# Replace with your target path
#os.chdir(".")

# Confirm the current directory
#print("Current directory:", os.getcwd())

tracker = adapters.HamiltonTracker(
project_id= myconfig["project_id"],  # modify this as needed
username="kaveh",
dag_name="Import Data",
tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
)
#if __name__ == "__main__":
config = {
    "dataFilename": "test_radar_data",  # or any other file name (without .csv)
    "sensorFilename": "sensor_info"
}

outputs = [
    "transform_raw_data",
    "save_transform_raw_data",
    "split_and_save_daily"
]
dr = driver.Driver(config, features_import_data)
dr = (
    driver.Builder()
    .with_config(config)  # we don't have any configuration or invariant data for this example.
    .with_modules(features_import_data)  # we need to tell hamilton where to load function definitions from
    .with_adapters(base.DictResult)  # we want a pandas dataframe as output
    .with_adapters(tracker)
    .build()
)
results = dr.execute(outputs)
print(results["save_transform_raw_data"])
print(results["split_and_save_daily"])
#print(results["transform_raw_data"])
#print(results["transform_raw_data"].head(5))
