"""
Hornsgatan Traffic Simulation Pipeline

This module implements a Hamilton pipeline for the Hornsgatan traffic simulation,
transforming the original script into a modular pipeline with well-defined dependencies.
"""

import os
import shutil

from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import xml.etree.ElementTree as ET
#from ..tools import mytools
#import libsumo as traci
import traci
from math import ceil
from hamilton import driver
from hamilton.function_modifiers import extract_fields, source
from skopt import Optimizer
import numpy as np
from skopt.space import Integer
import logging
import csv

logger = logging.getLogger("calib")


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
    
    detector2traveltimetosensor = {
        "e2w_out": 28,
        "e2w_in": 28,
        "w2e_out": 51,
        "w2e_in": 51,
    }
    
    return {
        "detector2lane": detector2lane,
        "detector2laneN": detector2laneN,
        "detector2from": detector2from,
        "detector2to": detector2to,
        "detector2route": detector2route,
        "detector2traveltimetosensor": detector2traveltimetosensor,
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
def trips(sample_data: pd.DataFrame,  detector_mappings: Dict, detector:str) -> pd.DataFrame:
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
    trips['depart'] = trips["time_detector_real"].apply(lambda x:
                      x - detector_mappings["detector2traveltimetosensor"][detector])
    trips['from'] = detector_mappings["detector2from"][detector]
    trips['to'] = detector_mappings["detector2to"][detector]
    trips['departLane'] =  detector_mappings["detector2laneN"][detector]
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
def sumo_config(network_file: str, induction_loop_add_file: str,instant_induction_loop_add_file:str, trips: pd.DataFrame, path: str, postfix: str) -> str:
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
        <emergency-insert value="true"/>
        <random-depart-offset value="0"/>
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
        
  

    
    traci.start([sumo_binary, "-c", sumo_config, "--begin", str(trips["depart"][0]-100)])
    traci.route.add(f"{detector}_route",  detector_mappings["detector2route"][detector].split())
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    return sumo_binary


def _calibrate_single_vehicle_FCD(
    row: dict, 
    detector: str, 
    maxspeed: float, 
    path: str, 
    postfix: str, 
    iteration: int, 
    mylog: List,
    base_estimator: str,   #{"GP", "RF", "ET", "GBRT"}
    acq_func: str, #{"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
    n_initial_points: int,
) -> Tuple[Dict[str, Any], list]:
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
    #traci.simulation.loadState(f"{path}simulation_{postfix}_next.sumo.state")
    #traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    
    logger.info(f"Processing vehicle ID: {row['id']}")
    
    time = None
    speed = None
    simlog = []
    time_list = []
    speed_list = []
    simlog_list = []
    
    if len(mylog) > 0:
        depart_min = mylog[-1]["depart"]+1
    else:
        depart_min = row["time_detector_real"] - 100
        
    depart_max = max(row["time_detector_real"] - 10, depart_min +2)
    
    
    speed_factor_min = 0.6
    speed_factor_max = 3.2
    speed_factor_resolution = 20
    
    bounds = [Integer(0, depart_max-depart_min), Integer(int(speed_factor_min*speed_factor_resolution), int(speed_factor_max*speed_factor_resolution))]
    #bounds = [Integer(0, depart_max-depart_min), (speed_factor_min, speed_factor_max)]

    logger.info(row)
    logger.info(f"bounds = {bounds}, depart_min = {depart_min} ")
    
    # --- Initialize Bayesian Optimizer ---
    opt = Optimizer(dimensions=bounds, base_estimator=base_estimator, acq_func=acq_func, n_initial_points=n_initial_points)
    for i in range(iteration):
        x_next = opt.ask()                 # Propose next point
        row['depart'] = x_next[0]+depart_min
        row["speed_factor"] = x_next[1]/speed_factor_resolution
        #row["speed_factor"] = x_next[1]
 
        time_speed_simlog = _run_simulation_steps_FCD(row, detector, path, postfix, i, maxspeed=maxspeed)
        if time_speed_simlog is not None:
            time, speed,simlog = time_speed_simlog
            time_list.append(time)
            speed_list.append(speed)
            simlog_list.append(simlog)
            
        else:
            logger.info("errorrrrrrrrrrr in time-speeeeeeeed")
        time_error = time-row["time_detector_real"]
        speed_error = speed - row["speed_detector_real"]


        y_next = (time_error)**2 + (speed_error)**2
        y_next = y_next - .5*(row["speed_factor"]-speed_factor_min)/(speed_factor_max-speed_factor_min)
        y_next = y_next + (row['depart']-depart_min)/(depart_max-depart_min)

        opt.tell(x_next, y_next)          # Give result to optimizer
        #logger.info(f"Iter {i}: Input={x_next}, Error={y_next:.4f}, time_error={time_error},  speed_error={speed_error}")
        
    # --- Best result ---
    best_index = np.argmin(opt.yi)
    best_x = opt.Xi[best_index]
    best_y = min(opt.yi)
    logging.info(f"Best estimate: index = {best_index}" )
    logging.info(f"Depart time: {depart_min+ best_x[0]} s, factor speed: {round(best_x[1]/speed_factor_resolution, 2)} ")
    logging.info(f"Minimum error: {best_y:.4f}")
    logging.info(f"best_time_error={round(time_list[best_index]-row['time_detector_real'],3)}, best_speed_error={round(speed_list[best_index]-row['speed_detector_real'],3)} ")
    #for item in simlog_list[best_index]:
    #    logging.info(f"simlog = {item} ")

    traci.simulation.loadState(f"{path}simulation_{postfix}_{best_index}.sumo.state")
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    
    return {
        "veh_id": row["id"],
        "time_detector_sim": time_list[best_index],
        "speed_detector_sim": speed_list[best_index],
        "speed_factor": round((best_x[1]/speed_factor_resolution),2),
        #"speed_factor": round(best_x[1],2),

        "time_detector_real": row["time_detector_real"],
        "depart": best_x[0]+depart_min,
        "departSpeed": maxspeed * round((best_x[1]/speed_factor_resolution),2) ,
        "speed_detector_real": row["speed_detector_real"]
    }, simlog_list[best_index]



def _run_simulation_steps_FCD(row: dict, detector: str, path: str, postfix: str, iteration_number:int, maxspeed: float) -> Optional[Tuple[float, float]]:
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
    simulation_log =[]
    
    try:
        traci.simulation.loadState(f"{path}simulation_{postfix}.sumo.state")
    except traci.FatalTraCIError as e:
        logger.error(f"Error loading simulation state: {e}")
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
        row["departSpeed"] = row["speed_factor"] * maxspeed
        traci.vehicle.setLaneChangeMode(row['id'], 0)
    except traci.TraCIException as e:
        logger.error(f"Error adding vehicle {row['id']}: {e}")
        traci.close()
        raise
    
    traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])
    traci.vehicle.setSpeed(row['id'], row["speed_factor"] * maxspeed)
    
    #traci.vehicle.setMaxSpeed(row["id"], row["speed_factor"] * maxspeed)



    
    while traci.simulation.getMinExpectedNumber() > 0:
        #print(f"step  = {traci.simulation.getTime()}  , depart  = {row["depart"]}")
            
        traci.simulationStep()
                    
        simtime = traci.simulation.getTime()
        if simtime == int(row["depart"])+1:
            traci.simulation.saveState(f"{path}simulation_{postfix}_{iteration_number}.sumo.state")
            #print (f"depart = {row["depart"]}, step = {traci.simulation.getMinExpectedNumber()}, ite = {iteration_number}" )
        
        #if simtime == int(row["depart"]):
            #traci.vehicle.setSpeed(row['id'], row["speed_factor"] * maxspeed)
            #traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])

        #    logger.info(f"iteration = {iteration_number}, speedfactor = {traci.vehicle.getSpeedFactor(row['id'])}, speed ={traci.vehicle.getSpeed(row['id'])}")

        
        if simtime <= int(row["depart"])+1:
            for veh in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(veh)
                lon, lat = traci.simulation.convertGeo(x, y)
                #lon, lat = self.net.convertXY2LonLat(x, y)
                simulation_log.append({"time": int(simtime)-1,
                                       "id":veh,
                                       "speedfactor": traci.vehicle.getSpeedFactor(veh),
                                       "x":round(lon,6),
                                       "y":round(lat,6),
                                       "angle":round(traci.vehicle.getAngle(veh),2),
                                       "speed":round(traci.vehicle.getSpeed(veh),2), 
                                       "acceleration":round(traci.vehicle.getAcceleration(veh),2),
                                       "pos":round(traci.vehicle.getLanePosition(veh),2),
                                       "lane":traci.vehicle.getLaneID(veh),
                                       "noise":round(traci.vehicle.getNoiseEmission(veh),2)})
            #if not (traci.vehicle.getIDList()):
            #    simulation_log.append({"time": int(simtime)-1})
          
        
        
        
        vehicles = traci.inductionloop.getLastStepVehicleIDs(detector)
        
        if vehicles and vehicles[0] == row["id"]:
            veh_id, veh_length, entry_time, exit_time, vType = traci.inductionloop.getVehicleData(detector)[0]
            speed = traci.inductionloop.getLastStepMeanSpeed(detector)
            time = round(entry_time - 1, 2)
            #time = round(entry_time, 2)

            return time, speed, simulation_log
    
    return None


