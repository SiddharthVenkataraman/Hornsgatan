"""
Hornsgatan Traffic Simulation Pipeline

This module implements a Hamilton pipeline for the Hornsgatan traffic simulation,
transforming the original script into a modular pipeline with well-defined dependencies.
"""

import os
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import xml.etree.ElementTree as ET
import logging
import traci
import sumolib
from math import ceil
from hamilton import driver
from hamilton.function_modifiers import extract_fields, source




def maxspeed(detector: str) -> float:
    """Determine maximum speed based on detector type.
    
    Args:
        detector: Detector ID string
        
    Returns:
        Maximum speed value in m/s
    """
    if detector in ['e2w_out', 'e2w_in']:
        return 8.33
    else:
        return 13.89


# Data loading and preprocessing
def raw_data(pathin: str, date: str, detector: str) -> pd.DataFrame:
    """Load and filter the raw data for the specified detector.
    
    Args:
        pathin: Path to input data
        date: Date string for data file
        detector: Detector ID to filter for
        
    Returns:
        DataFrame containing filtered data
    """
    data = pd.read_csv(f'{pathin}data_{date}.csv')
    return data[data['detector_id'] == detector]


def preprocess_data(raw_data: pd.DataFrame, detector: str) -> pd.DataFrame:
    """Preprocess the raw data for the simulation.
    
    Args:
        raw_data: Raw data DataFrame
        detector: Detector ID string
        
    Returns:
        Preprocessed DataFrame
    """
    data = raw_data.copy()
    data.reset_index(drop=True, inplace=True)
    data.reset_index(inplace=True)
    data.rename(columns={"index": "id"}, inplace=True)
    data["id"] = data["id"].apply(lambda x: f"{x}_{detector}")
    data.sort_values(by=['time_detector_real'], inplace=True)
    return data

def number(init_number:int, preprocess_data: pd.DataFrame)->int:
    n = init_number
    if init_number<1: 
        n = len(preprocess_data)
    return n

def sample_data(preprocess_data: pd.DataFrame, number: int) -> pd.DataFrame:
    """Sample a subset of data for testing.
    
    Args:
        preprocessed_data: Preprocessed data DataFrame
        number: Number of samples to take
        
    Returns:
        Sampled DataFrame
    """
    return preprocess_data[["id", "detector_id", "time_detector_real", "speed_detector_real"]].head(number)


def postfix(detector: str, date: str, number: int, init_number:int) -> str:
    """Generate a postfix string for file naming.
    
    Args:
        detector: Detector ID string
        date: Date string
        number: Number of samples
        
    Returns:
        Formatted postfix string
    """
    if init_number<1:
        return f"{detector}_{date}"
    else:
        return f"{detector}_{date}_{number}"


# Detector mappings
#@source
def detector_mappings() -> Dict[str, Dict[str, Union[str, int]]]:
    """Return detector mappings for the simulation.
    
    Returns:
        Dictionary of detector mapping dictionaries
    """
    detector2lane = {
        "e2w_out": "1285834640_0",
        "e2w_in": "1285834640_1",
        "w2e_out": "151884974#0_0",
        "w2e_in": "151884974#0_1",
    }
    
    detector2laneN = {
        "e2w_out": 0,
        "e2w_in": 1,
        "w2e_out": 0,
        "w2e_in": 1,
    }
    
    detector2from = {
        "e2w_out": "24225358#0",
        "e2w_in": "24225358#0",
        "w2e_out": "151884975#0",
        "w2e_in": "151884975#0",
    }
    
    detector2to = {
        "e2w_out": "1243253622#0",
        "e2w_in": "1243253622#0",
        "w2e_out": "151884974#0",
        "w2e_in": "151884974#0",
    }
    
    detector2route = {
        "e2w_out": "24225358#0 1285834640 110107986#2 1243253630#0 98438064#0 1243253622#0",
        "e2w_in": "24225358#0 1285834640 110107986#2 1243253630#0 98438064#0 1243253622#0",
        "w2e_out": "151884975#0 1080999537#0 151884977#0 151884977#4 151884974#0",
        "w2e_in": "151884975#0 1080999537#0 151884977#0 151884977#4 151884974#0",
    }
    
    return {
        "detector2lane": detector2lane,
        "detector2laneN": detector2laneN,
        "detector2from": detector2from,
        "detector2to": detector2to,
        "detector2route": detector2route
    }


