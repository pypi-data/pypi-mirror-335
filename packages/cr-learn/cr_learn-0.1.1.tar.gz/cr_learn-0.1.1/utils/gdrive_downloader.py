import os
import gdown
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
import cr_learn.utils.vish_variables as ve

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ASCII Art for CRLearn
CRLEARN_ASCII_ART = r"""                                
  _____ _____    _                           
 / ____|  __ \  | |                          
| |    | |__) | | |     ___  __ _ _ __ _ __  
| |    |  _  /  | |    / _ \/ _` | '__| '_ \ 
| |____| | \ \  | |___|  __/ (_| | |  | | | |
 \_____|_|  \_\ |______\___|\__,_|_|  |_| |_| [powered by corerec]                                 
"""

_ENV_UIVERSE_ = "15jH2ceXyN0JIR_Q9VAfCs4gCMzbb7eHm"
null=_ENV_UIVERSE_

# Dictionary mapping dataset names to their Google Drive file IDs
# You'll need to replace these with actual Google Drive file IDs
DATASET_DRIVE_IDS = {
    'ml_1m': {
        'folder_id': '1fBmaWwTKYYOxdOjXQoDeYb7gd3WC7Hq2',
        'files': {
            'users.dat': '1cpJHG80LPKa4yfIsnYSr8h6AmoaXNVUj',
            'movies.dat': '1rTR4l8tjXiPQtVnhAFB5pMtLajsyS6N2',
            'ratings.dat': '15wltC5LPW1bYtIwXmQulkRYoynOGjobl'
        }
    },
    'ml_100k': {
        'folder_id': '1I293VYyz65Z_Gf8wf2Js20F2R0CYdl7i',
        'files': {
            'ub.test': '1S83FBlqKYmmgYrE-41jGBUAzu6oU7ivX',
            'ub.base': '1dZVJci0nDQnEcZtqzPauxENkGcb9h3Dx',
            'ua.test': '1O8gOY5mzNsduuM84q45N4vAzcW2bHJ_2',
            'ua.base': '1q0fNy9XUQTf2tlr13yQoV3oMqjXlQW2B',
            'u5.test': '1IGGo9xPUTXFJSbSWIR2DgamkUzREWkFV',
            'u5.base': '137lkpfm43sDmOC-j4syv2r7Nh5Mqne6u',
            'u4.test': '1JL97trjA8Uh81a_Eq9reKw0xYh3r-eI2',
            'u4.base': '1ZP7eoqt0kwTA5HsCdWQV6HdVNO-6KHMr',
            'u3.test': '1aZgmV1ILwJNAe6ChkyzmLxoIR9AWyASr',
            'u3.base': '1TF-0TVciJg-j6mH3jSsODLrdhCaStEjo',
            'u2.test': '10hyfW7Ksr9n-o4ro2O1gXtJ3m4IEASBM',
            'u2.base': '11prGUBQlmYGnbuNpFasqaWhMqqi-CyWW',
            'u1.test': '1mU25I_-q3wP-eOeI_1Xbid-vsDEGcQEq',
            'u1.base': '1iuJK9E2xUo2RD-tErIGmcsXEZJvNU2qe',
            'u.user': '1zdwJ7a4n29Ymw6at8k3H5HEhlblD997L',
            'u.occupation': '1w4rOiVrJfZF8RjY2IdInaeNqUbD9Uyau',
            'u.item': '1e68tS7vUMhcnzUHT0JSwZgZDvc7Jxrk-',
            'u.info': '1wa5Vo7Qc4MSQmKsYYWQU01qEIbAhldPX',
            'u.genre': '1KE8r1LeRhRNJQs0rhkAr4rROJQQNUMeX',
            'u.data': '1TBDxoLfY4_duS7qPpDU46cwKeNf3zzHF',
            'ullbut.pl': '1OE-3spWk9GRYBrzmJpUEsGxOs4grZEVx'
        }
    },

    'tmall': {
        'folder_id': '1s2w74SWDHhfAvsa9JQcOCTK-Xph7c__T',
        'files': {
            'ijcai2016_koubei_test': '1xkXzBt87_yQ7Y-bDyaHEbOFAViE9mz2_',
            'ijcai2016_koubei_train': '1k6i_8wJwPGBnxm0MUEI4vzqGMi1y3NWz',
            'ijcai2016_merchant_info': '5_u46UqgxOdYd08_PJWdIEPVvRXy5',
            'ijcai2016_taobao.csv': '1tKcTT46v29PJG-8arkYz4jgFChHauK3K'
        }
    },
    'beibei': {
        'folder_id': '1lFXSlAW0pZUo2J4MlHMudQ6kcFjHI4TA',
        'files': {
            'trn_buy': '1hQpnc-I3pIkcTk9TluCAZ-xCGLI1hn52',
            'trn_cart': '1B8vB37DfGwQBMWytKyb5rlz41RwtxeOp',
            'trn_pv': 'obwrQgDzBlfKCaCZ1rvkMunMqrNn',
            'tst_int': '1GFjdABMgixv6vQ0e95HBUjTwtDtMuoT2'
        }
    },
    'ijcai': {
        'folder_id': 'your_folder_id_here',
        'files': {
            'train_format1.csv': 'file_id_for_train',
            'test_format1.csv': 'file_id_for_test',
            'user_info_format1.csv': 'file_id_for_user_info'
        }
    },
    'library_thing': {
        'folder_id': '1YjXeuoAmKlWXfX2i8oL11KKvJ6nGmNJQ',
        'files': {
            'MappingLibrarything2DBpedia_1.tsv': '1gHHEAHUBC5v0p7rlv7CBZgXTXO8N9UCL',
            'MappingLibrarything2DBpedia_2.tsv': '1yyC3rVSQrAhd8WaRPPs0y2SksYZ6kdoM',
            'MappingLibrarything2DBpedia_3.tsv': '1yY2TrYH5W7iynTDcbqDUpS3Vevj4khpX'
        }
    },
    'rees46': {
        'folder_id': 'your_folder_id_here',
        'files': {
            'events.csv': 'file_id_for_events',
            'direct_msg/campaigns.csv': 'file_id_for_campaigns',
            'direct_msg/client_first_purchase_date.csv': 'file_id_for_client_first_purchase',
            'direct_msg/holidays.csv': 'file_id_for_holidays',
            'direct_msg/messages-demo.csv': 'file_id_for_messages'
        }
    },
    'steam_games': {
        'folder_id': '1i44UED8Ja48hJ6lh1jrQRXtUS7j_HwaD',
        'files': {
            'steam_games.json': '1bgdx2PjwnhcYVyAsvkGt6hCxUgUV9uHy'
        }
    },
    'ml_to_dbpedia': {
        'folder_id': '1muVOvwbQRFduGX_jKnkNh-VCRwQ3fZmU',
        'files': {
            'MappingMovielens2DBpedia-1.0.tsv':'1gd1YeOJBX4RVH7Whok8G41_VrM3L1QTo',
            'MappingMovielens2DBpedia-1.1.tsv':'1U-FL14y7gzHVYPvSjSEifkf9HARxpKh4',
            'MappingMovielens2DBpedia-1.2.tsv':'1gd1YeOJBX4RVH7Whok8G41_VrM3L1QTo'
        }
    }
}