def calibrated_data_FCD(
    trips: pd.DataFrame,
    sumo_config: str,
    detector_mappings: Dict,
    detector: str,
    maxspeed: float,
    path: str,
    postfix: str,
    pathout: str,
    iteration: int,
    base_estimator: str,   #{"GP", "RF", "ET", "GBRT"}
    acq_func: str, #{"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
    n_initial_points: int,
) -> str:
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
    # Determine the output file path
    output_csv_path = f"{pathout}calibrated_data_{postfix}.csv"
    logsim_csv_path = f"{pathout}fcd_data_{postfix}.csv"

    # Define the CSV column headers based on the result dictionary keys and the calculated deltas
    csv_headers = [
        "veh_id",
        "time_detector_sim",
        "speed_detector_sim",
        "speed_factor",
        "time_detector_real",
        "depart",
        "departSpeed",
        "speed_detector_real",
        "delta_time",
        "delta_speed"
    ]
    
    fcd_header = [
        "time",
        "id",
        "speedfactor",
        "x",
        "y",
        "angle",
        "speed", 
        "acceleration",
        "pos",
        "lane",
        "noise",   
    ]

    # Open the CSV file in write mode to create a new file and write the header
    # Use newline='' to prevent extra blank rows.
    logsim_list = []
    
    with open(output_csv_path, 'w', newline='') as result_csv,  \
         open(logsim_csv_path, 'w', newline='') as fcd_csv:

        result_writer = csv.writer(result_csv)
        fcd_writer = csv.writer(fcd_csv)

        result_writer.writerow(csv_headers)
        fcd_writer.writerow(fcd_header)  # Assuming each dict in logsim_list has these keys


        #mylog = [] # Keep mylog for existing logic if needed later in the function
        step = 0

        for index, row in trips.iterrows():
            result, logsim_list = _calibrate_single_vehicle_FCD(dict(row), detector, maxspeed, path, postfix, iteration, mylog,
                                               base_estimator, acq_func, n_initial_points )

            # Calculate the delta values for the current vehicle
            result["delta_time"] = result["time_detector_sim"] - result["time_detector_real"]
            result["delta_speed"] = result["speed_detector_sim"] - result["speed_detector_real"]
            mylog.append(result)
            # Write the current vehicle's result as a row to the CSV
            row_data = [result.get(header, "") for header in csv_headers] # Use .get to handle missing keys gracefully
            result_writer.writerow(row_data)

            # FCD ---------
            for log_row in logsim_list:
                fcd_writer.writerow([log_row.get(h, "") for h in fcd_header])
                logger.info(log_row)
            #mylog.append(result) # Keep appending to mylog if needed for other logic
            step += 1

    # The file is automatically closed when exiting the 'with' block.
    # The original code then converts mylog to a DataFrame and saves again.
    # If you only want to save once per vehicle in the loop, you can remove the DataFrame conversion and final save outside the loop.
    # Let's keep the final save to maintain the original function's output structure,
    # although the file has already been written row by row.
    # Note: This will overwrite the file just created in the loop, but ensures consistency
    # if other parts of the pipeline expect the DataFrame return value or the final file format.

    if traci.isLoaded():
        traci.close()
    #out_df = pd.DataFrame(mylog)
    #out_df["delta_time"] = out_df["time_detector_sim"] - out_df["time_detector_real"] # Recalculate deltas for the DataFrame
    #out_df["delta_speed"] = out_df["speed_detector_sim"] - out_df["speed_detector_real"] # Recalculate deltas for the DataFrame
    #out_df.to_csv(f"{pathout}calibrated_data_{postfix}.csv", index=False)
    return output_csv_path


