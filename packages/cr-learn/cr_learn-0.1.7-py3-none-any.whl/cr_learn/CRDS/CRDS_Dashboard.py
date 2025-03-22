'''
CRDS Dashboard
This script provides a command-line interface to manage datasets in the .cache directory.
It allows users to list downloaded datasets and delete them if needed.
'''
import os
import argparse
import logging
import shutil
from typing import List, Dict, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the cache directory
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/CRLearn")

def get_datasets_in_cache(cache_dir: str = DEFAULT_CACHE_DIR) -> List[Dict[str, Any]]:
    """Get a list of all datasets in the cache directory with their sizes and last modified times."""
    datasets = []
    
    if not os.path.exists(cache_dir):
        logging.warning(f"Cache directory {cache_dir} does not exist.")
        return datasets
    
    for dataset_name in os.listdir(cache_dir):
        dataset_path = os.path.join(cache_dir, dataset_name)
        
        if os.path.isdir(dataset_path):
            size = get_directory_size(dataset_path)
            last_modified = os.path.getmtime(dataset_path)
            last_modified_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_modified))
            
            datasets.append({
                'name': dataset_name,
                'path': dataset_path,
                'size': size,
                'size_str': format_size(size),
                'last_modified': last_modified,
                'last_modified_str': last_modified_str
            })
    
    # Sort by size (largest first)
    datasets.sort(key=lambda x: x['size'], reverse=True)
    return datasets

def get_directory_size(path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def format_size(size_bytes: int) -> str:
    """Format size in bytes to a human-readable string."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def delete_dataset(dataset_name: str, cache_dir: str = DEFAULT_CACHE_DIR) -> bool:
    """Delete a dataset from the cache directory."""
    dataset_path = os.path.join(cache_dir, dataset_name)
    
    if not os.path.exists(dataset_path):
        logging.error(f"Dataset {dataset_name} does not exist in {cache_dir}.")
        return False
    
    try:
        if os.path.isdir(dataset_path):
            shutil.rmtree(dataset_path)
        else:
            os.remove(dataset_path)
        logging.info(f"Successfully deleted dataset: {dataset_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to delete dataset {dataset_name}: {e}")
        return False

def list_datasets(args: argparse.Namespace) -> None:
    """List all datasets in the cache directory."""
    datasets = get_datasets_in_cache(args.cache_dir)
    
    if not datasets:
        logging.info("No datasets found in cache directory.")
        return
    
    total_size = sum(dataset['size'] for dataset in datasets)
    
    print(f"\nFound {len(datasets)} datasets in cache (Total size: {format_size(total_size)}):")
    print("-" * 80)
    print(f"{'#':<4} {'Dataset':<20} {'Size':<10} {'Last Modified':<20}")
    print("-" * 80)
    
    for i, dataset in enumerate(datasets, 1):
        print(f"{i:<4} {dataset['name']:<20} {dataset['size_str']:<10} {dataset['last_modified_str']:<20}")
    
    print("-" * 80)

def delete_datasets(args: argparse.Namespace) -> None:
    """Delete specified datasets from the cache directory."""
    if not args.datasets:
        logging.error("No datasets specified for deletion.")
        return
    
    all_datasets = get_datasets_in_cache(args.cache_dir)
    all_dataset_names = [d['name'] for d in all_datasets]
    
    for dataset_name in args.datasets:
        if dataset_name not in all_dataset_names:
            logging.warning(f"Dataset '{dataset_name}' not found in cache.")
            continue
            
        if args.confirm:
            confirm = input(f"Are you sure you want to delete '{dataset_name}'? (y/n): ")
            if confirm.lower() != 'y':
                logging.info(f"Skipping deletion of '{dataset_name}'.")
                continue
        
        delete_dataset(dataset_name, args.cache_dir)

def clear_all_datasets(args: argparse.Namespace) -> None:
    """Clear all datasets from the cache directory."""
    datasets = get_datasets_in_cache(args.cache_dir)
    
    if not datasets:
        logging.info("No datasets found in cache directory.")
        return
    
    if args.confirm:
        confirm = input(f"Are you sure you want to delete ALL {len(datasets)} datasets? (y/n): ")
        if confirm.lower() != 'y':
            logging.info("Operation cancelled.")
            return
    
    for dataset in datasets:
        delete_dataset(dataset['name'], args.cache_dir)
    
    logging.info(f"All datasets cleared from {args.cache_dir}")

def get_cache_info(args: argparse.Namespace) -> None:
    """Get information about the cache directory."""
    if not os.path.exists(args.cache_dir):
        logging.warning(f"Cache directory {args.cache_dir} does not exist.")
        return
    
    datasets = get_datasets_in_cache(args.cache_dir)
    total_size = sum(dataset['size'] for dataset in datasets)
    
    print("\nCache Information:")
    print("-" * 80)
    print(f"Cache directory: {args.cache_dir}")
    print(f"Total datasets: {len(datasets)}")
    print(f"Total size: {format_size(total_size)}")
    
    # Get available disk space
    try:
        total, used, free = shutil.disk_usage(args.cache_dir)
        print(f"Disk space: {format_size(free)} free of {format_size(total)}")
        print(f"Cache usage: {(total_size / total) * 100:.2f}% of total disk space")
    except Exception as e:
        logging.error(f"Could not get disk usage information: {e}")
    
    print("-" * 80)

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(
        description="CRDS Dashboard - Manage datasets in the cache directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python CRDS_Dashboard.py list                   # List all datasets in cache
  python CRDS_Dashboard.py delete ml_1m beibei    # Delete specified datasets
  python CRDS_Dashboard.py clear                  # Clear all datasets
  python CRDS_Dashboard.py info                   # Show cache information
        """
    )
    
    parser.add_argument('--cache-dir', default=DEFAULT_CACHE_DIR,
                        help=f'Path to the cache directory (default: {DEFAULT_CACHE_DIR})')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all datasets in cache')
    list_parser.set_defaults(func=list_datasets)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete specified datasets')
    delete_parser.add_argument('datasets', nargs='+', help='Names of datasets to delete')
    delete_parser.add_argument('--no-confirm', dest='confirm', action='store_false',
                              help='Skip confirmation prompt')
    delete_parser.set_defaults(func=delete_datasets, confirm=True)
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all datasets from cache')
    clear_parser.add_argument('--no-confirm', dest='confirm', action='store_false',
                             help='Skip confirmation prompt')
    clear_parser.set_defaults(func=clear_all_datasets, confirm=True)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show cache information')
    info_parser.set_defaults(func=get_cache_info)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return
    
    args.func(args)

if __name__ == "__main__":
    main() 