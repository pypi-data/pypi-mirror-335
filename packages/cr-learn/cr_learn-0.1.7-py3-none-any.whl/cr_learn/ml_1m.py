import pandas as pd
import json
from typing import Dict, List, Any
import os
from .utils.gdrive_downloader import check_and_download, get_dataset_path
from .utils.cr_cache_path import path

# Define the base path - use the expanded path to avoid issues with ~
base_path = os.path.expanduser(path)

def ensure_dataset_files(files: List[str] = None) -> bool:
    """Ensure that the required dataset files are available, downloading them if necessary."""
    # Check and download missing files
    return check_and_download('ml_1m', base_path=base_path, files=files)

def load_movies(movies_file: str = None) -> pd.DataFrame:
    """Load movies data, downloading if necessary."""
    if movies_file is None:
        movies_file = os.path.join(get_dataset_path('ml_1m', base_path=base_path), 'movies.dat')
    
    # Ensure the movies file exists
    if not os.path.exists(movies_file):
        ensure_dataset_files(['movies.dat'])
    
    # Read the file with more robust error handling
    try:
        # First, try to read with the standard parameters
        df = pd.read_csv(movies_file, sep='::', engine='python', 
                         names=['movie_id', 'title', 'genres'], 
                         encoding='latin-1', dtype={'genres': str})
        
        # Check if the title column has values
        if df['title'].isnull().all() or df['title'].str.strip().eq('').all():
            print("Warning: Title column is empty. Trying alternative parsing...")
            
            # Try reading the file as a single column and then split
            with open(movies_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()
            
            data = []
            for line in lines:
                parts = line.strip().split('::')
                if len(parts) >= 3:
                    movie_id = parts[0]
                    title = parts[1]
                    genres = '|'.join(parts[2:])
                    data.append([movie_id, title, genres])
            
            df = pd.DataFrame(data, columns=['movie_id', 'title', 'genres'])
        
        return df
    
    except Exception as e:
        print(f"Error loading movies data: {str(e)}")
        # Return an empty DataFrame as a fallback
        return pd.DataFrame(columns=['movie_id', 'title', 'genres'])

# This is now a function call, not a global variable
# movies_df = load_movies()

def load(data_path: str = None) -> Dict[str, pd.DataFrame]:
    """Load and process users, ratings, and movies data from the specified path."""
    # Use the base_path if data_path is not provided
    if data_path is None:
        data_path = base_path
    
    # Ensure all required files exist
    ensure_dataset_files(['users.dat', 'ratings.dat', 'movies.dat'])
    
    # Get the actual dataset path where files were downloaded
    dataset_path = get_dataset_path('ml_1m', base_path=data_path)
    
    # Print the path for debugging
    print(f"Loading data from: {dataset_path}")
    
    # Define file paths
    users_file = os.path.join(dataset_path, 'users.dat')
    ratings_file = os.path.join(dataset_path, 'ratings.dat')
    movies_file = os.path.join(dataset_path, 'movies.dat')
    
    # Check if files exist
    for file_path in [users_file, ratings_file, movies_file]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
    
    # Define column names for each file type
    column_names_users = ['user_id', 'gender', 'age', 'occupation', 'zip_code']
    column_names_ratings = ['user_id', 'movie_id', 'rating', 'timestamp']
    column_names_movies = ['movie_id', 'title', 'genres']
    
    # Check the format of each file to determine its actual content
    file_contents = {}
    
    # Function to identify file type based on content
    def identify_file_type(file_path):
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                first_line = f.readline().strip()
            
            parts = first_line.split('::')
            
            # Check for movies file - should have a title with year in parentheses
            if len(parts) >= 3 and '(' in parts[1] and ')' in parts[1]:
                return 'movies'
            
            # Check for users file - should have gender as second field (M or F)
            if len(parts) >= 5 and parts[1] in ['M', 'F']:
                return 'users'
            
            # Check for ratings file - should have 4 numeric fields
            if len(parts) == 4:
                try:
                    int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    return 'ratings'
                except ValueError:
                    pass
            
            # If we can't determine the file type, check the filename
            if 'movie' in os.path.basename(file_path).lower():
                return 'movies'
            elif 'user' in os.path.basename(file_path).lower():
                return 'users'
            elif 'rating' in os.path.basename(file_path).lower():
                return 'ratings'
            
            return None
        except Exception as e:
            print(f"Error identifying file type: {str(e)}")
            return None
    
    # Identify the actual content of each file
    file_types = {
        users_file: identify_file_type(users_file),
        ratings_file: identify_file_type(ratings_file),
        movies_file: identify_file_type(movies_file)
    }
    
    print(f"File type detection: {file_types}")
    
    # If file type detection fails, use the filename as a fallback
    if None in file_types.values():
        print("Warning: Some file types could not be detected. Using filenames as fallback.")
        if file_types[users_file] is None and 'user' in os.path.basename(users_file).lower():
            file_types[users_file] = 'users'
        if file_types[ratings_file] is None and 'rating' in os.path.basename(ratings_file).lower():
            file_types[ratings_file] = 'ratings'
        if file_types[movies_file] is None and 'movie' in os.path.basename(movies_file).lower():
            file_types[movies_file] = 'movies'
    
    # Map file paths to their actual content types
    actual_files = {
        'users': next((f for f, t in file_types.items() if t == 'users'), None),
        'ratings': next((f for f, t in file_types.items() if t == 'ratings'), None),
        'movies': next((f for f, t in file_types.items() if t == 'movies'), None)
    }
    
    print(f"Actual file mapping: {actual_files}")
    
    # Read the files based on their actual content
    users = pd.DataFrame(columns=column_names_users)
    ratings = pd.DataFrame(columns=column_names_ratings)
    movies = pd.DataFrame(columns=column_names_movies)
    
    if actual_files['users']:
        try:
            users = pd.read_csv(
                actual_files['users'],
                sep='::',
                engine='python',
                names=column_names_users,
                encoding='latin-1'
            )
            print(f"Successfully loaded users data from {actual_files['users']}")
        except Exception as e:
            print(f"Error loading users data: {str(e)}")
    
    if actual_files['ratings']:
        try:
            ratings = pd.read_csv(
                actual_files['ratings'],
                sep='::',
                engine='python',
                names=column_names_ratings,
                encoding='latin-1'
            )
            ratings['rating'] = pd.to_numeric(ratings['rating'], errors='coerce')
            print(f"Successfully loaded ratings data from {actual_files['ratings']}")
        except Exception as e:
            print(f"Error loading ratings data: {str(e)}")
    
    if actual_files['movies']:
        try:
            movies = pd.read_csv(
                actual_files['movies'],
                sep='::',
                engine='python',
                names=column_names_movies,
                encoding='latin-1',
                on_bad_lines='skip'
            )
            print(f"Successfully loaded movies data from {actual_files['movies']}")
        except Exception as e:
            print(f"Error loading movies data: {str(e)}")
    
    # If we couldn't identify the movies file, try to infer it from the other files
    if not actual_files['movies'] and (actual_files['users'] or actual_files['ratings']):
        missing_file = next((f for f in [users_file, ratings_file, movies_file] 
                            if f not in [actual_files['users'], actual_files['ratings']]), None)
        if missing_file:
            try:
                movies = pd.read_csv(
                    missing_file,
                    sep='::',
                    engine='python',
                    names=column_names_movies,
                    encoding='latin-1',
                    on_bad_lines='skip'
                )
                print(f"Inferred and loaded movies data from {missing_file}")
            except Exception as e:
                print(f"Error loading inferred movies data: {str(e)}")
    
    # Ensure movie_id is numeric
    if 'movie_id' in movies.columns:
        movies['movie_id'] = pd.to_numeric(movies['movie_id'], errors='coerce')
        movies = movies.dropna(subset=['movie_id'])
        if len(movies) > 0:
            movies['movie_id'] = movies['movie_id'].astype(int)
    
    # Build User Interactions
    user_interactions = {}
    if len(ratings) > 0:
        user_interactions = ratings.groupby('user_id')['movie_id'].apply(list).to_dict()
    
    # Build Item Features
    item_features = {}
    if len(movies) > 0:
        for _, row in movies.iterrows():
            movie_id = row['movie_id']
            genres = row['genres'].split('|') if isinstance(row['genres'], str) else []
            item_features[movie_id] = {genre: 1 for genre in genres}
    
    # Create a subset for training data (buy interactions)
    trn_buy = pd.DataFrame(columns=['user_id', 'item_id', 'label'])
    if len(ratings) > 0:
        trn_buy = ratings[ratings['rating'] >= 4].copy()
        trn_buy.rename(columns={'movie_id': 'item_id'}, inplace=True)
        trn_buy['label'] = 1
        trn_buy = trn_buy[['user_id', 'item_id', 'label']]
    
    return {
        'users': users,
        'ratings': ratings,
        'movies': movies,
        'user_interactions': user_interactions,
        'item_features': item_features,
        'trn_buy': trn_buy
    }

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from the specified path."""
    if config_path is None:
        config_path = os.path.join(get_dataset_path('ml_1m', base_path=base_path), 'context_config.json')
    
    # Ensure config file exists
    if not os.path.exists(config_path):
        # Try to download it
        ensure_dataset_files(['context_config.json'])
    
    # Ensure config_path is a valid string
    if not isinstance(config_path, str):
        raise ValueError("config_path must be a valid string.")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The configuration file at {config_path} does not exist.")
    
    with open(config_path, 'r') as file:
        return json.load(file)
    

def prepare_embedding_data(movies_file: str = None) -> List[List[str]]:
    """
    Prepare data for embedding training by tokenizing movie titles or genres.

    Parameters:
    - movies_file (str): Path to the movies file.

    Returns:
    - List[List[str]]: Tokenized sentences/documents for embedding training.
    """
    # Load movies data from the file
    if movies_file is None:
        movies_file = os.path.join(get_dataset_path('ml_1m', base_path=base_path), 'movies.dat')
        
    # Ensure the movies file exists
    if not os.path.exists(movies_file):
        ensure_dataset_files(['movies.dat'])
        
    movies = pd.read_csv(movies_file, sep='::', engine='python', names=['movie_id', 'title', 'genres'], encoding='latin-1', dtype={'genres': str})
    
    # Example: Using genres as sentences for Word2Vec
    sentences = [genres.split('|') for genres in movies['genres'] if isinstance(genres, str)]
    return sentences