##########   NO  FCD  Version  ####################

def calibrated_data(
    trips: pd.DataFrame,
    sumo_config: str,
    detector_mappings: Dict,
    detector: str,
    maxspeed: float,
    path: str,
    postfix: str,
    pathout: str,
    iteration: int,
    base_estimator: str,   #{"GP", "RF", "ET", "GBRT"}
    acq_func: str, #{"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
    n_initial_points: int,
) -> str:
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
    # Determine the output file path
    output_csv_path = f"{pathout}calibrated_data_{postfix}.csv"

    # Define the CSV column headers based on the result dictionary keys and the calculated deltas
    csv_headers = [
        "veh_id",
        "time_detector_sim",
        "speed_detector_sim",
        "speed_factor",
        "time_detector_real",
        "depart",
        "departSpeed",
        "speed_detector_real",
        "delta_time",
        "delta_speed"
    ]

    # Open the CSV file in write mode to create a new file and write the header
    # Use newline='' to prevent extra blank rows.
    logsim_list = []
    
    with open(output_csv_path, 'w', newline='') as result_csv:

        result_writer = csv.writer(result_csv)

        result_writer.writerow(csv_headers)


        #mylog = [] # Keep mylog for existing logic if needed later in the function
        step = 0

        for index, row in trips.iterrows():
            result = _calibrate_single_vehicle(dict(row), detector, maxspeed, path, postfix, iteration, mylog,
                                               base_estimator, acq_func, n_initial_points )

            # Calculate the delta values for the current vehicle
            result["delta_time"] = result["time_detector_sim"] - result["time_detector_real"]
            result["delta_speed"] = result["speed_detector_sim"] - result["speed_detector_real"]
            mylog.append(result)
            # Write the current vehicle's result as a row to the CSV
            row_data = [result.get(header, "") for header in csv_headers] # Use .get to handle missing keys gracefully
            result_writer.writerow(row_data)

         
            #mylog.append(result) # Keep appending to mylog if needed for other logic
            step += 1

    # The file is automatically closed when exiting the 'with' block.
    # The original code then converts mylog to a DataFrame and saves again.
    # If you only want to save once per vehicle in the loop, you can remove the DataFrame conversion and final save outside the loop.
    # Let's keep the final save to maintain the original function's output structure,
    # although the file has already been written row by row.
    # Note: This will overwrite the file just created in the loop, but ensures consistency
    # if other parts of the pipeline expect the DataFrame return value or the final file format.

    if traci.isLoaded():
        traci.close()
    #out_df = pd.DataFrame(mylog)
    #out_df["delta_time"] = out_df["time_detector_sim"] - out_df["time_detector_real"] # Recalculate deltas for the DataFrame
    #out_df["delta_speed"] = out_df["speed_detector_sim"] - out_df["speed_detector_real"] # Recalculate deltas for the DataFrame
    #out_df.to_csv(f"{pathout}calibrated_data_{postfix}.csv", index=False)
    return output_csv_path



