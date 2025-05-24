#import libsumo as traci
import traci

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import xml.etree.ElementTree as ET
logger = logging.getLogger("sim")



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
    
def number(init_number:int)->int:
    n = init_number
    if init_number<1: 
        n = 0
    return n

def postfix(detector: str, date: str, number: int) -> str:
    """Generate a postfix string for file naming.
    
    Args:
        detector: Detector ID string
        date: Date string
        number: Number of samples
        
    Returns:
        Formatted postfix string
    """
    if number<1:
        return f"{detector}_{date}"
    else:
        return f"{detector}_{date}_{number}"
    
def calibrated_data(postfix:str, detector:str, pathin:str) -> pd.DataFrame:
    calibrated_data = pd.read_csv(f'{pathin}calibrated_data_{postfix}.csv')
    #calibrated_data = calibrated_data[calibrated_data['detector_id'] == detector]
    return calibrated_data

def detector_mappings() -> Dict[str, Dict]:
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
    path: str,
    pathout: str,
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
    instantInductionLoop_filename_xml =  f"../../{pathout}instantInductionLoop_{postfix}.xml"
    instantInductionLoop_filename_add =  f"instantInductionLoop_{postfix}.add.xml"
    
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



def trips(calibrated_data: pd.DataFrame, detector_mappings:  Dict[str,Dict], detector:str) -> pd.DataFrame:
    """Initialize trips from data sample.
    
    Args:
        data_sample: Sampled data DataFrame
        E2S_time: East to South time offset in seconds
        W2S_time: West to South time offset in seconds
        
    Returns:
        Initialized trips DataFrame
    """
    trips = calibrated_data.copy()
    trips['from'] = detector_mappings["detector2from"][detector]
    trips['to']   = detector_mappings["detector2to"][detector]
    trips['departLane'] = detector_mappings["detector2laneN"][detector]
    trips["detector_id"] = detector
    trips.rename(columns={"veh_id": "id"}, inplace=True)
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
def routes(trips: pd.DataFrame, detector_mappings:  Dict[str,Dict], path: str, postfix: str) -> str:
    """Create route file for SUMO simulation.
    
    Args:
        trips: Trips DataFrame
        routes_dict: Dictionary mapping detector IDs to routes
        path: Output path
        postfix: Postfix for filename
        
    Returns:
        Path to created route file
    """
    def convert_row(row, routes_dict=detector_mappings["detector2route"], departPos="0", arrivalPos="max"):
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
def sumo_config(network_file: str, instant_induction_loop_add_file: str, trips: pd.DataFrame, path: str, postfix: str) -> str:
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
        <additional-files value="{instant_induction_loop_add_file}"/>
    </input>
    <output>
        <lanechange-output value="lanechange_output.xml"/>
        <summary-output value="summary_output_{postfix}.xml"/>
        <tripinfo-output value="tripinfo_output_{postfix}.xml"/>
        <fcd-output value="fcd_output_{postfix}.xml"/> 
        <fcd-output.geo value="true"/>
        <fcd-output.acceleration value="true"/> 
    </output>
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





def run_sumo(sumo_config: str, detector: str,detector_mappings: Dict[str, Dict], 
             maxspeed: float, trips: pd.DataFrame, pathout:str,postfix: str) -> str:

    # Start the SUMO simulation
    path = "data/sim_intermediate_data/"

    sumo_binary = "sumo"  # Use "sumo-gui" if you want to visualize the simulation
    traci.start([sumo_binary, "-c", sumo_config])
    traci.route.add(f"{detector}_route", detector_mappings["detector2route"][detector].split())
    logger.info("SUMO simulation is started.")
    for index, row in trips.iterrows():
            try:
                traci.vehicle.addFull(
                    vehID=row['id'],
                    routeID=f"{row['detector_id']}_route",
                    depart=row["depart"],
                    departPos="0",
                    departSpeed="max",
                    departLane=row["departLane"],
                    #speedFactor = 1.2
                )
                #traci.vehicle.setSpeedMode(row['id'], 95)
                row["departSpeed"] = row["speed_factor"]*maxspeed                
                traci.vehicle.setLaneChangeMode(row['id'], 0)
                
            except traci.TraCIException as e:
                print(f"Error adding vehicle {row['id']}:", e)
                traci.close()
                raise
            traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])
            traci.vehicle.setSpeed(row['id'], row["speed_factor"]*maxspeed)
            #traci.vehicle.setMaxSpeed(row["id"], row["speed_factor"] * maxspeed)

    #traci.simulation.saveState(f"{path}simulation_{postfix}_test.sumo.state")

    # Run the simulation step by step
    simulation_log = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        simtime = traci.simulation.getTime()-1
        for veh in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(veh)
                lon, lat = traci.simulation.convertGeo(x, y)
                #lon, lat = self.net.convertXY2LonLat(x, y)
                simulation_log.append({"time": simtime,
                                       "id":veh,
                                       "speedfactor": traci.vehicle.getSpeedFactor(veh),
                                       "x":round(lon,6),
                                       "y":round(lat,6),
                                       "angle":traci.vehicle.getAngle(veh),
                                       "speed":traci.vehicle.getSpeed(veh), 
                                       "acceleration":traci.vehicle.getAcceleration(veh),
                                       "pos":traci.vehicle.getLanePosition(veh),
                                       "lane":traci.vehicle.getLaneID(veh),
                                       "noise":traci.vehicle.getNoiseEmission(veh)})
                logger.info(simulation_log[-1])
                #traci.simulation.saveState(f"{path}simulation_{postfix}_test.sumo.state")
                #traci.simulation.loadState(f"{path}simulation_{postfix}_test.sumo.state")

                #for veh_id in traci.simulation.getDepartedIDList():
                #    traci.vehicle.setLaneChangeMode(veh_id, 0)
                #    traci.vehicle.setSpeedFactor(veh_id, veh2sf[veh_id])

                            
            # Close the simulation
    traci.close()
    logger.info("Simulation completed.")
    return  f"../../{pathout}instanceInductionLoop_{postfix}.xml"






