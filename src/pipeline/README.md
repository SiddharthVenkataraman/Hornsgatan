# Hornsgatan Traffic Simulation Calibration Pipeline

This module provides a vehicle-level calibration pipeline for SUMO-based traffic simulation, ensuring that simulated vehicle behavior closely matches real-world detector data.

## Overview

The calibration process adjusts each vehicle's simulated departure time and speed factor so that the simulation output aligns with observed detector measurements. The process is automated and data-driven, leveraging Bayesian optimization for efficient parameter search.

## Calibration Algorithm

**Input:**  
- Preprocessed vehicle trip data  
- Detector mappings  
- SUMO network and configuration files

**Output:**  
- Calibrated parameters for each vehicle  
- CSV file with calibration results

### Steps

1. **Initialize the SUMO simulation** and save the initial state.

2. **For each vehicle:**
   - **Set up the Bayesian optimizer:**
     - **Parameter bounds:**
       - *Departure time*: Integer range, from a minimum (based on previous vehicle or earliest possible) to a maximum (close to the real detector time).
       - *Speed factor*: Discretized by multiplying the continuous range (e.g., 0.6 to 3.2) by 20, so the optimizer works over integer steps (e.g., 12 to 64).
     - The optimizer proposes new parameter values at each iteration.
   - **Iterative optimization:**
     - For a fixed number of iterations:
       - Convert the proposed speed factor integer back to a float by dividing by 20.
       - Load the saved simulation state.
       - Add the vehicle with the proposed parameters.
       - Run the simulation until the vehicle passes the detector.
       - Measure the error between simulated and real detector data.
       - Update the optimizer with the error.
   - **Select the best parameters** (lowest error) and save the simulation state for the next vehicle.

3. **Save the calibrated results** for all vehicles to a CSV file.

## Key Features

- **Bayesian Optimization:** Efficiently searches for optimal parameters for each vehicle.
- **Parameter Discretization:** Speed factor is discretized for optimization, but applied as a continuous value in simulation.
- **State Management:** Simulation state is saved and restored to ensure efficient, repeatable calibration for each vehicle.
- **Result Logging:** All calibration results are saved for further analysis.

## Usage

1. Prepare your input data and detector mappings.
2. Run the calibration pipeline as described in your main script or notebook.
3. Find the calibrated results in the specified output CSV file.

## File Structure

- `features_calib.py` — Main calibration logic and algorithm implementation.
- (Other pipeline files as needed.)

---

**For more details, see the function docstrings in `features_calib.py`.** 