# Define default cache directory (similar to HF datasets)
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/crlearn")

# Function to get cache directory with environment variable override
def get_cache_dir() -> str:
    """Get the cache directory, respecting environment variables."""
    return os.environ.get("CRLEARN_CACHE_DIR", DEFAULT_CACHE_DIR)

# Function to create and manage dataset registry
def get_registry_path() -> str:
    """Get the path to the dataset registry file."""
    cache_dir = get_cache_dir()
    ensure_dir_exists(cache_dir)
    return os.path.join(cache_dir, "dataset_registry.json")

def load_registry() -> Dict:
    """Load the dataset registry or create if it doesn't exist."""
    registry_path = get_registry_path()
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning(f"Registry file corrupted, creating new one")
            return {"datasets": {}}
    return {"datasets": {}}

def save_registry(registry: Dict) -> None:
    """Save the dataset registry."""
    registry_path = get_registry_path()
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

def register_dataset_file(dataset_name: str, file_name: str, file_path: str) -> None:
    """Register a downloaded dataset file in the registry."""
    registry = load_registry()
    if dataset_name not in registry["datasets"]:
        registry["datasets"][dataset_name] = {"files": {}}
    
    registry["datasets"][dataset_name]["files"][file_name] = file_path
    save_registry(registry)
    logging.info(f"Registered {file_name} for dataset {dataset_name}")

def get_dataset_file_path(dataset_name: str, file_name: str) -> Optional[str]:
    """Get the path to a dataset file from the registry."""
    registry = load_registry()
    if (dataset_name in registry["datasets"] and 
        "files" in registry["datasets"][dataset_name] and
        file_name in registry["datasets"][dataset_name]["files"]):
        path = registry["datasets"][dataset_name]["files"][file_name]
        if os.path.exists(path):
            return path
    return None

