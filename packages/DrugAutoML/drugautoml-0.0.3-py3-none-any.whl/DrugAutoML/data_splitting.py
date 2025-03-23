import os
import pandas as pd
import logging
from sklearn.model_selection import train_test_split, StratifiedKFold

# ----------------------------------------------------------------------
# LOG CONFIGURATION
# ----------------------------------------------------------------------
results_folder = "results"
folds_folder = os.path.join(results_folder, "folds")

# Check if directories exist, and create them if they don't
for folder in [results_folder, folds_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

log_file = os.path.join(results_folder, "data_splitting.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)

# ----------------------------------------------------------------------
def load_and_merge_data():
    """
    Loads and merges the fingerprint_data.csv and preprocessed_data.csv files
    from the 'results' folder based on the 'Smiles' column. In the preprocessed data,
    the 'Response' column is label encoded: Active -> 1, Inactive -> 0.

    Returns:
        pd.DataFrame: Merged DataFrame containing fingerprint columns (X) and 'Response' (y).
    """
    fingerprint_path = os.path.join(results_folder, "fingerprint_data.csv")
    preprocessed_path = os.path.join(results_folder, "preprocessed_data.csv")

    fingerprint_df = pd.read_csv(fingerprint_path)
    preprocessed_df = pd.read_csv(preprocessed_path)

    # Label encoding: Active -> 1, Inactive -> 0
    preprocessed_df['Response'] = preprocessed_df['Response'].map({'Active': 1, 'Inactive': 0})

    # Merge on common 'Smiles' column
    merged_df = pd.merge(fingerprint_df, preprocessed_df[['Smiles', 'Response']], on='Smiles', how='inner')
    logging.info(f"Merged dataset shape: {merged_df.shape}")

    return merged_df


def create_and_save_folds(X, y, n_splits=5, random_state=42):
    """
    Performs n-fold cross-validation using StratifiedKFold and saves each fold's
    training and validation data as separate CSV files.

    For each fold:
      - Training data (X_train_fold, y_train_fold)
      - Validation data (X_val_fold, y_val_fold)

    Files are saved in the results/folds directory as:
      fold_i_train_X.csv, fold_i_train_y.csv, fold_i_val_X.csv, fold_i_val_y.csv

    Parameters:
        X (pd.DataFrame): Features for training.
        y (pd.Series): Labels for training.
        n_splits (int): Number of folds.
        random_state (int): Random state for reproducibility.

    Returns:
        list: A list of dictionaries containing fold information.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    folds = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), start=1):
        X_train_fold = X.iloc[train_idx]
        y_train_fold = y.iloc[train_idx]
        X_val_fold = X.iloc[val_idx]
        y_val_fold = y.iloc[val_idx]

        # File paths
        train_X_path = os.path.join(folds_folder, f"fold_{fold}_train_X.csv")
        train_y_path = os.path.join(folds_folder, f"fold_{fold}_train_y.csv")
        val_X_path = os.path.join(folds_folder, f"fold_{fold}_val_X.csv")
        val_y_path = os.path.join(folds_folder, f"fold_{fold}_val_y.csv")

        # Save files
        X_train_fold.to_csv(train_X_path, index=False)
        y_train_fold.to_csv(train_y_path, index=False)
        X_val_fold.to_csv(val_X_path, index=False)
        y_val_fold.to_csv(val_y_path, index=False)

        logging.info(f"Fold {fold} - Training samples: {X_train_fold.shape[0]}, Validation samples: {X_val_fold.shape[0]}")

        folds.append({
            "fold": fold,
            "train_X": X_train_fold,
            "train_y": y_train_fold,
            "val_X": X_val_fold,
            "val_y": y_val_fold
        })

    logging.info(f"{n_splits}-fold stratified CV created and saved.")
    return folds


def split_data(test_size=0.2, n_splits=5, random_state=42):
    """
    Combines all data preparation steps into a single function:
      1. Loads and merges fingerprint_data.csv and preprocessed_data.csv from the 'results' folder using the 'Smiles' column.
      2. Applies a stratified train-test split.
      3. Creates stratified n-fold CV and saves the folds.

    Parameters:
        test_size (float): Proportion of the data to use as test set.
        n_splits (int): Number of folds for cross-validation.
        random_state (int): Random state for reproducibility.

    Returns:
        dict: A dictionary containing:
          - 'X_train': Training features.
          - 'X_test': Test features.
          - 'y_train': Training labels.
          - 'y_test': Test labels.
          - 'folds': List of dictionaries with n-fold stratified CV fold details.
    """
    # 1. Load and merge data
    merged_df = load_and_merge_data()

    # Features (X): All columns except 'Smiles' and 'Response'
    X = merged_df.drop(columns=['Smiles', 'Response'])
    # Labels (y): Response column
    y = merged_df['Response']

    # 2. Perform stratified train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Save split data to the results folder
    X_train.to_csv(os.path.join(results_folder, "train_X.csv"), index=False)
    X_test.to_csv(os.path.join(results_folder, "test_X.csv"), index=False)
    y_train.to_csv(os.path.join(results_folder, "train_y.csv"), index=False)
    y_test.to_csv(os.path.join(results_folder, "test_y.csv"), index=False)

    logging.info(f"Training samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")

    # 3. Create stratified n-fold CV
    folds = create_and_save_folds(X_train, y_train, n_splits=n_splits, random_state=random_state)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "folds": folds
    }
