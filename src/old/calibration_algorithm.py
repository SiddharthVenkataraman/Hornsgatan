
import os



"""
# Calibration Algorithm for One Detector

This script calibrates vehicle departure times and speeds in a SUMO simulation
to match observed detector data. It iteratively adjusts each vehicle's
departure and speed until the simulated detector readings converge to the
measured values.

---

## Key Steps

1. **Load and preprocess detector data.**
2. **Initialize vehicle trips** with estimated depart times and speeds.
3. **Generate SUMO route and configuration files.**
4. **For each vehicle:**
    - Run SUMO simulation.
    - Adjust depart time and speed factor based on detector errors.
    - Repeat until convergence or max iterations.
5. **Save calibrated results.**

---

## Speed Units

- **All speeds are in meters per second (m/s).**

---

## Speed Factor

- The `speed_factor` is a multiplier applied to the vehicle’s maximum speed (`maxspeed`) in SUMO.
- The actual departure speed (`departSpeed`) is calculated as:  
  `departSpeed = speed_factor * maxspeed`
- **Range of speed factor in this algorithm:**  
  - **Minimum:** `0.9`  
  - **Maximum:** `3.0`
- **How it is updated:**
    - If the simulated speed at the detector is **too high** (`speed_error > 1`), the speed factor is **decreased** by `0.01`, but not below `0.9`.
    - If the simulated speed is **too low** (`speed_error < -0.5`), the speed factor is **increased** by `0.1`, but not above `3.0`.
- **Limitation:**  
  - SUMO may not handle `speed_factor` values less than 1.0 as expected, and very low values can cause unrealistic or unstable simulation behavior.
  - The calibration loop increases or decreases `speed_factor` to minimize the difference between simulated and real detector speeds.

---

## Iteration and Convergence Parameters

- **Maximum number of iterations per vehicle:**  
  - `iteration = 30` (configurable in the script)
- **Convergence conditions:**  
  - The calibration loop stops early if both of the following are satisfied:
    - `abs(time_error) <= 2` (the difference between simulated and real detector times is less than or equal to 2 seconds)
    - `abs(speed_error) <= 1` (the difference between simulated and real detector speeds is# Calibration Algorithm for One Detector

This script calibrates vehicle departure times and speeds in a SUMO simulation
to match observed detector data. It iteratively adjusts each vehicle's
departure and speed until the simulated detector readings converge to the
measured values.

---

## Key Steps

1. **Load and preprocess detector data.**
2. **Initialize vehicle trips** with estimated depart times and speeds.
3. **Generate SUMO route and configuration files.**
4. **For each vehicle:**
    - Run SUMO simulation.
    - Adjust depart time and speed factor based on detector errors.
    - Repeat until convergence or max iterations.
5. **Save calibrated results.**

---

## Speed Units

- **All speeds are in meters per second (m/s).**

---

## Speed Factor

- The `speed_factor` is a multiplier applied to the vehicle’s maximum speed (`maxspeed`) in SUMO.
- The actual departure speed (`departSpeed`) is calculated as:  
  `departSpeed = speed_factor * maxspeed`
- **Range of speed factor in this algorithm:**  
  - **Minimum:** `0.9`  
  - **Maximum:** `3.0`
- **How it is updated:**
    - If the simulated speed at the detector is **too high** (`speed_error > 1`), the speed factor is **decreased** by `0.01`, but not below `0.9`.
    - If the simulated speed is **too low** (`speed_error < -0.5`), the speed factor is **increased** by `0.1`, but not above `3.0`.
- **Limitation:**  
  - SUMO may not handle `speed_factor` values less than 1.0 as expected, and very low values can cause unrealistic or unstable simulation behavior.
  - The calibration loop increases or decreases `speed_factor` to minimize the difference between simulated and real detector speeds.

---

## Iteration and Convergence Parameters

- **Maximum number of iterations per vehicle:**  
  - `iteration = 30` (configurable in the script)
- **Convergence conditions:**  
  - The calibration loop stops early if both of the following are satisfied:
    - `abs(time_error) <= 2` (the difference between simulated and real detector times is less than or equal to 2 seconds)
    - `abs(speed_error) <= 1` (the difference between simulated and real detector speeds is
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET
import logging
import traci
import sumolib
from math import ceil

Hornsgatan_Home = "/home/kaveh/Hornsgatan/"
print("Current directory:", os.getcwd())
#os.chdir(Hornsgatan_Home)

# --- Parameters ---
date = '2020-01-01'
detector = 'w2e_in'
path = "data/calibration_intermediate_data/"
pathout = "data/calibration_data/"
pathin = "data/daily_splitted_data/"
iteration = 30

network_file = "data/map/Hornsgatan.net.xml"

if detector in ['e2w_out', 'e2w_in']:
    maxspeed = 8.33
else:
    maxspeed = 13.89


# --- Load and preprocess data ---
data = pd.read_csv(f'{pathin}data_{date}.csv')
data = data[data['detector_id'] == detector]
data.reset_index(drop=True, inplace=True)
data.reset_index(inplace=True)
data.rename(columns={"index": "id"}, inplace=True)
data["id"] = data["id"].apply(lambda x: f"{x}_{detector}")
data.sort_values(by=['time_detector_real'], inplace=True)
number = 10 #len(data)
df = data[["id", "detector_id", "time_detector_real", "speed_detector_real"]].head(number)
postfix = f"{detector}_{date}_{number}"

# --- Detector and route dictionaries ---
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

# Combine dictionaries into a DataFrame for easy access
dataframes = {
    "detector2from": pd.DataFrame.from_dict(detector2from, orient="index", columns=["from"]),
    "detector2lane": pd.DataFrame.from_dict(detector2lane, orient="index", columns=["lane"]),
    "detector2laneN": pd.DataFrame.from_dict(detector2laneN, orient="index", columns=["laneN"]),
    "detector2route": pd.DataFrame.from_dict(detector2route, orient="index", columns=["route"]),
    "detector2to": pd.DataFrame.from_dict(detector2to, orient="index", columns=["to"]),
}
combined_df = pd.concat(dataframes.values(), axis=1)

# --- Generate induction loop XML files ---
inductionLoop_filename_xml = f"inductionLoop_{postfix}.xml"
inductionLoop_filename_add = f"{path}inductionLoop_{postfix}.add.xml"
instantInductionLoop_filename_xml = f"instantInductionLoop_{postfix}.xml"
instantInductionLoop_filename_add = f"{path}instantInductionLoop_{postfix}.add.xml"

print(instantInductionLoop_filename_xml)

def write_instant_induction_loop_file():
    # Instant induction loop
    instant_induction_loops = [
        {"id": detector, "lane": detector2lane[detector], "pos": "1", "file": instantInductionLoop_filename_xml},
    ]
    root = ET.Element("additional")
    for loop in instant_induction_loops:
        ET.SubElement(root, "instantInductionLoop", loop)
    xml_string = ET.tostring(root, encoding="unicode").replace("<additional>", "<additional>\n").replace("/>", "/>\n")
    with open(instantInductionLoop_filename_add, "w") as file:
        file.write(xml_string)
    return xml_string

write_instant_induction_loop_file()

def write_induction_loop_file():
    # Standard induction loop
    induction_loops = [
        {"id": detector, "lane": detector2lane[detector], "pos": "1", "period": "1", "file": inductionLoop_filename_xml},
    ]
    root = ET.Element("additional")
    for loop in induction_loops:
        ET.SubElement(root, "inductionLoop", loop)
    xml_string = ET.tostring(root, encoding="unicode").replace("<additional>", "<additional>\n").replace("/>", "/>\n")
    with open(inductionLoop_filename_add, "w") as file:
        file.write(xml_string)
    return xml_string
       
xml_string = write_induction_loop_file() 


# --- Initialize trips ---
def trips_initializing(df, E2S_time=28, W2S_time=51):
    trips = df.copy()
    trips['depart'] = trips['time_detector_real'].copy()
    trips['depart'] = trips.apply(lambda row: row["time_detector_real"] - E2S_time if row['detector_id'][0] == 'e' else row["time_detector_real"] - W2S_time, axis=1)
    trips['from'] = trips['detector_id'].apply(lambda x: "24225358#0" if x[0] == 'e' else "151884975#0")
    trips['to'] = trips['detector_id'].apply(lambda x: "1243253622#0" if x[0] == 'e' else "151884974#0")
    trips['departLane'] = trips['detector_id'].apply(lambda x: "0" if x[-1] == 't' else "1")
    trips["departSpeed"] = 0
    trips["speed_detector_real"] = trips["speed_detector_real"].apply(lambda x: x / 3.6)
    trips.sort_values(by=["depart"], inplace=True)
    return trips

trips = trips_initializing(df)
trips.to_csv(f"{path}trips_{postfix}.csv", index=False)

# --- Generate SUMO route file ---
def route_creating(trips, routes_dict):
    def convert_row(row, routes_dict=routes_dict, departPos="0", arrivalPos="max"):
        return (
            f'\n<vehicle id="{row.id}" depart="{row.depart}" departLane="{row.departLane}" '
            f'departSpeed="{row.departSpeed}" departPos="{departPos}" arrivalPos="{arrivalPos}">'
            f'\n    <route edges="{routes_dict[row.detector_id]}"/>\n</vehicle>'
        )
    routes = trips.copy()
    text0 = '<?xml version="1.0" encoding="UTF-8"?>\n\n\n'
    text1 = '<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">'
    text2 = ''.join(routes.apply(convert_row, axis=1))
    text3 = '\n</routes>'
    with open(f"{path}routes_{postfix}.xml", 'w') as myfile:
        myfile.write(text0 + text1 + text2 + text3)

route_creating(trips, combined_df["route"].to_dict())

# --- Generate SUMO configuration file ---
route_file_name = f"{path}routes_{postfix}.xml"
trips_file_name = f"{path}trips_{postfix}.csv"
start_time = trips["depart"].min()

inductionLoop_filename_add = f"inductionLoop_{postfix}.add.xml"

additional_file = inductionLoop_filename_add
#additional_file_2 = f"instantInductionLoop_{postfix}.add.xml"
config_file_name = f"{path}simulation_{postfix}.sumo.cfg"

config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="../../{network_file}"/>
        <additional-files value="{additional_file}"/>
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

print(f"Configuration file '{config_file_name}' created successfully.")

# --- Main calibration loop ---
# To improve speed, you can comment out or remove the logging lines below.
# If you want to keep only error logs, adjust the logging level accordingly.

# Configure logging (comment out to improve speed)
logfile_name = f"log/simulation_{postfix}.log"
logging.basicConfig(
    filename=logfile_name,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Simulation started.")

trips["departSpeed"] = maxspeed
trips["speed_factor"] = 1
sumo_binary = "sumo"

if traci.isLoaded():
    traci.close()
traci.start([sumo_binary, "-c", config_file_name, "--begin", str(trips["depart"][0])])#, "--threads", "1"])
traci.route.add(f"{detector}_route", combined_df.loc[detector]["route"].split())
traci.simulation.saveState(f"{path}simulation_{postfix}_next.sumo.state")
traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")

#lasttrips = []
mylog = []
step = 0

for index, row in trips.iterrows():
    traci.simulation.loadState(f"{path}simulation_{postfix}_next.sumo.state")
    traci.simulation.saveState(f"{path}simulation_{postfix}.sumo.state")

    # Logging can be commented out for speed
    logging.info(f"Processing vehicle ID: {row['id']}")
    #logging.info(f"Initial depart: {row['depart']}, departSpeed: {row['departSpeed']}, speed_factor: {row['speed_factor']}")
    row_dict = row.to_dict()
    #logging.info(f"Row data: {row_dict}")

    step += 1
    time_error = 10
    speed_error = 10
    count = 0
    speed_factor = 1
    prow = row.copy()

    while (count < iteration) and ((abs(time_error) > 2) or abs(speed_error) > 1):
        try:
            traci.simulation.loadState(f"{path}simulation_{postfix}.sumo.state")
        except traci.FatalTraCIError as e:
            print("Error loading simulation state:", e)
            logging.error(f"Error loading simulation state: {e}")
            traci.close()
            raise

        count += 1

        # Remove the vehicle if it exists
        if row['id'] in traci.vehicle.getIDList():
            traci.vehicle.remove(row['id'])

        # Adjust depart time for consecutive vehicles
        if len(mylog) > 0 and count == 1:
            row["depart"] = mylog[-1]["depart"] + (row["time_detector_real"] - mylog[-1]["time_detector_real"])

        #logging.info(f"Updated depart: {row['depart']}, departSpeed: {row['departSpeed']}, speed_factor: {row['speed_factor']}")

        try:
            traci.vehicle.addFull(
                vehID=row['id'],
                routeID=f"{row['detector_id']}_route",
                depart=row["depart"],
                departPos="0",
                departSpeed="max",    #change o to max
                departLane=row["departLane"],
            )
            traci.vehicle.setSpeedMode(row['id'], 95)
            traci.vehicle.setSpeed(row['id'], row["speed_factor"] * maxspeed)
            row["departSpeed"] = row["speed_factor"] * maxspeed
            traci.vehicle.setLaneChangeMode(row['id'], 0)
        except traci.TraCIException as e:
            print(f"Error adding vehicle {row['id']}:", e)
            logging.error(f"Error adding vehicle {row['id']}: {e}")
            traci.close()
            raise

        traci.vehicle.setSpeedFactor(row["id"], row["speed_factor"])
        #logging.info(f"start iteration in time {traci.simulation.getTime()}")

        while traci.simulation.getMinExpectedNumber() > 0:
            if traci.simulation.getTime() == int(row["depart"]) + 1:
                #logging.info(f" In time {traci.simulation.getTime()} added simulation_{postfix}_next.sumo.state")
                traci.vehicle.setSpeed(row["id"], row["departSpeed"])
                traci.vehicle.setLaneChangeMode(row["id"], 0)
                traci.simulation.saveState(f"simulation_{postfix}_next.sumo.state")
            traci.simulationStep()

            for veh_id in traci.simulation.getDepartedIDList():
                traci.vehicle.setLaneChangeMode(veh_id, 0)
            vehicles = traci.inductionloop.getLastStepVehicleIDs(detector)
            #if vehicles and vehicles[0] != row["id"] and row['id'] == "3e2w_out":
            #    logging.info(vehicles, row["id"])
            #    print(vehicles, row["id"])
            if vehicles and vehicles[0] == row["id"]:
                veh_id, veh_length, entry_time, exit_time, vType = traci.inductionloop.getVehicleData(detector)[0]
                speed = traci.inductionloop.getLastStepMeanSpeed(detector)
                time = round(entry_time - 1, 2)
                #print(f"veh_id: {veh_id} | Time: {time} s  | Speed: {speed:.2f} m/s")
                #logging.info(f"traci_time: {traci.simulation.getTime()} | veh_id: {veh_id} | Time: {time} s  | Speed: {speed:.2f} m/s")
                # Calculate the time and speed errors
                time_error = time - row["time_detector_real"]
                speed_error = speed - row["speed_detector_real"]
                #print("depart: ", row["depart"], "departSpeed: ",
                #      row["departSpeed"], "speed_factor: ", row["speed_factor"], "time_error : ", time_error,
                #      "speed_error : ", speed_error)
                #logging.info(f"depart: {row['depart']}, departSpeed: {row['departSpeed']}, speed_factor: {row['speed_factor']}, time_error: {time_error}, speed_error: {speed_error}")

                prow = row.copy()
                row["depart"] = row["depart"] - (time - row["time_detector_real"])
                if len(mylog) > 0 and row["depart"] <= mylog[-1]["depart"]:
                    row["depart"] = mylog[-1]["depart"] + 1

                if speed_error > 0 and speed_error > 1:
                    row["speed_factor"] = max(.9, row["speed_factor"] - 0.01)
                if speed_error <= 0 and speed_error < -.5:
                    row["speed_factor"] = min(3, row["speed_factor"] + 0.1)

                row["departSpeed"] = maxspeed
                if row['speed_factor'] < 1:
                    row["departSpeed"] = maxspeed * row["speed_factor"]
                if row['speed_factor'] > 1:
                    row["departSpeed"] = maxspeed * row["speed_factor"]

                #print("next depart: ", row["depart"], "next SPEED factor: ", row["speed_factor"])
                #logging.info(f"next depart: {row['depart']}, next SPEED factor: {row['speed_factor']}")
                break

    # Save the calibrated values back to the DataFrame
    #lasttrips.append(row)
    mylog.append({
        "veh_id": prow["id"],
        "time_detector_sim": time,
        "speed_detector_sim": speed,
        "speed_factor": prow["speed_factor"],
        "time_detector_real": prow["time_detector_real"],
        "depart": prow["depart"],
        "departSpeed": prow["departSpeed"],
        "speed_detector_real": prow["speed_detector_real"]
    })

if traci.isLoaded():
    traci.close()

# --- Save results ---
#df = pd.DataFrame(lasttrips)
#df.to_csv(f"{path}calibrated_trips_{postfix}.csv", index=False)

log_df = pd.DataFrame(mylog)
log_df["delta_time"] = log_df["time_detector_sim"] - log_df["time_detector_real"]
log_df["delta_speed"] = log_df["speed_detector_sim"] - log_df["speed_detector_real"]
log_df.to_csv(f"{pathout}calibrated_data_{postfix}.csv", index=False)

#print("Calibration complete. Results saved.")

# --- Note on Logging ---
# To improve running speed, you may comment out or remove the logging configuration and all logging.info/logging.error calls above.
# This will reduce disk I/O and speed up the calibration loop.