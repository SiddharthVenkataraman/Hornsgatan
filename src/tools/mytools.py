import configparser
import logging
import os


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


def create_local_config(filename = 'config.ini' ):
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['Hamilton'] = {'project_id': 1}
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