def instant_induction_loop_add_file(
    detector: str, 
    detector_mappings: Dict, 
    postfix: str,
    path: str
) -> str:
    """Generate XML for instant induction loop.
    
    Args:
        detector: Detector ID
        detector_mappings['detector2lane']: Dictionary mapping detectors to lanes
        instantInductionLoop_filename_xml: XML filename for instant induction loop
        instantInductionLoop_filename_add: Add XML filename for instant induction loop
        
    Returns:
        Generated XML string
    """
    instantInductionLoop_filename_xml =  f"instanceInductionLoop_{postfix}.xml"
    instantInductionLoop_filename_add =  f"instanceInductionLoop_{postfix}.add.xml"
    
    instant_induction_loops = [
        {"id": detector, "lane": detector_mappings['detector2lane'][detector], "pos": "1", "file": instantInductionLoop_filename_xml},
    ]
    root = ET.Element("additional")
    for loop in instant_induction_loops:
        ET.SubElement(root, "instantInductionLoop", loop)
    xml_string = ET.tostring(root, encoding="unicode").replace("<additional>", "<additional>\n").replace("/>", "/>\n")
    with open(f"{path}{instantInductionLoop_filename_add}", "w") as file:
        file.write(xml_string)
    return instantInductionLoop_filename_add


def induction_loop_add_file(
    detector: str, 
    detector_mappings: Dict, 
    postfix: str,
    path: str,
) -> str:
    """Generate XML for standard induction loop.
    
    Args:
        detector: Detector ID
        detector_mappings['detector2lane']: Dictionary mapping detectors to lanes
        inductionLoop_filename_xml: XML filename for induction loop
        inductionLoop_filename_add: Add XML filename for induction loop
        
    Returns:
        Generated XML string
    """
    
    inductionLoop_filename_xml =  f"inductionLoop_{postfix}.xml"
    inductionLoop_filename_add =  f"inductionLoop_{postfix}.add.xml"
    
    induction_loops = [
        {"id": detector, "lane": detector_mappings['detector2lane'][detector], "pos": "1", "period": "1", "file": inductionLoop_filename_xml},
    ]
    root = ET.Element("additional")
    for loop in induction_loops:
        ET.SubElement(root, "inductionLoop", loop)
    xml_string = ET.tostring(root, encoding="unicode").replace("<additional>", "<additional>\n").replace("/>", "/>\n")
    with open(f"{path}{inductionLoop_filename_add}", "w") as file:
        file.write(xml_string)
    return inductionLoop_filename_add


# Trips initialization
def trips(sample_data: pd.DataFrame, E2S_time: int = 28, W2S_time: int = 51) -> pd.DataFrame:
    """Initialize trips from data sample.
    
    Args:
        data_sample: Sampled data DataFrame
        E2S_time: East to South time offset in seconds
        W2S_time: West to South time offset in seconds
        
    Returns:
        Initialized trips DataFrame
    """
    trips = sample_data.copy()
    trips['depart'] = trips['time_detector_real'].copy()
    trips['depart'] = trips.apply(lambda row: row["time_detector_real"] - E2S_time if row['detector_id'][0] == 'e' else row["time_detector_real"] - W2S_time, axis=1)
    trips['from'] = trips['detector_id'].apply(lambda x: "24225358#0" if x[0] == 'e' else "151884975#0")
    trips['to'] = trips['detector_id'].apply(lambda x: "1243253622#0" if x[0] == 'e' else "151884974#0")
    trips['departLane'] = trips['detector_id'].apply(lambda x: "0" if x[-1] == 't' else "1")
    trips["departSpeed"] = 0
    trips["speed_detector_real"] = trips["speed_detector_real"].apply(lambda x: x / 3.6)
    trips.sort_values(by=["depart"], inplace=True)
    return trips


def save_trips_to_csv(trips: pd.DataFrame, path: str, postfix: str) -> str:
    """Save trips to CSV file.
    
    Args:
        trips: Trips DataFrame
        path: Output path
        postfix: Postfix for filename
        
    Returns:
        Path to saved CSV file
    """
    filename = f"{path}trips_{postfix}.csv"
    trips.to_csv(filename, index=False)
    return filename


# Route creation
def routes(trips: pd.DataFrame, routes_dict: Dict[str, str], path: str, postfix: str) -> str:
    """Create route file for SUMO simulation.
    
    Args:
        trips: Trips DataFrame
        routes_dict: Dictionary mapping detector IDs to routes
        path: Output path
        postfix: Postfix for filename
        
    Returns:
        Path to created route file
    """
    def convert_row(row, routes_dict=routes_dict, departPos="0", arrivalPos="max"):
        return (
            f'\n<vehicle id="{row.id}" depart="{row.depart}" departLane="{row.departLane}" '
            f'departSpeed="{row.departSpeed}" departPos="{departPos}" arrivalPos="{arrivalPos}">'
            f'\n    <route edges="{routes_dict[row.detector_id]}"/>\n</vehicle>'
        )
    
    myroutes = trips.copy()
    text0 = '<?xml version="1.0" encoding="UTF-8"?>\n\n\n'
    text1 = '<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">'
    text2 = ''.join(myroutes.apply(convert_row, axis=1))
    text3 = '\n</routes>'
    
    route_filename = f"{path}routes_{postfix}.xml"
    with open(route_filename, 'w') as myfile:
        myfile.write(text0 + text1 + text2 + text3)
    
    return route_filename


