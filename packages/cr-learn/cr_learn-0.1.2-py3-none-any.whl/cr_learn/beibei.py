import pandas as pd
import numpy as np
from torch.utils.data import Dataset
import os
from cr_learn.utils.gdrive_downloader import check_and_download

class BeibeiDataset(Dataset):
    def __init__(self, file_path, user_col='user_id', item_col='item_id', label_col='label', sep=' ', num_negative=8, skiprows=1, encoding='latin1'):
        try:
            # Try reading with different parameters to handle potential issues
            self.data = pd.read_csv(
                file_path, 
                sep=sep, 
                header=None, 
                names=[user_col, item_col, label_col], 
                skiprows=skiprows, 
                encoding=encoding,
                on_bad_lines='skip',  # Skip problematic lines
                engine='python',      # Use Python engine instead of C
                quoting=3            # Turn off quote handling
            )
            
            # Create mappings
            self.user_map = {id_: idx for idx, id_ in enumerate(self.data[user_col].unique())}
            self.item_map = {id_: idx for idx, id_ in enumerate(self.data[item_col].unique())}
            
            # Map IDs
            self.data[user_col] = self.data[user_col].map(self.user_map)
            self.data[item_col] = self.data[item_col].map(self.item_map)
            
            self.num_users = len(self.user_map)
            self.num_items = len(self.item_map)
            self.num_negative = num_negative
            
            # Create user-items dictionary
            self.user_items = self.create_user_items_dict(user_col, item_col)
            
            # Add negative samples with improved sampling strategy
            self.data = self.add_negative_samples(user_col, item_col, label_col)
            
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            raise
        
    def create_user_items_dict(self, user_col, item_col):
        return {user_id: set(self.data[self.data[user_col] == user_id][item_col]) 
                for user_id in range(self.num_users)}
        
    def add_negative_samples(self, user_col, item_col, label_col):
        negative_samples = []
        all_items = set(range(self.num_items))
        
        # Calculate item popularity
        item_counts = self.data[item_col].value_counts()
        item_probs = 1 / (item_counts + 1)  # Add 1 to avoid division by zero
        item_probs = item_probs / item_probs.sum()
        
        for user_id in self.user_items:
            pos_items = self.user_items[user_id]
            neg_items = list(all_items - pos_items)
            
            if len(neg_items) > 0:
                # Calculate sampling probabilities for negative items
                neg_probs = item_probs[neg_items]
                neg_probs = neg_probs / neg_probs.sum()
                
                # Sample negative items based on popularity
                num_neg = min(len(neg_items), self.num_negative)
                sampled_neg = np.random.choice(
                    neg_items, 
                    size=num_neg, 
                    replace=False,
                    p=neg_probs
                )
                
                for item_id in sampled_neg:
                    negative_samples.append([user_id, item_id, 0])
        
        neg_df = pd.DataFrame(negative_samples, columns=[user_col, item_col, label_col])
        return pd.concat([self.data, neg_df], ignore_index=True).sample(frac=1)

    # Feature functions
    def get_user_count(self):
        return self.num_users

    def get_item_count(self):
        return self.num_items

    def get_interaction_count(self):
        return len(self.data)

    def get_user_interactions(self, user_id):
        return len(self.data[self.data['user_id'] == user_id])

    def get_item_interactions(self, item_id):
        return len(self.data[self.data['item_id'] == item_id])

    def get_user_item_matrix(self):
        return self.data.pivot(index='user_id', columns='item_id', values='label').fillna(0)

    def get_popular_items(self, top_n=10):
        return self.data['item_id'].value_counts().head(top_n)

    def get_active_users(self, top_n=10):
        return self.data['user_id'].value_counts().head(top_n)
    def get_sparsity(self):
        total_possible_interactions = self.num_users * self.num_items
        actual_interactions = len(self.data)
        return 1 - (actual_interactions / total_possible_interactions)

    def get_negative_samples(self, sample_size=10):
        negative_samples = self.data[self.data['label'] == 0]
        return negative_samples.sample(n=sample_size)

path = 'CRLearn/CRDS/beibei/'
files = ['trn_buy', 'trn_cart', 'trn_pv', 'tst_int']

def load():
    """Load all Beibei datasets."""
    check_and_download('beibei', base_path=path)

    datasets = {}
    if not os.path.exists(path):
        os.makedirs(path)
    for file in files:
        file_path = os.path.join(path, file)
        try:
            datasets[file] = BeibeiDataset(file_path)
            print(f"Successfully loaded {file}")
        except Exception as e:
            print(f"Failed to load {file}: {str(e)}")
    return datasets
