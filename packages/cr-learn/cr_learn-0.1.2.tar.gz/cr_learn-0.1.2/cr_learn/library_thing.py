import pandas as pd
import json
from typing import Dict, List, Any
import os
from cr_learn.utils.gdrive_downloader import check_and_download, get_dataset_path

# Define the base path
path = 'CRLearn/CRDS/library_thing'
default_file_path = 'CRLearn/CRDS/library_thing'

# These paths will be updated dynamically when loading
map_cluster_1 = None
map_cluster_2 = None
map_cluster_3 = None

def load_mapping() -> pd.DataFrame:
    """Load and combine the LibraryThing mapping files."""
    global map_cluster_1, map_cluster_2, map_cluster_3
    
    # Download files if necessary and get the actual path where files are stored
    check_and_download('library_thing', base_path=path)
    
    # Get the actual dataset path where files were downloaded
    dataset_path = get_dataset_path('library_thing', base_path=path)
    
    # Update the file paths to point to the correct location
    map_cluster_1 = os.path.join(dataset_path, 'MappingLibrarything2DBpedia_1.tsv')
    map_cluster_2 = os.path.join(dataset_path, 'MappingLibrarything2DBpedia_2.tsv')
    map_cluster_3 = os.path.join(dataset_path, 'MappingLibrarything2DBpedia_3.tsv')
    
    columns = ['book_id', 'title', 'dbpedia_url']
    
    df1 = pd.read_csv(map_cluster_1, sep='\t', encoding='utf-8', names=columns, header=None)
    df2 = pd.read_csv(map_cluster_2, sep='\t', encoding='utf-8', names=columns, header=None)
    df3 = pd.read_csv(map_cluster_3, sep='\t', encoding='utf-8', names=columns, header=None)
    
    # Concatenate all DataFrames vertically
    combined_df = pd.concat([df1, df2, df3], ignore_index=True)
    
    return combined_df


def load(data_path: str = path) -> Dict[str, pd.DataFrame]:
    """Load and process LibraryThing mapping data from the specified path."""
    # Ensure the directory exists
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
    
    mapping = load_mapping()
    
    # Create a simplified books DataFrame from the mapping
    books = mapping[['book_id', 'title']].copy()
    
    # Extract DBpedia resource name from URL
    mapping['dbpedia_resource'] = mapping['dbpedia_url'].apply(
        lambda x: x.split('/')[-1] if pd.notnull(x) else None
    )

    return {
        'books': books,
        'mapping': mapping,
        'dbpedia_mapping': dict(zip(mapping['book_id'], mapping['dbpedia_resource']))
    }


# if __name__ == "__main__":
#     # Test load_mapping function
#     print("Testing load_mapping()...")
#     mapping_df = load_mapping()
#     print(f"Mapping DataFrame shape: {mapping_df.shape}")
#     print("\nFirst few rows of mapping:")
#     print(mapping_df.head())
#     print("\n" + "="*50 + "\n")

#     # Test load function
#     print("Testing load()...")
#     data = load()
    
#     # Print information about each component
#     print("\nBooks DataFrame:")
#     print(f"Shape: {data['books'].shape}")
#     print(data['books'].head())
    
#     print("\nMapping DataFrame:")
#     print(f"Shape: {data['mapping'].shape}")
#     print(data['mapping'].head())
    
#     print("\nDBpedia Mapping (first 5 items):")
#     print(dict(list(data['dbpedia_mapping'].items())[:5]))
