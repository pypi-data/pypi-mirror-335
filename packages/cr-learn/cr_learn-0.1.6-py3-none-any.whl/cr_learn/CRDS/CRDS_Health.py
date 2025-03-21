'''
Corerec Dataset
CRDS is corerec dataset which is having a bunch of datasets and it keeps updating datasets.
The main motive of this CRDS_Health.py is to check whether the preprocessors of these 
datasets (e.g., ml_1m.py, tmall.py, etc.) are working fine or not, and also check other important 
things which will define if the dataset is healthy.
'''
import os
import logging
import importlib
import pandas as pd
import time
import sys
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the paths to check for datasets
DEFAULT_PATHS = [
    os.path.abspath('CRLearn/CRDS'),
    os.path.expanduser('~/.cache/cr_learn'),
    os.path.expanduser('~/.cache/CRLearn')
]

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    if not os.path.exists(file_path):
        logging.error(f"The file {file_path} does not exist.")
        return False
    return True

def find_dataset_path(dataset_name: str) -> str:
    """
    Search for a dataset in multiple possible locations.
    Returns the path where the dataset is found, or None if not found.
    """
    for base_path in DEFAULT_PATHS:
        dataset_path = os.path.join(base_path, dataset_name)
        if os.path.exists(dataset_path):
            return dataset_path
    
    return None

def check_preprocessor(module_name: str, sample_size: float = 0.01) -> Dict[str, Any]:
    """Check if the preprocessor can load and preprocess the dataset."""
    results = {
        'module': module_name,
        'status': 'failed',
        'datasets': [],
        'error': None,
        'load_time': 0,
        'dataset_path': None,
        'dataset_available': False
    }
    
    # Check if the dataset directory exists in any of the possible locations
    dataset_path = find_dataset_path(module_name)
    if dataset_path:
        results['dataset_path'] = dataset_path
        results['dataset_available'] = True
    
    # If dataset is not available, return early with appropriate message
    if not results['dataset_available']:
        results['error'] = f"Dataset '{module_name}' not found in any of the search paths"
        return results
    
    try:
        # First try to import from cr_learn
        try:
            start_time = time.time()
            module = importlib.import_module(f'cr_learn.{module_name}')
        except ImportError:
            # If that fails, try CRLearn
            try:
                module = importlib.import_module(f'CRLearn.{module_name}')
            except ImportError:
                raise ImportError(f"Could not import module {module_name} from either cr_learn or CRLearn")
        
        if hasattr(module, 'load'):
            # Handle different load function signatures
            if module_name == 'rees46':
                data = module.load(sample_size=sample_size, nrows=100)
            elif module_name == 'ijcai':
                data = module.load(limit_rows=100)
            else:
                data = module.load()
                
            results['load_time'] = time.time() - start_time
            results['status'] = 'success'
            
            # Process the returned data
            if isinstance(data, dict):
                for dataset_name, dataset in data.items():
                    dataset_info = {
                        'name': dataset_name,
                        'type': type(dataset).__name__,
                        'status': 'success'
                    }
                    
                    if isinstance(dataset, pd.DataFrame):
                        dataset_info['rows'] = len(dataset)
                        dataset_info['columns'] = len(dataset.columns)
                        dataset_info['empty'] = dataset.empty
                    elif hasattr(dataset, 'data') and isinstance(dataset.data, pd.DataFrame):
                        # For BeibeiDataset objects
                        dataset_info['rows'] = len(dataset.data)
                        dataset_info['columns'] = len(dataset.data.columns)
                        dataset_info['empty'] = dataset.data.empty
                    elif isinstance(dataset, dict):
                        dataset_info['entries'] = len(dataset)
                    elif isinstance(dataset, list):
                        dataset_info['items'] = len(dataset)
                    
                    results['datasets'].append(dataset_info)
            else:
                results['error'] = f"Unexpected return type from load function: {type(data)}"
        else:
            results['error'] = f"{module_name} does not have the required 'load' function."
    except Exception as e:
        results['error'] = str(e)
        logging.error(f"An error occurred in {module_name}: {e}")
    
    return results

def check_all_preprocessors() -> List[Dict[str, Any]]:
    """Check all preprocessors in the CRDS directory and return detailed results."""
    preprocessors = ['ml_1m', 'tmall', 'beibei', 'ijcai', 'library_thing', 'rees46', 'steam_games']
    results = []
    
    print("\n🔍 Running health checks on dataset preprocessors...")
    print("=" * 80)
    
    for preprocessor in preprocessors:
        print(f"Checking {preprocessor}...", end="", flush=True)
        result = check_preprocessor(preprocessor)
        results.append(result)
        
        # Log the result
        if not result['dataset_available']:
            print(f" ⚠️ Not available (searched in: {', '.join(DEFAULT_PATHS)})")
        elif result['status'] == 'success':
            dataset_path = result.get('dataset_path', 'Unknown location')
            print(f" ✅ Success ({result['load_time']:.2f}s) - Found at: {dataset_path}")
            
            for dataset in result['datasets']:
                if dataset.get('empty', True) == False:
                    if 'rows' in dataset:
                        print(f"  - {dataset['name']}: {dataset['rows']} rows, {dataset.get('columns', 'N/A')} columns")
                    elif 'entries' in dataset:
                        print(f"  - {dataset['name']}: {dataset['entries']} entries")
                    elif 'items' in dataset:
                        print(f"  - {dataset['name']}: {dataset['items']} items")
                else:
                    print(f"  - {dataset['name']}: ⚠️ Empty dataset")
        else:
            dataset_path = result.get('dataset_path')
            print(f" ❌ Failed: {result['error']} (Dataset found at: {dataset_path})")
    
    print("=" * 80)
    return results

def generate_health_report(results: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """Generate a summary health report from the preprocessor check results."""
    total = len(results)
    successful = sum(1 for result in results if result['status'] == 'success')
    failed = sum(1 for result in results if result['status'] == 'failed' and result['dataset_available'])
    not_available = sum(1 for result in results if not result['dataset_available'])
    
    failed_modules = [result['module'] for result in results if result['status'] == 'failed' and result['dataset_available']]
    missing_modules = [result['module'] for result in results if not result['dataset_available']]
    
    print(f"\n📊 Health Report Summary:")
    print(f"  Total preprocessors checked: {total}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Not available: {not_available}")
    
    if failed > 0:
        print(f"\nFailed modules: {', '.join(failed_modules)}")
        
        # Provide more detailed information about failed modules
        print("\nDetails for failed modules:")
        for result in results:
            if result['status'] == 'failed' and result['dataset_available']:
                print(f"  - {result['module']}: {result['error']}")
    
    if not_available > 0:
        print(f"\nMissing datasets: {', '.join(missing_modules)}")
        print("\nTo use these datasets, you need to download them first.")
        print("You can download them using the command:")
        print("  cr download dataset [dataset_name]")
    
    return successful, failed, failed_modules

def main():
    """Main function to run health checks on all preprocessors."""
    print("\n🩺 CR-Learn Doctor - Dataset Health Check")
    print("=" * 80)
    results = check_all_preprocessors()
    successful, failed, failed_modules = generate_health_report(results)
    
    if successful == len(results):
        print("\n🎉 All preprocessors are healthy!")
    else:
        print(f"\n⚠️  Some datasets need attention.")
        print("\nNote: This tool only checks for dataset availability and does not download missing datasets.")
        print("      Use 'cr download dataset [dataset_name]' to download missing datasets.")
    
    print("=" * 80)
    return successful, failed, failed_modules

if __name__ == "__main__":
    main()