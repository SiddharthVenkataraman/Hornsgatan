# SUMO vs. TraCI: A Traffic Simulation Overview

## What is SUMO?

**SUMO (Simulation of Urban MObility)** is a microscopic traffic simulation engine that simulates detailed traffic behavior over a road network using predefined inputs.

### Key Features:

- Microscopic traffic simulation  
- Supports vehicles, pedestrians, traffic lights  
- Reads static input files (routes, trips, network)  
- Produces traffic output like vehicle positions, speeds, and emissions  

---

## What is TraCI?

**TraCI (Traffic Control Interface)** is an API that allows you to control a SUMO simulation in real time from an external program (e.g., Python).

### Key Features:

- Step-by-step simulation control  
- Add/remove/change vehicles dynamically  
- Adjust traffic light phases programmatically  
- Access and manipulate simulation data in real time  
- Save/load simulation state  

---

## SUMO vs. TraCI

| Feature       | **SUMO**                 | **TraCI**                               |
| ------------- | ------------------------ | --------------------------------------- |
| Type          | Simulation engine        | Real-time control interface (API)       |
| Input         | Static files             | Dynamic commands from external programs |
| Interactivity | ❌ Not interactive        | ✅ Interactive (step-by-step control)    |
| Use Case      | Full scenario simulation | Adaptive control, optimization, RL      |
| Output        | Based on setup files     | Real-time data and custom behaviors     |

## Analogy

> **SUMO** is like a traffic simulation game that plays itself.  
>  
> **TraCI** is the controller that lets you pause the game, insert new cars, reroute traffic, or change traffic light rules while the game is running.  

---

## Why Use TraCI?

- Enables dynamic simulation scenarios  
- Essential for calibration, optimization, and AI training  
- Allows vehicle-level and real-time decision making  
- Supports experiments with live sensor data or adaptive algorithms  

---

## What You Can Do with TraCI

### 🚗 Vehicle Control

```python
traci.vehicle.getSpeed(vehID)                  # Get current speed
traci.vehicle.getPosition(vehID)               # Get location (x, y)
traci.vehicle.getSpeedFactor(vehID)            # Get speed factor
traci.vehicle.setSpeed(vehID, speed)           # Set specific speed
traci.vehicle.setSpeedFactor(vehID, factor)    # Set speed factor
traci.vehicle.changeLane(vehID,                # Change lane
                         laneIndex,
                         duration)             
traci.vehicle.getLaneID(vehID)                 # Get current lane
traci.vehicle.getRoadID(vehID)                 # Get current road
traci.vehicle.setRoute(vehID, edgeList)        # Set a custom route
traci.vehicle.remove(vehID)                    # Remove vehicle
traci.vehicle.setColor(vehID, (r, g, b, a))    # Set vehicle color
traci.vehicle.add(vehID, routeID)              # Add a vehicle to the simulation

traci.vehicle.addFull(vehID, routeID,          #Add a vehicle with detailed parameters
                      typeID, depart,
                      departLane, departPos,
                      departSpeed)              
```


### 📟 Detector Data

```python
traci.inductionloop.getLastStepVehicleNumber(detectorID)   # Vehicle count
traci.inductionloop.getLastStepMeanSpeed(detectorID)       # Avg speed
traci.inductionloop.getLastStepVehicleIDs(detectorID)      # Vehicle IDs
traci.inductionloop.getLastStepOccupancy(detectorID)       # Occupancy
```

### 🕹️ Simulation Control

```python
traci.simulationStep()                              # Advance simulation step  
traci.simulation.getTime()                          # Current simulation time  
traci.simulation.getMinExpectedNumber()             # Remaining vehicles  
traci.load(["-c", "config.sumocfg"])                # Load new simulation  
traci.simulation.saveState("state.xml")             # Save current state  
traci.simulation.loadState("state.xml")             # Load saved state  

```

### 🚦 Traffic Light Control

```python
traci.trafficlight.getRedYellowGreenState(tlsID)        # Get light state
traci.trafficlight.setRedYellowGreenState(tlsID, state) # Set light state
traci.trafficlight.getPhase(tlsID)                      # Get phase index
traci.trafficlight.setPhase(tlsID, phaseIndex)          # Set specific phase
```

---

## References

- Official TraCI API documentation: [https://sumo.dlr.de/docs/TraCI/](https://sumo.dlr.de/docs/TraCI/)
- SUMO Traffic Simulator: [https://sumo.dlr.de/](https://sumo.dlr.de/)

