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

1. Place your detector data and network files in the `data/` directory.
2. Run the main pipeline (example):
   ```bash
   python src/main.py
   ```
3. Analyze results using the notebooks in `notebook/`.

## Calibration Methodology

The pipeline uses Bayesian optimization to calibrate vehicle departure times and speed factors, minimizing the error between simulated and real detector data. The process is modular and extensible via Hamilton.

## Contributing

Pull requests and issues are welcome!

## License

MIT License

---

For more information on SUMO and traffic simulation, visit the [SUMO Documentation](https://sumo.dlr.de/docs/index.html).