import configparser
import logging

# Logging setup
def setup_logging(postfix: str) -> str:
    """Set up logging for the simulation.
    
    Args:
        postfix: Postfix for log filename
        
    Returns:
        Path to log file
    """
    logfile_name = f"log/simulation_{postfix}.log"
    logger = logging.getLogger("calib")

    logging.basicConfig(
        filename=logfile_name,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Simulation started.")
    return logfile_name



def create_config(filename = 'config.ini' ):
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['Hamilton'] = {'project_id': 1}
    config['Database'] = {'db_name': 'example_db',
                          'db_host': 'localhost', 'db_port': '5432'}

    # Write the configuration to a file
    with open(filename, 'w') as configfile:
        config.write(configfile)
     
     
        
def read_config(filename = 'config.ini'):
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