# SUMO configuration file
def sumo_config(network_file: str, induction_loop_add_file: str, trips: pd.DataFrame, path: str, postfix: str) -> str:
    """Create SUMO configuration file.
    
    Args:
        network_file: Path to network file
        additional_file: Path to additional file
        trips: Trips DataFrame
        path: Output path
        postfix: Postfix for filename
        
    Returns:
        Path to created configuration file
    """
    start_time = trips["depart"].min()
    config_file_name = f"{path}simulation_{postfix}.sumo.cfg"
    
    config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="../../{network_file}"/>
        <additional-files value="{induction_loop_add_file}"/>
    </input>
    <processing>
        <default.speeddev value="0"/>
    </processing>
    <time>
        <begin value="{start_time}"/>
    </time>
    <random>
        <seed value="13"/>
    </random>
    <report>
        <no-step-log value="true"/>
        <no-warnings value="true"/>
    </report>
</configuration>
"""
    
    with open(config_file_name, "w") as config_file:
        config_file.write(config_content)
    
    return config_file_name


# Logging setup
def setup_logging(postfix: str) -> str:
    """Set up logging for the simulation.
    
    Args:
        postfix: Postfix for log filename
        
    Returns:
        Path to log file
    """
    logfile_name = f"log/simulation_{postfix}.log"
    logging.basicConfig(
        filename=logfile_name,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Simulation started.")
    return logfile_name


# Calibration process
def setup_traci_simulation(
    sumo_config: str, 
    trips: pd.DataFrame, 
    detector: str, 
    detector_mappings: Dict, 
    path: str, 
    postfix: str
) -> str:
    """Set up TraCI simulation environment.
    
    Args:
        config_file_name: Path to SUMO config file
        trips: Trips DataFrame
        detector: Detector ID
         detector_mappings: Combined detector DataFrame
        path: Output path
        postfix: Postfix for filenames
        
    Returns:
        SUMO binary path
    """
    sumo_binary = "sumo"
    
    if traci.isLoaded():
        traci.close()
    
    traci.start([sumo_binary, "-c", sumo_config, "--begin", str(trips["depart"][0])])
    traci.route.add(f"{detector}_route",  detector_mappings["detector2route"][detector].split())
    traci.simulation.saveState(f"{path}simulation_{postfix}_next.sumo.state")
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    return sumo_binary


def _calibrate_single_vehicle(
    row: dict, 
    detector: str, 
    maxspeed: float, 
    path: str, 
    postfix: str, 
    iteration: int, 
    mylog: List#[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calibrate a single vehicle in the simulation.
    
    Args:
        row: Vehicle data row
        detector: Detector ID
        maxspeed: Maximum speed value
        path: Output path
        postfix: Postfix for filenames
        iteration: Maximum number of iterations
        mylog: List of calibration results
        
    Returns:
        Dictionary with calibration result for this vehicle
    """
    traci.simulation.loadState(f"{path}simulation_{postfix}_next.sumo.state")
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    
    logging.info(f"Processing vehicle ID: {row['id']}")
    
    time_error = 10
    speed_error = 10
    count = 0
    time = None
    speed = None
    prow = row.copy()
    
    # Adjust depart time for consecutive vehicles
    if len(mylog) > 0 and count == 1:
        row["depart"] = mylog[-1]["depart"] + (row["time_detector_real"] - mylog[-1]["time_detector_real"])
    
    while (count < iteration) and ((abs(time_error) > 2) or abs(speed_error) > 1):
        count += 1
        
        try:
            traci.simulation.loadState(f"{path}simulation_{postfix}.sumo.state")
        except traci.FatalTraCIError as e:
            print("Error loading simulation state:", e)
            logging.error(f"Error loading simulation state: {e}")
            traci.close()
            raise
        
        # Remove the vehicle if it exists
        if row['id'] in traci.vehicle.getIDList():
            traci.vehicle.remove(row['id'])
        
        try:
            traci.vehicle.addFull(
                vehID=row['id'],
                routeID=f"{row['detector_id']}_route",
                depart=row["depart"],
                departPos="0",
                departSpeed="max",
                departLane=row["departLane"],
            )
            #traci.vehicle.setSpeedMode(row['id'], 95)
            traci.vehicle.setSpeed(row['id'], row["speed_factor"] * maxspeed)
            row["departSpeed"] = row["speed_factor"] * maxspeed
            traci.vehicle.setLaneChangeMode(row['id'], 0)
        except traci.TraCIException as e:
            print(f"Error adding vehicle {row['id']}:", e)
            logging.error(f"Error adding vehicle {row['id']}: {e}")
            traci.close()
            raise
        
        traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])
        
        time_speed = _run_simulation_steps(row, detector, path, postfix)
        if time_speed is not None:
            time, speed = time_speed
            
            time_error = time - row["time_detector_real"]
            speed_error = speed - row["speed_detector_real"]
            
            prow = row.copy()
            row["depart"] = row["depart"] - (time - row["time_detector_real"])
            
            if len(mylog) > 0 and row["depart"] <= mylog[-1]["depart"]:
                row["depart"] = mylog[-1]["depart"] + 1
            
            if speed_error > 0 and speed_error > 1:
                row["speed_factor"] = max(.9, row["speed_factor"] - 0.01)
            if speed_error <= 0 and speed_error < -.3:
                row["speed_factor"] = min(3, row["speed_factor"] + 0.1)
            
            row["departSpeed"] = maxspeed
            if row['speed_factor'] != 1:
                row["departSpeed"] = maxspeed * row["speed_factor"]
    
    return {
        "veh_id": prow["id"],
        "time_detector_sim": time,
        "speed_detector_sim": speed,
        "speed_factor": prow["speed_factor"],
        "time_detector_real": prow["time_detector_real"],
        "depart": prow["depart"],
        "departSpeed": prow["departSpeed"],
        "speed_detector_real": prow["speed_detector_real"]
    }


