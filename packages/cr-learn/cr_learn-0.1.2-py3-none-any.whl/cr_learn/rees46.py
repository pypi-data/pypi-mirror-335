import pandas as pd
import os
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the paths
path = os.path.abspath('CRLearn/CRDS/REES46')
dm_path = os.path.join(path, 'direct_msg')
events_file = os.path.join(path, 'events.csv')

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    if not os.path.exists(file_path):
        logging.error(f"The file {file_path} does not exist.")
        return False
    return True

def load_csv(file_path: str, use_columns: list = None, nrows: int = None) -> pd.DataFrame:
    """Generic function to load a CSV file with safety checks."""
    if not check_file_exists(file_path):
        return pd.DataFrame()  # Return empty DataFrame instead of raising error
    
    try:
        return pd.read_csv(
            file_path, 
            usecols=use_columns, 
            nrows=nrows,  # Add row limit
            low_memory=False,
            on_bad_lines='skip'  # Skip problematic lines
        )
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        return pd.DataFrame()

def load_events(sample_size: float = 1.0, use_columns: list = None, nrows: int = None) -> pd.DataFrame:
    """Load and optionally sample events data."""
    df = load_csv(events_file, use_columns, nrows)
    if len(df) > 0 and sample_size < 1.0:
        df = df.sample(frac=sample_size)
    return df

def preprocess_events(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the events DataFrame."""
    if len(df) == 0:
        return df
        
    try:
        df = df.copy()
        df.fillna({'brand': 'unknown'}, inplace=True)
        if 'event_time' in df.columns:
            df['event_time'] = pd.to_datetime(df['event_time'])
        if 'price' in df.columns:
            df = df[df['price'] >= 10]
        return df
    except Exception as e:
        logging.error(f"Error preprocessing events: {str(e)}")
        return df

def load_direct_msg_data(limit_rows: int = 100) -> Dict[str, pd.DataFrame]:
    """Load all datasets from the direct_msg folder with a row limit."""
    datasets = {}
    files = ['campaigns.csv', 'client_first_purchase_date.csv', 'holidays.csv', 'messages-demo.csv']
    
    if not os.path.exists(dm_path):
        logging.error(f"Directory not found: {dm_path}")
        return datasets
    
    for file in files:
        file_path = os.path.join(dm_path, file)
        if check_file_exists(file_path):
            df = load_csv(file_path, nrows=limit_rows)
            if len(df) > 0:
                datasets[file.split('.')[0]] = df
    
    return datasets

def load(data_path: str = path, sample_size: float = 0.1, use_columns: list = None, nrows: int = 1000) -> Dict[str, pd.DataFrame]:
    """Load and preprocess all data with safety limits."""
    try:
        data_path = os.path.abspath(data_path)
        events = load_events(sample_size, use_columns, nrows)
        processed_events = preprocess_events(events)
        direct_msg_data = load_direct_msg_data(limit_rows=nrows)
        
        result = {'events': processed_events}
        result.update(direct_msg_data)
        return result
        
    except Exception as e:
        logging.error(f"Error in load function: {str(e)}")
        return {'events': pd.DataFrame()}

def load_config(config_path: str = os.path.join(path, 'context_config.json')) -> Dict[str, Any]:
    """Load configuration from the specified path."""
    if not check_file_exists(config_path):
        raise FileNotFoundError(f"The configuration file at {config_path} does not exist.")
    
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from the configuration file at {config_path}.")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading configuration: {e}")
        raise

if __name__ == "__main__":
    # Test with small sample size and row limit
    logging.info("Testing REES46 data loading...")
    
    try:
        # Test events loading
        events_sample = load_events(sample_size=0.01, nrows=1000)
        logging.info(f"Loaded events sample shape: {events_sample.shape}")
        print(events_sample)
        # Test direct message data loading
        msg_data = load_direct_msg_data(limit_rows=100)
        print(msg_data)

        for name, df in msg_data.items():
            logging.info(f"Loaded {name} shape: {df.shape}")
        
        # Test full load
        all_data = load(sample_size=0.01, nrows=1000)
        for name, df in all_data.items():
            logging.info(f"Final {name} shape: {df.shape}")
            
    except KeyboardInterrupt:
        logging.info("Loading interrupted by user")
    except Exception as e:
        logging.error(f"Error during testing: {str(e)}")
