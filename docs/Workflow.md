# Hornsgatan Traffic Simulation and Calibration Project Workflows

This document outlines the project's data processing and simulation workflows.

---

## High-Level Project Workflow

Overview of the main stages in the Hornsgatan traffic simulation and calibration project.

The project uses a modular Hamilton pipeline with these main steps:

1.  **Data Ingestion & Preprocessing:** Import and process real detector data for simulation and calibration.
2.  **Calibration:** Calibrate vehicle parameters against real data using Bayesian optimization (scikit-optimize) to minimize simulation-to-real data difference.
3.  **Traffic Simulation:** Run SUMO scenarios to produce traffic flow data.
4.  **Analysis & Export:** Analyze and export simulation and calibration results.

Each stage is a Hamilton dataflow, triggered via `main.py`.

Available pipelines:

-   `import_data`: Data ingestion and preparation.
-   `calib`: Calibration process.
-   `sim`: Traffic simulation.

Hamilton manages step dependencies for a clear and maintainable workflow. 

---

## High-Level Dataflow Diagram

```mermaid
graph TD
    A[Real Detector Data] --> B["Data Ingestion and Preprocessing"]
    B --> C["Split Data for one Day and one Detector"]
    C --> E["Calibrated Vehicle Depart Time/Speed Factor (Traci + Optimizer)"]
    C --> F[SUMO Traffic Simulator]
    E --> F
    F --> G["FCD Output (floating car data)"]
    E --> H["Analysis & Results Export"]
    G --> H
    H --> I[Results]

    %% Styling for clarity
    classDef data fill:#4682B4,stroke:#333,stroke-width:2px;
    class A,G,I data
    classDef process fill:#2E8B57,stroke:#333,stroke-width:2px;
    class B,C,E,H process
    classDef tool fill:#DAA520,stroke:#333,stroke-width:2px;
    class F tool
    classDef param fill:#8A2BE2,stroke:#333,stroke-width:2px;
    class E param
```

---

## Low-Level Calibration Workflow

Detailed workflow of the calibration process, finding optimal vehicle parameters by iteratively using real data, SUMO via TraCI, and skopt.

```mermaid
graph TD
    A["Split Data for one Day and one Detector"] --> B("Iterate Through Data Entries/Vehicles")
    B --> C{"For Each Data Entry:"}
    C --> D["Initial/Current Vehicle Parameters"]
    C --> E("Initialize Optimizer (skopt)")
    E --> F{"For N Optimization Iterations:"}
    F --> G("Optimizer Proposes Parameters")
    G --> H["Suggested Parameters (Depart Time, Speed Factor)"]
    H --> I("Run SUMO Simulation (via TraCI)")
    I --> J["Simulated Detector Data / FCD Output"]
    J --> K("Calculate Simulation Cost/Error")
    K --> L["Simulation Cost/Error Value"]
    L --> M("Optimizer Updates with Result")
    M --> F
    F -- All Iterations Complete --> N["Best Found Parameters for Entry"]
    N --> O("Collect Calibrated Results")
    O --> B
    B -- All Entries Processed --> P["All Calibrated Data Output"]

    %% Styling
    classDef data fill:#4682B4,stroke:#333,stroke-width:2px;
    class A,D,H,J,L,N,P data
    classDef process fill:#2E8B57,stroke:#333,stroke-width:2px;
    class B,C,E,F,G,I,K,M,O process
```


---

### Explanations:

*   **Simulation Cost/Error:**
Metric quantifying how well simulation output (with suggested parameters) matches real data for an entry. A numerical value minimized by the optimizer. Lower = better match.
Cost function formula:

$$(t_{sim} - t_{real})^2 + (v_{sim} - v_{real})^2$$

*   **Calibration Iterations & Best Parameters:**
Skopt optimizer runs for fixed iterations (`iteration`) per entry. It proposes parameters to minimize cost. After iterations, the parameters with the lowest cost found are the **Best Found Parameters for Entry**.
    Where:
    -    $t_{sim}$, $v_{sim}$: simulated detection time/speed.
    *   $t_{real}$, $v_{real}$: real observed time/speed.
    *   $f_{speed}$, $t_{depart}$: vehicle speed factor/depart time parameters calibrated.
    *   $f_{speed}^{min/max}$, $t_{depart}^{min/max}$: parameter bounds.

*   **Suggested Parameters (Depart Time, Speed Factor):**
Values proposed by the optimizer in an iteration, aiming for lower costs based on Bayesian optimization.

*   **Optimizer Updates:** Suggested parameters and their cost are fed back to the optimizer. This update refines its model for better future suggestions.