def _run_simulation_steps(row: dict, detector: str, path: str, postfix: str) -> Optional[Tuple[float, float]]:
    """Run simulation steps until the vehicle passes the detector.
    
    Args:
        row: Vehicle data row
        detector: Detector ID
        path: Output path
        postfix: Postfix for filenames
        
    Returns:
        Tuple of (time, speed) or None if vehicle didn't pass detector
    """
    time = None
    speed = None
    
    while traci.simulation.getMinExpectedNumber() > 0:
        if traci.simulation.getTime() == int(row["depart"]) + 1:
            #traci.vehicle.setSpeed(row["id"], row["departSpeed"])
            #traci.vehicle.setLaneChangeMode(row["id"], 0)
            traci.simulation.saveState(f"{path}simulation_{postfix}_next.sumo.state")
        
        traci.simulationStep()
        
        #for veh_id in traci.simulation.getDepartedIDList():
        #    traci.vehicle.setLaneChangeMode(veh_id, 0)
        
        vehicles = traci.inductionloop.getLastStepVehicleIDs(detector)
        
        if vehicles and vehicles[0] == row["id"]:
            veh_id, veh_length, entry_time, exit_time, vType = traci.inductionloop.getVehicleData(detector)[0]
            speed = traci.inductionloop.getLastStepMeanSpeed(detector)
            time = round(entry_time - 1, 2)
            return time, speed
    
    return None

def calibrated_data(
    trips: pd.DataFrame, 
    sumo_config: str, 
    detector_mappings: Dict, 
    detector: str, 
    maxspeed: float, 
    path: str, 
    postfix: str, 
    pathout: str,
    iteration: int = 30,
) -> pd.DataFrame:
    """Run the calibration process for all vehicles.
    
    Args:
        trips: Trips DataFrame
        detector: Detector ID
        maxspeed: Maximum speed value
        path: Output path
        postfix: Postfix for filenames
        iteration: Maximum number of iterations
        
    Returns:
        DataFrame with calibration results
    """
    
    setup_traci_simulation(
    sumo_config, 
    trips, 
    detector, 
    detector_mappings, 
    path, 
    postfix) 
    
    trips["departSpeed"] = maxspeed
    trips["speed_factor"] = 1
    
    mylog = []
    step = 0
    
    for index, row in trips.iterrows():
        result = _calibrate_single_vehicle(dict(row), detector, maxspeed, path, postfix, iteration, mylog)
        mylog.append(result)
        step += 1
    
    if traci.isLoaded():
        traci.close()
    out_df = pd.DataFrame(mylog)
    out_df["delta_time"] = out_df["time_detector_sim"] - out_df["time_detector_real"]
    out_df["delta_speed"] = out_df["speed_detector_sim"] - out_df["speed_detector_real"]
    out_df.to_csv(f"{pathout}calibrated_data_{postfix}.csv", index=False)
    return out_df



