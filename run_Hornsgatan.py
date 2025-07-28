import os
import sys
import argparse
import yaml
import subprocess
import shutil

""" Script to run the pipelines in Hornsgatan

Command:
    - Running:
    - - simulation named "TEST",
    - - over all three pipelines, one after the other (import_data -> calib -> sim),
    - - for ALL vehicles,
    - - using parameters in "config/config-TEST.yaml"
    python run_Hornsgatan.py --config config/config-TEST.yaml --simulation_name TEST --init_number 0 --verbose
    
    - - for the first 1000 vehicles
    python run_Hornsgatan.py --config config/config-TEST.yaml --simulation_name TEST --init_number 1000 --verbose
    
    - - Running only a single pipelines
    python run_Hornsgatan.py --config config/config-TEST.yaml --simulation_name TEST --init_number 1000 --verbose --only_run_import_data (or --only_run_calib or --only_run_sim)

Prerequisites:
    1. Ensure required timestamps are in folder "config['hornsgatan_home']/data/raw_data" with format "timestamps-TEST.csv"
    2. Ensure the config "config-TEST.yaml" has the following entries:
    3. Ensure the required conda environment is activated. E.g. "GeometricPaper3SUMO"
    4. Ensure file "config.ini" is found with path "config['hornsgatan_home']/config/config.ini"
        This file config.ini can have a template as follows:
            <START>
            [Hamilton]
            project_id = 'Test'
            [Database]
            db_name = 'db_name'
            db_host = 'db_host'
            db_port = 'db_port'
            <EOF>

Example of a config.yaml
    minimumLenData: 10000  # Minimum number of vehicles PER DAY in the .csv file, else the day is skipped 
    hornsgatan_home: "/home/siddharth/GitHub/Hornsgatan"  # Home directory for "Hornsgatan" repository
    hornsgatan_input: "/home/siddharth/GitHub/input/Hornsgatan"  # Directory to store the generated config files before the script calls the pipelines 
    detector_list:  "['w2e_out', 'w2e_in', 'e2w_out', 'e2w_in']"  # "['w2e_out']"  # Detectors to iterate over when calling pipelines calib and sim
    date: "2020-01-02"  # Date to consider. Calib and sim are run with only data from this date. Other dates, if provided in input timestamps, are ignored.
    no_speed: false  # If "true", skips using speed in calibration, if "false", uses deviation in measured and simulated of both speed and time 
    calib_with_fcd: "True"  # If "True", calib pipeline outputs an fcd at the end. If "False", fcd is not produced. Fcd in calib may be useful for comparing with fcd from sim

"""


def run_command_on_bash(command, cwd, verbose):
    """
    Run a command on a bash shell, with settings
    """
    if verbose:
        subprocess.run(command,
                       cwd=cwd,
                       shell=True,
                       text=True)

    else:
        result = subprocess.run(command,
                                cwd=cwd,
                                shell=True,
                                capture_output=True,
                                text=True)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"Error running {command}")
        print(result.stdout)

    return 0


def create_yaml_file(data, path_to_file):
    """
    Create a YAML file from a data dictionary
    Args:
        data:
        path_to_file:

    Returns:

    """
    yaml.dump(data, open(path_to_file, "w"))

    return 0


def move_all_files_from_folder_to_folder(folder_from, folder_to):
    """
    Move ALL files from folder_from to folder_to
    """
    if not os.path.exists(folder_to):
        os.makedirs(folder_to)

    for cur_file in os.listdir(folder_from):
        if os.path.isfile(os.path.join(folder_from, cur_file)) and cur_file[0] != '.':
            shutil.move(os.path.join(folder_from, cur_file), os.path.join(folder_to, cur_file))

    return 0


def delete_all_files_in_folder(folder):
    """
    Delete ALL files from folder
    """
    for cur_file in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, cur_file)) and cur_file[0] != '.':
            os.remove(os.path.join(folder, cur_file))

    return 0


