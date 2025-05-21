# Hornsgatan Traffic Simulation & Calibration Pipeline

This project provides a modular, data-driven pipeline for simulating and calibrating traffic on Hornsgatan (Stockholm) using the SUMO traffic simulator and the Hamilton pipeline framework. The system ingests real detector data, generates simulation scenarios, and calibrates vehicle parameters to match observed traffic patterns.

## Features

- **Microscopic traffic simulation** using SUMO and TraCI
- **Modular pipeline** with [Hamilton](https://github.com/dagworks-inc/hamilton)
- **Bayesian optimization** for calibration ([scikit-optimize](https://scikit-optimize.github.io/))
- **Flexible data ingestion** and preprocessing
- **Exportable results** for further analysis

## Project Structure

```
Hornsgatan/
├── config/         # YAML configuration files for pipelines
│   ├── calib_discrete_example.yaml
│   ├── calib_example.yaml
│   ├── import_data_example.yaml
│   └── sim_example.yaml
├── data/           # Input data and network files
├── diagram/        # Visual diagrams and plots
├── notebook/       # Jupyter notebooks for analysis
├── src/            # Source code (simulation, calibration, pipeline)
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- [SUMO](https://sumo.dlr.de/docs/Installing/index.html) installed and in your PATH

### Setting the Project Root Environment Variable

For convenience, set the project root as an environment variable:

**Temporarily (for current shell/session):**
```bash
export HORNSGATAN_HOME="/path/to/your/Hornsgatan"
```

**Permanently (for all new shells):**
Add the above line to your `~/.bashrc` or `~/.zshrc` and run:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

You can then use this variable in your Python scripts or notebooks:
```python
import os
project_root = os.environ["HORNSGATAN_HOME"]
```

Or expand it in file paths:
```python
import os
path = os.path.expandvars("${HORNSGATAN_HOME}/data/myfile.csv")
```

### Installation

```bash
git clone <your-repo-url>
cd Hornsgatan
pip install -r requirements.txt
```

Set SUMO environment variables if needed:
```bash
export SUMO_HOME="/path/to/sumo"
export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"
```

### Usage

#### Running Pipelines

You can run any pipeline from the project root using the `main.py` dispatcher and the `--pipeline` argument. Available pipelines are:
- `import_data`
- `calib_discrete`
- `calib`
- `sim`
- `my_driver` (demonstration pipeline)

You can run the pipelines in two ways:

**1. As a script:**
```bash
python main.py --pipeline import_data
python main.py --pipeline calib_discrete
python main.py --pipeline calib
python main.py --pipeline sim
python main.py --pipeline my_driver
```

**2. As a module:**
```bash
python -m main --pipeline import_data
python -m main --pipeline calib_discrete
python -m main --pipeline calib
python -m main --pipeline sim
python -m main --pipeline my_driver
```

Both approaches are supported and will work the same way.

**Specifying a Configuration File**

You can specify a YAML configuration file for any pipeline using the `--config` argument. Example:

```bash
python main.py --pipeline calib_discrete --config config/calib_discrete_example.yaml
python main.py --pipeline sim --config config/sim_example.yaml
python main.py --pipeline import_data --config config/import_data_example.yaml
python main.py --pipeline calib --config config/calib_example.yaml
```

If you omit `--config`, the pipeline will use its default configuration.

**Enabling Experiment Tracking**

You can enable Hamilton experiment tracking for any pipeline by adding the `--tracker` flag:

```bash
python main.py --pipeline calib_discrete --tracker
python main.py --pipeline import_data --tracker
python main.py --pipeline sim --tracker
python main.py --pipeline calib --tracker
```

If you omit `--tracker`, the pipeline will run without experiment tracking (faster, less metadata).

This approach allows you to flexibly select and run any pipeline from a single entry point, with custom configuration and optional tracking.

**Logging**

- All pipeline runs generate logs in the `logs/` directory (created automatically).
- Log files are named according to the pipeline and configuration (e.g., `pipeline_calib_discrete_2020-01-02.log`).
- Logs include timestamps, log levels, and messages from both the console and file.
- You can control the verbosity with the `--log-level` argument:
  - `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`
- Example:
  ```bash
  python main.py --pipeline calib_discrete --log-level DEBUG
  ```

## Calibration Methodology

The pipeline uses Bayesian optimization to calibrate vehicle departure times and speed factors, minimizing the error between simulated and real detector data. The process is modular and extensible via Hamilton.

## Contributing

Pull requests and issues are welcome!

## License

MIT License

---

For more information on SUMO and traffic simulation, visit the [SUMO Documentation](https://sumo.dlr.de/docs/index.html).