def _calibrate_single_vehicle(
    row: dict, 
    detector: str, 
    maxspeed: float, 
    path: str, 
    postfix: str, 
    iteration: int, 
    mylog: List,
    base_estimator: str,   #{"GP", "RF", "ET", "GBRT"}
    acq_func: str, #{"LCB", "EI", "PI", "MES", "PVRS", "gp_hedge", "EIps", "PIps"}
    n_initial_points: int,
) -> Tuple[Dict[str, Any], list]:
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
    #traci.simulation.loadState(f"{path}simulation_{postfix}_next.sumo.state")
    #traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    
    logger.info(f"Processing vehicle ID: {row['id']}")
    
    time = None
    speed = None
    simlog = []
    time_list = []
    speed_list = []
    
    if len(mylog) > 0:
        depart_min = mylog[-1]["depart"]+1
    else:
        depart_min = row["time_detector_real"] - 100
        
    depart_max = max(row["time_detector_real"] - 10, depart_min +2)
    
    
    speed_factor_min = 0.6
    speed_factor_max = 3.2
    speed_factor_resolution = 20

    
    bounds = [Integer(0, depart_max-depart_min), Integer(int(speed_factor_min*speed_factor_resolution), int(speed_factor_max*speed_factor_resolution))]
    #bounds = [Integer(0, depart_max-depart_min), (speed_factor_min, speed_factor_max)]

    logger.info(row)
    logger.info(f"bounds = {bounds}, depart_min = {depart_min} ")
    
    # --- Initialize Bayesian Optimizer ---
    opt = Optimizer(dimensions=bounds, base_estimator=base_estimator, acq_func=acq_func, n_initial_points=n_initial_points)
    for i in range(iteration):
        x_next = opt.ask()                 # Propose next point
        row['depart'] = x_next[0]+depart_min
        row["speed_factor"] = x_next[1]/speed_factor_resolution
        #row["speed_factor"] = x_next[1]
 
        time_speed = _run_simulation_steps(row, detector, path, postfix, i, maxspeed=maxspeed)
        if time_speed is not None:
            time, speed = time_speed
            time_list.append(time)
            speed_list.append(speed)
            
        else:
            logger.info("errorrrrrrrrrrr in time-speeeeeeeed")
        time_error = time-row["time_detector_real"]
        speed_error = speed - row["speed_detector_real"]


        y_next = (time_error)**2 + (speed_error)**2
        y_next = y_next - .5*(row["speed_factor"]-speed_factor_min)/(speed_factor_max-speed_factor_min)
        y_next = y_next + (row['depart']-depart_min)/(depart_max-depart_min)

        opt.tell(x_next, y_next)          # Give result to optimizer
        #logger.info(f"Iter {i}: Input={x_next}, Error={y_next:.4f}, time_error={time_error},  speed_error={speed_error}")
        
    # --- Best result ---
    best_index = np.argmin(opt.yi)
    best_x = opt.Xi[best_index]
    best_y = min(opt.yi)
    logging.info(f"Best estimate: index = {best_index}" )
    logging.info(f"Depart time: {depart_min+ best_x[0]} s, factor speed: {round(best_x[1]/speed_factor_resolution, 2)} ")
    logging.info(f"Minimum error: {best_y:.4f}")
    logging.info(f"best_time_error={round(time_list[best_index]-row['time_detector_real'],3)}, best_speed_error={round(speed_list[best_index]-row['speed_detector_real'],3)} ")
    #for item in simlog_list[best_index]:
    #    logging.info(f"simlog = {item} ")

    traci.simulation.loadState(f"{path}simulation_{postfix}_{best_index}.sumo.state")
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")
    
    return {
        "veh_id": row["id"],
        "time_detector_sim": time_list[best_index],
        "speed_detector_sim": speed_list[best_index],
        "speed_factor": round((best_x[1]/speed_factor_resolution),2),
        #"speed_factor": round(best_x[1],2),

        "time_detector_real": row["time_detector_real"],
        "depart": best_x[0]+depart_min,
        "departSpeed": maxspeed * round((best_x[1]/speed_factor_resolution),2) ,
        "speed_detector_real": row["speed_detector_real"]
    }



