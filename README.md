# Hornsgatan: SUMO-based Microsimulation and Traffic Calibration

This project offers a detailed traffic microsimulation and calibration framework for Hornsgatan, a prominent street in Stockholm, Sweden. Utilizing the Simulation of Urban MObility (SUMO) platform, it integrates real-world traffic data to model, simulate, and calibrate traffic flows, aiming to replicate realistic urban traffic conditions.

## Overview

- **Simulation Engine**: [SUMO](https://sumo.dlr.de/docs/index.html)
- **Calibration Method**: SUMO's built-in calibrator with TraCI interface
- **Data Sources**: Real-world traffic counts and network topology
- **Key Features**:
  - Microscopic traffic simulation
  - Dynamic calibration using TraCI
  - Visualization of traffic patterns and calibration results

## Project Structure

```
Hornsgatan/
├── data/
│   ├── demand.csv             # Traffic demand data
│   └── map/
│       └── Hornsgatan.net.xml # Network topology file
├── diagram/                   # Visual diagrams and plots
├── notebook/                  # Jupyter notebooks for analysis
├── src/                       # Source code for simulation and calibration
├── .gitignore                 # Git ignore file
└── requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [SUMO](https://sumo.dlr.de/docs/Installing/index.html) installed and added to your system's PATH

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Khoshkhah/Hornsgatan.git
   cd Hornsgatan
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up SUMO environment variables** (if not already set):

   ```bash
   export SUMO_HOME="/path/to/sumo"
   export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"
   ```

## Usage

### Running the Simulation

1. **Prepare the network and demand files**:

   Ensure that `Hornsgatan.net.xml` and `demand.csv` are correctly placed in the `data/map/` and `data/` directories, respectively.

2. **Execute the main simulation script**:

   ```bash
   python src/main.py
   ```

   This script initializes the SUMO simulation, applies the calibration using TraCI, and generates output files for analysis.

### Analyzing Results

Use the Jupyter notebooks in the `notebook/` directory to visualize and analyze the simulation and calibration results. These notebooks provide insights into traffic flow patterns, calibration accuracy, and other key metrics.

## Calibration Methodology

The project employs SUMO's calibrator in conjunction with the TraCI (Traffic Control Interface) to dynamically adjust traffic flows during the simulation. This approach ensures that the simulated traffic volumes align closely with observed real-world data. For more details on the calibrator, refer to the [SUMO Calibrator Documentation](https://sumo.dlr.de/docs/Simulation/Calibrator.html).

## Contributing

Contributions are welcome! If you have suggestions for improvements or encounter issues, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more information on SUMO and traffic simulation, visit the [SUMO Documentation](https://sumo.dlr.de/docs/index.html).