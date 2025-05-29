from hamilton.function_modifiers import extract_columns, schema
import pandas as pd

# --- 1. Read raw CSV file and extract key columns ---

#@extract_columns("timestamp", "avg_speed", "node_id")
@schema.output(
    ("timestamp",str),
    ("avg_speed",float),
    ("node_id",str),
)
def raw_data(dataFilename: str) -> pd.DataFrame:
    """
    Reads raw sensor data from a CSV file located in 'data/raw_data/'.
    Extracts only the 'timestamp', 'avg_speed', and 'node_id' columns using Hamilton's `extract_columns`.
    
    Args:
        dataFilename: The name of the file (without `.csv`) to read.
    
    Returns:
        A DataFrame with columns: timestamp, avg_speed, node_id.
    """
    raw_data_path = f"data/raw_data/{dataFilename}.csv"
    return pd.read_csv(raw_data_path)

def timestamp(raw_data: pd.DataFrame) -> pd.Series:
    return raw_data["timestamp"]

def avg_speed(raw_data: pd.DataFrame) -> pd.Series:
    return raw_data["avg_speed"]

def node_id(raw_data: pd.DataFrame) -> pd.Series:
    return raw_data["node_id"]
# --- 2. Load sensor info from file ---

def sensor_info(sensorFilename: str) -> pd.DataFrame:
    """
    Loads sensor mapping information from a CSV file in 'data/sensor_info/'.
    
    Args:
        sensorFilename: The name of the file (without `.csv`) containing node-to-detector mappings.
    
    Returns:
        A DataFrame with sensor metadata (expected columns: node_id, detector_id).
    """
    sensor_info_path = f"data/sensor_info/{sensorFilename}.csv"
    return pd.read_csv(sensor_info_path)


# --- 3. Convert timestamp string to integer Unix timestamp ---

def time_detector_real(timestamp: pd.Series) -> pd.Series:
    """
    Converts string timestamps to UNIX time (seconds since epoch).
    Assumes the format is 'YYYYMMDDTHHMMSS'.
    
    Args:
        timestamp: Series of timestamp strings.
    
    Returns:
        Series of integer UNIX timestamps.
    """
    s1 = pd.to_datetime(timestamp, format='%Y%m%dT%H%M%S')
    return s1.apply(lambda x: int(x.timestamp()))

# --- 4. Pass speed value through (already float) ---

def speed_detector_real(avg_speed: pd.Series) -> pd.Series:
    """
    Pass-through function to rename avg_speed to speed_detector_real in the DAG.
    
    Args:
        avg_speed: Average speed values from sensors.
    
    Returns:
        Same speed values, but with a new logical name in the DAG.
    """
    return avg_speed

# --- 5. Map node_id to detector_id (assumed to be string) ---

def detector_id(node_id: pd.Series, sensor_info: pd.DataFrame) -> pd.Series:
    """
    Maps node IDs to detector IDs using a lookup from sensor_info.
    
    Args:
        node_id: Series of node IDs from raw data.
        sensor_info: DataFrame containing node_id and detector_id mapping.
    
    Returns:
        Series of detector IDs.
    """
    node2detector = sensor_info.set_index('node_id')['detector_id'].to_dict()
    return node_id.map(node2detector)


# --- 6. Combine columns into a clean DataFrame ---
@schema.output(
    ("detector_id", str),
    ("time_detector_real", int),
    ("speed_detector_real", float),  
)
def transform_raw_data(detector_id: pd.Series, time_detector_real: pd.Series, speed_detector_real: pd.Series) -> pd.DataFrame:
    """
    Combines cleaned and mapped data into a unified DataFrame.
    
    Args:
        detector_id: Mapped detector IDs.
        time_detector_real: UNIX timestamps.
        speed_detector_real: Speed values.
    
    Returns:
        A tidy DataFrame with cleaned data.
    """
    df = pd.DataFrame({
        "detector_id": detector_id,
        "time_detector_real": time_detector_real,
        "speed_detector_real": speed_detector_real
    })
    return df


# --- 7. Save transformed DataFrame to CSV ---

def save_transform_raw_data(transform_raw_data: pd.DataFrame, dataFilename: str) -> str:
    """
    Saves the cleaned dataset to disk.
    
    Args:
        transform_raw_data: Cleaned and combined DataFrame.
        dataFilename: Name of the original file (used in output naming).
    
    Returns:
        Path to the saved CSV file.
    """
    extended_output_file_path = f"data/transform_raw_data/{dataFilename}_out.csv"
    transform_raw_data.to_csv(extended_output_file_path, index=False)
    return extended_output_file_path


# --- 8. Split data by day and save to separate files ---

def split_and_save_daily(transform_raw_data: pd.DataFrame, minimumLenData:int) -> list:
    """
    Adds 'day' and 'date' columns, then splits the data by date, saving each to a separate file.
    Saves only if there are more than 10,000 rows for that date.
    
    Args:
        transform_raw_data: The full cleaned dataset.
    
    Returns:
        A list of filenames that were saved.
    """
    output_dir = "data/daily_splitted_data/"
    
    # Convert UNIX time to datetime and extract day name and date
    transform_raw_data['day'] = pd.to_datetime(transform_raw_data['time_detector_real'], unit='s').dt.day_name()
    transform_raw_data['date'] = pd.to_datetime(transform_raw_data['time_detector_real'], unit='s').dt.date
    
    saved_files = []
    for date, group in transform_raw_data.groupby('date'):
        file_name = f"data_{date}.csv"
        if len(group) > minimumLenData:
            group.to_csv(output_dir + file_name, index=False)
            saved_files.append(file_name)
    
    return saved_files