def _run_simulation_steps(row: dict, detector: str, path: str, postfix: str, iteration_number:int, maxspeed: float) -> Optional[Tuple[float, float]]:
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
    simulation_log =[]
    
    try:
        traci.simulation.loadState(f"{path}simulation_{postfix}.sumo.state")
    except traci.FatalTraCIError as e:
        logger.error(f"Error loading simulation state: {e}")
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
        row["departSpeed"] = row["speed_factor"] * maxspeed
        traci.vehicle.setLaneChangeMode(row['id'], 0)
    except traci.TraCIException as e:
        logger.error(f"Error adding vehicle {row['id']}: {e}")
        traci.close()
        raise
    
    traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])
    traci.vehicle.setSpeed(row['id'], row["speed_factor"] * maxspeed)
    
    #traci.vehicle.setMaxSpeed(row["id"], row["speed_factor"] * maxspeed)

    
    while traci.simulation.getMinExpectedNumber() > 0:
        #print(f"step  = {traci.simulation.getTime()}  , depart  = {row["depart"]}")
            
        traci.simulationStep()
                    
        simtime = traci.simulation.getTime()
        if simtime == int(row["depart"])+1:
            traci.simulation.saveState(f"{path}simulation_{postfix}_{iteration_number}.sumo.state")
            #print (f"depart = {row["depart"]}, step = {traci.simulation.getMinExpectedNumber()}, ite = {iteration_number}" )
      
        
        vehicles = traci.inductionloop.getLastStepVehicleIDs(detector)
        
        if vehicles and vehicles[0] == row["id"]:
            veh_id, veh_length, entry_time, exit_time, vType = traci.inductionloop.getVehicleData(detector)[0]
            speed = traci.inductionloop.getLastStepMeanSpeed(detector)
            time = round(entry_time - 1, 2)
            #time = round(entry_time, 2)

            return time, speed
    
    return None

