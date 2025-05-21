# main.py
import sys
import os

# Ensure src is in the path for script execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import argparse

def run_import_data():
    from src.pipeline import driver_import_data
    driver_import_data.main()

def run_calib():
    from src.pipeline import driver_calib
    driver_calib.main()

def run_sim():
    from src.pipeline import driver_sim
    driver_sim.main()

def run_my_driver():
    # my_driver does not have a main(), so we run as script
    import runpy
    runpy.run_module('src.pipeline.my_driver', run_name='__main__')

PIPELINES = {
    "import_data": run_import_data,
    "calib": run_calib,
    "sim": run_sim,
}

def main():
    parser = argparse.ArgumentParser(description="Hornsgatan Pipeline Runner")
    parser.add_argument(
        "--pipeline",
        type=str,
        required=True,
        choices=PIPELINES.keys(),
        help="Which pipeline to run: import_data, calib_discrete, calib, sim, my_driver"
    )
    # Parse only known args so that --tracker and others are passed through
    args, unknown = parser.parse_known_args()
    sys.argv = [sys.argv[0]] + unknown
    PIPELINES[args.pipeline]()

if __name__ == "__main__":
    main()