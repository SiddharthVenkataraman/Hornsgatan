import configparser
import logging
import os
import xml.etree.ElementTree as ET
import pandas as pd
import zipfile

# Logging setup
def setup_logging(postfix, log_level="INFO", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"pipeline_{postfix}.log")
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, mode='a'),  # use mode 'w' for overwritting
            logging.StreamHandler()
        ]
    )


def create_local_config(filename = 'config/config.ini', project_id = 1 ):
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['Hamilton'] = {'project_id': project_id}
    config['Database'] = {'db_name': 'example_db',
                          'db_host': 'localhost', 'db_port': '5432'}

    # Write the configuration to a file
    with open(filename, 'w') as configfile:
        config.write(configfile)
     
     
        
def read_local_config(filename = 'config/config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    # Read the configuration file
    config.read(filename)
    # Access values from the configuration file
    project_id = config.get('Hamilton', 'project_id')
    db_name = config.get('Database', 'db_name')
    db_host = config.get('Database', 'db_host')
    db_port = config.get('Database', 'db_port')

    # Return a dictionary with the retrieved values
    config_values = {
        'project_id': project_id,
        'db_name': db_name,
        'db_host': db_host,
        'db_port': db_port
    }

    return config_values


def delete_all_except_list(directory, keep_files):
    """
    Delete all files in the given directory except those listed.

    Args:
        directory (str): Path to the target directory.
        keep_files (list): Filenames to keep (not full paths).
    """
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)

        if os.path.isfile(fpath) and fname not in keep_files:
            try:
                os.remove(fpath)
                print(f"Deleted: {fpath}")
            except Exception as e:
                print(f"Failed to delete {fpath}: {e}")
                
        
def fcd_xml_to_csv(path, postfix, pathout=None):
    if pathout==None:
        pathout = path
    # Parse the FCD XML file
    fcd_xml_file = f"{path}fcd_output_{postfix}.xml"
    tree_fcd = ET.parse(fcd_xml_file)
    root_fcd = tree_fcd.getroot()

    # Extract data from the XML
    fcd_data = []
    for timestep in root_fcd.findall('timestep'):
        time = float(timestep.get('time'))
        for vehicle in timestep.findall('vehicle'):
            fcd_data.append({
                'time': time,
                'id': vehicle.get('id'),
                'x': float(vehicle.get('x')),
                'y': float(vehicle.get('y')),
                'angle': float(vehicle.get('angle')),
                'speed': float(vehicle.get('speed')),
                'acceleration': float(vehicle.get('acceleration')),
                'pos': float(vehicle.get('pos')),
                'lane': vehicle.get('lane'),
            })

    # Convert to a DataFrame
    df_fcd = pd.DataFrame(fcd_data)

    # Save to CSV
    fcd_csv_file = f"{pathout}fcd_output_{postfix}.csv"
    df_fcd.to_csv(fcd_csv_file, index=False)
    print(f"FCD data successfully converted to CSV and saved as '{fcd_csv_file}'.")
    return fcd_csv_file
    
    


def zip_files(file_paths, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)  # Store just the file name
            zipf.write(file_path, arcname)
    print(f"Created zip file: {output_zip_path}")
