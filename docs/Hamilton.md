# Hamilton Usage in Hornsgatan Project

This document explains how the [Hamilton](https://github.com/dagworks-inc/hamilton) library is used to structure and run the dataflows within the Hornsgatan traffic simulation and calibration project.

## What is Hamilton and Why Use It?

Hamilton is a micro-orchestration library for building dataflows.

**Why is it important?**

Hamilton promotes building data pipelines using modular, testable Python functions. By defining dependencies through function signatures, it creates an explicit and visualizable Directed Acyclic Graph (DAG) of your data transformation logic. This approach offers several key benefits:

- **Improved Readability:** Dataflows are defined by code, not configuration, making them easier to understand.
- **Enhanced Testability:** Individual functions can be easily unit tested.
- **Increased Reusability:** Functions can be reused across different dataflows.
- **Simplified Debugging:** The DAG structure helps pinpoint where issues occur.
- **Better Maintainability:** Changes to one part of the dataflow have clearly defined impacts.

Hamilton helps move away from imperative scripting towards a more declarative, functional style for data processing.

## General Hamilton Implementation Concepts

Implementing Hamilton typically involves:

1.  **Defining Functions:** Writing Python functions where the function name is the name of the output data artifact and the function arguments are the required input data artifacts.
2.  **Creating a Driver:** Instantiating a `hamilton.driver.Driver` object, providing it with the modules containing your functions.
3.  **Running the Driver:** Calling the `execute()` method on the Driver, specifying the desired output data artifacts.
4.  **Configuration:** Providing configuration to the Driver, which can influence how functions are executed or provide necessary parameters.

Hamilton automatically determines the execution order based on the function dependencies.

## Hamilton in this Project

In the Hornsgatan project, Hamilton is used to define and manage the various data processing steps involved in importing data, running simulations, and performing calibration.

The dataflow logic is primarily defined within the `src/` directory. Each function in a Hamilton module represents a step in the dataflow, and its inputs are determined by its function signature.

## Running Hamilton Pipelines

The project uses `main.py` as the central dispatcher to run different Hamilton pipelines. You can specify which pipeline to run (`import_data`, `calib`, or `sim`) and provide a specific configuration file.

For example, to run the simulation pipeline with a specific configuration:

```bash
python main.py --pipeline sim --config config/sim_example.yaml
```

The `--tracker` flag can be added to enable Hamilton experiment tracking.

Configuration for the Hamilton drivers is managed through YAML files located in the `config/` directory.

## Dataflow Structure

The Hamilton dataflows are designed to be modular. Key aspects include:

- **Functions:** Each step is a Python function.
- **Dependencies:** Dependencies between steps are inferred from function signatures.
- **Drivers:** Hamilton Drivers orchestrate the execution of the functions based on the requested outputs.
- **Config:** Configuration files in `config/` provide parameters to the Hamilton runs.

Refer to the code within the `src/` directory to see the specific Hamilton modules and functions that define the dataflows.

## Further Information

- For details on setting up the project and running the main entry point, see the main [README.md](../README.md).
- For specific details on the calibration pipeline, see the [pipeline/README.md](../../src/pipeline/README.md). (Note: Adjust path if needed based on actual structure)
- Visit the [Hamilton documentation](https://docs.dagworks.io/) for more general information on using Hamilton.

### Official Hamilton Resources

- **Hamilton Documentation:** The official documentation is the best place to find detailed information, guides, and API references. [https://docs.dagworks.io/](https://docs.dagworks.io/)
- **Hamilton GitHub Repository:** Explore the source code, contribute, and file issues. [https://github.com/dagworks-inc/hamilton](https://github.com/dagworks-inc/hamilton)
- **DAGWorks Website:** Learn more about Hamilton and related tools from the creators. [https://dagworks.io/](https://dagworks.io/) 