def ensure_dir_exists(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def download_file(file_id: str, output_path: str) -> bool:
    """
    Download a file from Google Drive using its file ID.
    
    Args:
        file_id: The Google Drive file ID
        output_path: The path where the file should be saved
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        # Create the directory if it doesn't exist
        ensure_dir_exists(os.path.dirname(output_path))
        
        # Download the file
        logging.info(f"Downloading to {output_path}...")
        gdown.download(id=file_id, output=output_path, quiet=False)
        
        # Verify the file was downloaded
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logging.info(f"Successfully downloaded {output_path}")
            return True
        else:
            logging.error(f"Download failed or file is empty: {output_path}")
            return False
    except Exception as e:
        logging.error(f"Error downloading file {file_id} to {output_path}: {str(e)}")
        return False



def check_and_download(dataset_name: str, base_path: str = 'CRLearn/CRDS', files: Optional[List[str]] = None) -> bool:
    """Check for missing files, download those <500MB immediately, and prompt for larger files."""
    if dataset_name not in DATASET_DRIVE_IDS:
        logging.error(f"Unknown dataset: {dataset_name}")
        return False

    dataset_info = DATASET_DRIVE_IDS[dataset_name]
    
    # Use cache directory if base_path is not explicitly provided
    if base_path == 'CRLearn/CRDS':
        base_path = os.path.join(get_cache_dir(), 'datasets')
    
    dataset_path = os.path.join(base_path, dataset_name)
    ensure_dir_exists(dataset_path)

    files_to_check = files if files else dataset_info['files'].keys()
    
    # Check registry first for each file
    missing_files = []
    for file_name in files_to_check:
        cached_path = get_dataset_file_path(dataset_name, file_name)
        if cached_path and os.path.exists(cached_path):
            logging.info(f"Using cached file for {dataset_name}/{file_name} from {cached_path}")
            # Create symlink to the cached file if needed
            target_path = os.path.join(dataset_path, file_name)
            if not os.path.exists(target_path):
                # Create directory structure if needed
                ensure_dir_exists(os.path.dirname(target_path))
                
                # Create symlink on Unix or copy on Windows
                try:
                    os.symlink(cached_path, target_path)
                    logging.info(f"Created symlink from {cached_path} to {target_path}")
                except (OSError, AttributeError):
                    # On Windows or if symlinks not supported
                    import shutil
                    shutil.copy2(cached_path, target_path)
                    logging.info(f"Copied file from {cached_path} to {target_path}")
        else:
            missing_files.append(file_name)

    if not missing_files:
        return True

    success = True
    large_files = []

    for file_name in missing_files:
        if file_name not in dataset_info['files']:
            logging.error(f"File {file_name} not found in dataset configuration")
            success = False
            continue
            
        file_id = dataset_info['files'][file_name]
        output_path = os.path.join(dataset_path, file_name)
        
        # Assume each file is 600 MB for demonstration purposes
        file_size = 600 * 1024 * 1024  # Example: 600 MB for demonstration purposes

        if file_size < 500 * 1024 * 1024:
            if download_file(file_id, output_path):
                # Register the downloaded file
                register_dataset_file(dataset_name, file_name, os.path.abspath(output_path))
            else:
                success = False
        else:
            large_files.append(file_name)

    if large_files:
        total_size = len(large_files) * 600 * 1024 * 1024
        print(CRLEARN_ASCII_ART)
        print(ve.HEAD_WELCOME)
        user_input = input("The files are large. Do you want to continue downloading? (yes/no): ").strip().lower()
        if user_input == 'yes':
            for file_name in large_files:
                file_id = dataset_info['files'][file_name]
                output_path = os.path.join(dataset_path, file_name)
                if download_file(file_id, output_path):
                    # Register the downloaded file
                    register_dataset_file(dataset_name, file_name, os.path.abspath(output_path))
                else:
                    success = False
        else:
            # raise FileNotFoundError("Required files are missing and were not downloaded.")
              raise FileNotFoundError(ve.EXC_NOT_FOUND) 

    return success

# Add a new function to get dataset path
def get_dataset_path(dataset_name: str, base_path: Optional[str] = None) -> str:
    """
    Get the path to a dataset, using cache if available.
    
    Args:
        dataset_name: Name of the dataset
        base_path: Optional custom base path
        
    Returns:
        Path to the dataset directory
    """
    if base_path is None:
        base_path = os.path.join(get_cache_dir(), 'datasets')
    
    dataset_path = os.path.join(base_path, dataset_name)
    return dataset_path

def check_dataset_files(dataset_name: str, base_path: str = 'CRLearn/CRDS') -> Dict[str, bool]:
    """
    Check which files from a dataset exist locally.
    
    Args:
        dataset_name: Name of the dataset
        base_path: Base directory where datasets are stored
        
    Returns:
        Dict mapping file names to boolean indicating if they exist locally
    """
    if dataset_name not in DATASET_DRIVE_IDS:
        logging.error(f"Unknown dataset: {dataset_name}")
        return {}
    
    dataset_info = DATASET_DRIVE_IDS[dataset_name]
    dataset_path = os.path.join(base_path, dataset_name)
    
    result = {}
    for file_name in dataset_info['files'].keys():
        file_path = os.path.join(dataset_path, file_name)
        result[file_name] = os.path.exists(file_path) and os.path.getsize(file_path) > 0
    
    return result 