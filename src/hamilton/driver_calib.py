from hamilton import driver
from typing import Dict, List, Optional, Tuple, Any, Union
from hamilton import driver, base
import sys

import features_calib

def _base_config() -> Dict[str, str]:
        """Return base configuration parameters for the simulation."""
        return {
            "date": "2020-01-01",
            "detector": "w2e_out",
            "path": "data/calibration_intermediate_data/",
            "pathout": "data/calibration_data/",
            "pathin": "data/daily_splitted_data/",
            "iteration": 50,
            "init_number" : -1,
            "network_file": "data/map/Hornsgatan.net.xml",
            "hornsgatan_home": "/home/kaveh/Hornsgatan/"
        }
config = _base_config()

# Option 1: Run the entire pipeline with the Hamilton driver
adapter = driver.Builder().with_config(config).with_modules(features_calib).build()

adapter.display_all_functions(
"diagram/calibration.png"
)    
result = adapter.execute(["calibrated_data"])