def main():
    parser = argparse.ArgumentParser(description="Running Hornsgatan")
    parser.add_argument('--simulation_name', help='Name of folder to store simulation', required=True)
    parser.add_argument('--config', type=str, help='Path to YAML config file', required=True)
    parser.add_argument('--init_number', help='init_number to use for simulations. If 0, use all vehicles', required=True)

    parser.add_argument('--only_run_import_data', action='store_true', help='Run only import_data pipeline')
    parser.add_argument('--only_run_calib', action='store_true', help='Run only calib pipeline')
    parser.add_argument('--only_run_sim', action='store_true', help='Run only sim pipeline')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args, _ = parser.parse_known_args()

    simulation_name = args.simulation_name
    init_number = eval(args.init_number)

    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        raise Exception("No config file specified")

    hornsgatan_home = config['hornsgatan_home']
    hornsgatan_input = config['hornsgatan_input']
    hornsgatan_config = os.path.join(hornsgatan_input, 'config')
    detector_list = eval(config['detector_list'])
    date = config['date']
    no_speed = config['no_speed']
    calib_with_fcd = eval(config['calib_with_fcd'])

    only_run_import_data = args.only_run_import_data
    only_run_calib = args.only_run_calib
    only_run_sim = args.only_run_sim

    verbose = args.verbose

    if not os.path.exists(hornsgatan_config):
        os.makedirs(hornsgatan_config)

    path_to_timestamps = os.path.join(hornsgatan_home, 'data', 'raw_data', f"timestamps-{simulation_name}.csv")
    if not os.path.exists(path_to_timestamps):
        raise Exception(f"Missing timestamps file with name {f'timestamps-{simulation_name}.csv'} at {path_to_timestamps}!")

    if not (only_run_calib or only_run_sim):

        ##########
        # A) --pipeline import_data
        ##########

        print(f"Running code for executing --pipeline import_data")

        # Create config file for import_data
        config_import_data = {
            'dataFilename': f'timestamps-{simulation_name}',
            'sensorFilename': "sensor_info",
            'minimumLenData': config['minimumLenData']  # Reduce if timestamps-TEST.csv contains fewer than 10000 vehicles in one 24h day
        }
        config_import_data_path = os.path.join(hornsgatan_config, f'import_data-{simulation_name}.yaml')
        create_yaml_file(config_import_data, config_import_data_path)

        # Run pipeline for import_data
        command_to_run = f"python main.py --pipeline import_data --config {config_import_data_path}"
        run_command_on_bash(command_to_run, hornsgatan_home, verbose)

        # Move files in folder "Hornsgatan/data/daily_splitted_data/" to "Hornsgatan/data/daily_splitted_data/{simulation_name}/"
        folder_from = os.path.join(hornsgatan_home, 'data', 'daily_splitted_data')
        folder_to = os.path.join(hornsgatan_home, 'data', 'daily_splitted_data', simulation_name)
        move_all_files_from_folder_to_folder(folder_from, folder_to)

        # Delete all files in folder "Hornsgatan/data/transform_raw_data/"
        folder_with_files_to_delete = os.path.join(hornsgatan_home, 'data', 'transform_raw_data')
        delete_all_files_in_folder(folder_with_files_to_delete)

    if not (only_run_import_data or only_run_sim):

        ##########
        # B) --pipeline calib
        ##########

        print(f"Running code for executing --pipeline calib")

        # Create folder for current simulation "{simulation_name}" under "Hornsgatan/data/calibration_data/"
        folder_to_create = os.path.join(hornsgatan_home, 'data', 'calibration_data', simulation_name)
        os.makedirs(folder_to_create, exist_ok=True)

        # Iterate through detector list
        for cur_detector in detector_list:
            print(f"Processing detector: {cur_detector}")

            # Create config file for calib
            config_calib = {
                'date': date,  # MODIFY.
                'detector': cur_detector,  # MODIFY.
                'path': "data/calibration_intermediate_data/",
                'pathout': f"data/calibration_data/{simulation_name}/",
                'pathin': f"data/daily_splitted_data/{simulation_name}/",
                'iteration': 50,
                'init_number': init_number,  # MODIFY. Number of vehicles considered. 0 = all vehicles
                'network_file': "data/map/Hornsgatan.net.xml",
                'base_estimator': "GP",
                'acq_func': "LCB",
                'n_initial_points': 5,
                'no_speed': no_speed,  # MODIFY. false -> loss is calculated using deviation from radar speed; true -> loss is calculated using deviation from speed limit
                'name': "GP_LCB_50_5",
            }
            config_calib_path = os.path.join(hornsgatan_config, f'calib-{simulation_name}.yaml')
            create_yaml_file(config_calib, config_calib_path)

            # Run pipeline for calib
            command_to_run = f"python main.py --pipeline calib --config {config_calib_path}"
            if calib_with_fcd:
                command_to_run += ' --fcd'  # Add --fcd option to calib if required
            run_command_on_bash(command_to_run, hornsgatan_home, verbose)

            # Move contents of folder "Hornsgatan/data/calibration_intermediate_data/" to
            # "Hornsgatan/data/calibration_intermediate_data/{simulation_name}/"
            folder_from = os.path.join(hornsgatan_home, 'data', 'calibration_intermediate_data')
            folder_to = os.path.join(hornsgatan_home, 'data', 'calibration_intermediate_data', simulation_name)
            move_all_files_from_folder_to_folder(folder_from, folder_to)

    if not (only_run_import_data or only_run_calib):

        ##########
        # B) --pipeline sim
        ##########

        # Create folder for current simulation "TEST" under "Hornsgatan/data/sim_data/"
        folder_to_create = os.path.join(hornsgatan_home, 'data', 'sim_data', simulation_name)
        os.makedirs(folder_to_create, exist_ok=True)

        # Iterate through detector list
        for cur_detector in detector_list:
            print(f"Processing detector: {cur_detector}")

            # Create config file for sim
            config_sim = {
                'date': date,  # MODIFY.
                'detector': cur_detector,  # MODIFY.
                'path': "data/sim_intermediate_data/",
                'pathout': f"data/sim_data/{simulation_name}/",
                'pathin': f"data/calibration_data/{simulation_name}/",
                'init_number': init_number,  # MODIFY. Number of vehicles considered. 0 = all vehicles
                'network_file': "data/map/Hornsgatan.net.xml",
                'hornsgatan_home': hornsgatan_home,
            }
            config_sim_path = os.path.join(hornsgatan_config, f'sim-{simulation_name}.yaml')
            create_yaml_file(config_sim, config_sim_path)

            # Run pipeline for sim
            command_to_run = f"python main.py --pipeline sim --config {config_sim_path}"
            run_command_on_bash(command_to_run, hornsgatan_home, verbose)

            # Move files in "Hornsgatan/data/sim_intermediate_data/" to
            # "Hornsgatan/data/sim_intermediate_data/TEST/"
            folder_from = os.path.join(hornsgatan_home, 'data', 'sim_intermediate_data')
            folder_to = os.path.join(hornsgatan_home, 'data', 'sim_intermediate_data', simulation_name)
            move_all_files_from_folder_to_folder(folder_from, folder_to)

            # Convert fcd file from .xml to .csv
            # Import required function
            if hornsgatan_home not in sys.path:
                sys.path.insert(0, hornsgatan_home)
            from src.tools import mytools
            path_to_xml_file_directory = folder_to+os.sep
            postfix = f"{cur_detector}_{date}" if init_number < 1 else f"{cur_detector}_{date}_{init_number}"
            mytools.fcd_xml_to_csv(path_to_xml_file_directory, postfix)

    return 0


if __name__ == "__main__":
    main()

    exit(0)
