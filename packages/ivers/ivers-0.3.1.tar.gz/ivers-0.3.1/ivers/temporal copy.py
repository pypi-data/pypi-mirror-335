"""
Filename: temporal.py

Code for the "leaky" and "AllForOne" splits

Functions "leaky_endpoint_split" and "allforone_endpoint_split" used when
only generate one test/train split

Functions "allforone_folds_endpoint_split" and "leaky_folds_endpoint_split"
where it is possible split data into multiple sections and concistently 
increase the train set

Author: Philip Ivers Ohlsson
License: MIT License 
"""

import pandas as pd
from pandas import DataFrame
import logging
from typing import Tuple, List, Dict
import numpy as np
import os
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def allforone_folds_endpoint_split(df: DataFrame, num_folds: int, smiles_column: str, 
                                    endpoint_date_columns: Dict[str, str], chemprop: bool, 
                                    save_path: str, aggregation: str, 
                                    feature_columns: List[str] = None) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Splits a DataFrame into multiple train/test sets (folds) with progressively increasing training data.
    
    For each fold, the test set size is reduced progressively based on the fold index, and the split is 
    determined by aggregating endpoint dates according to the specified aggregation method. Optionally, if 
    chemprop processing is enabled, the function extracts the specified feature columns to save separate 
    feature and target CSV files for each fold.
    
    Args:
        df: The input DataFrame containing compound data.
        num_folds: The number of folds for the cross-validation split.
        smiles_column: Name of the column containing compound identifiers (e.g., SMILES strings).
        endpoint_date_columns: Dictionary mapping endpoint names to their respective date columns.
        chemprop: Boolean flag indicating whether the output is intended for chemprop processing.
        save_path: Directory path to save the resulting CSV files for each fold.
        aggregation: Method to aggregate date values; must be one of 'first', 'last', or 'avg'.
        feature_columns: List of feature column names to extract (required if chemprop is True).
    
    Returns:
        A list of tuples, each containing the training and testing DataFrames for a fold.
    """
    if aggregation not in ['first', 'last', 'avg']:
        raise ValueError("Aggregation method must be 'first', 'last', or 'avg'.")
    cv_splits = []
    for fold in range(1, num_folds + 1):
        # Decrease the test size progressively: later folds have larger training sets.
        split_size = 1 - (fold / (num_folds + 1))
        
        # Generate the train/test split using the allforone_endpoint_split function.
        train_df, test_df = allforone_endpoint_split(df, split_size, smiles_column, endpoint_date_columns, aggregation)

        if chemprop:
            if feature_columns is None:
                raise ValueError("feature_columns must be provided when chemprop is True.")
            # Extract features using the helper function.
            train_features = extract_features(train_df, smiles_column, feature_columns)
            test_features = extract_features(test_df, smiles_column, feature_columns)
            # Define target sets including the smiles and endpoint columns.
            train_targets = train_df[[smiles_column] + list(endpoint_date_columns.keys())]
            test_targets = test_df[[smiles_column] + list(endpoint_date_columns.keys())]

            # Save features and targets as CSV files.
            train_features.to_csv(os.path.join(save_path, f'train_features_fold{fold}.csv'), index=False)
            test_features.to_csv(os.path.join(save_path, f'test_features_fold{fold}.csv'), index=False)
            train_targets.to_csv(os.path.join(save_path, f'train_targets_fold{fold}.csv'), index=False)
            test_targets.to_csv(os.path.join(save_path, f'test_targets_fold{fold}.csv'), index=False)
        else:
            # Save complete train/test DataFrames.
            train_df.to_csv(os.path.join(save_path, f'train_fold{fold}.csv'), index=False)
            test_df.to_csv(os.path.join(save_path, f'test_fold{fold}.csv'), index=False)

        cv_splits.append((train_df, test_df))

    return cv_splits

def extract_features(df: pd.DataFrame, smiles_column: str, feature_columns: List[str]) -> pd.DataFrame:
    """
    Extract features from the DataFrame.

    Args:
        df: The original DataFrame.
        smiles_column: Column name containing the SMILES strings.
        feature_columns: List of columns to be used as features.

    Returns:
        A DataFrame containing the SMILES and features.
    """
    return df[[smiles_column] + feature_columns]

def leaky_folds_endpoint_split(df: DataFrame, num_folds: int, smiles_column: str, endpoint_date_columns: Dict[str, str], chemprop: bool, save_path: str, feature_columns: List[str] = None) -> List[Tuple[DataFrame, DataFrame]]: 
    """
    Process a DataFrame by splitting it into multiple train/test sets for cross-validation, with the training set growing progressively.
    The size of the test set decreases with each fold, increasing the training data size.

    Args:
        df: DataFrame to be processed.
        num_folds: Number of folds for cross-validation.
        smiles_column: Name of the column containing compound identifiers.
        endpoint_date_columns: Dictionary of endpoint names to their respective date columns.
        chemprop: Boolean to indicate if data is for chemprop.
        save_path: Path to save the resulting dataframes.
        feature_columns: List of columns to be used as features.
    Returns:
        List of tuples containing training and testing DataFrames for each fold.
    """
    splits = []
    df = expand_df_to_endpoints(df, endpoint_date_columns)

    # test comment
    for fold in range(1, num_folds + 1 ):
        split_size = 1 - (fold / (num_folds + 1))  # Decrease the test size progressively
        
        # Use the leaky_endpoint_split function to generate each fold's split
        train_df, test_df = leaky_endpoint_split(df, split_size, smiles_column, endpoint_date_columns)
        
        if chemprop:
            train_features = extract_features(train_df, smiles_column, feature_columns)
            test_features = extract_features(test_df, smiles_column, feature_columns)

            # Include smiles_column in the targets
            train_targets = train_df[[smiles_column] + list(endpoint_date_columns.keys())]
            test_targets = test_df[[smiles_column] + list(endpoint_date_columns.keys())]

            # Save features and targets
            train_features.to_csv(os.path.join(save_path, f'train_features_fold{fold}.csv'), index=False)
            test_features.to_csv(os.path.join(save_path, f'test_features_fold{fold}.csv'), index=False)
            train_targets.to_csv(os.path.join(save_path, f'train_targets_fold{fold}.csv'), index=False)
            test_targets.to_csv(os.path.join(save_path, f'test_targets_fold{fold}.csv'), index=False)
        else:
            desired_columns = [smiles_column] + list(endpoint_date_columns.keys()) + feature_columns

            # Then subset the DataFrames before writing them to CSV.
            print(f"Desired columns: {desired_columns}")
            train_df = train_df[desired_columns]
            test_df = test_df[desired_columns]

            train_df.to_csv(os.path.join(save_path, f'train_fold{fold}.csv'), index=False)
            test_df.to_csv(os.path.join(save_path, f'test_fold{fold}.csv'), index=False)


        splits.append((train_df, test_df))

    return splits
