import os
import pandas as pd
from rdkit import Chem
import warnings
import logging
import re

warnings.filterwarnings("ignore", category=RuntimeWarning)
pd.options.display.max_columns = None
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1000)

# ---------------------------------------------------------
# LOG CONFIGURATION
# ---------------------------------------------------------
results_folder = "results"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

log_file = os.path.join(results_folder, "preprocessing.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)
# ---------------------------------------------------------

def load_and_prepare_data(file_path, ic50_thresholds):
    """
    Loads and prepares data from a CSV file.

    Steps:
      - Reads CSV file
      - Cleans quotes and whitespace in string columns
      - Validates SMILES strings and canonicalizes them
      - Filters records with 'nm' as Standard Units
      - Converts 'Standard Value' to numeric
      - Classifies activity based on IC50 thresholds (Active/Inactive/Gray Area)
      - Updates response using comments
      - Removes 'Gray Area' records and duplicates
      - Saves the final data to "results/preprocessed_data.csv"

    Parameters:
      file_path (str): Path to the input CSV file.
      ic50_thresholds (dict): Dictionary with keys 'lower_cutoff' and 'upper_cutoff'.

    Returns:
      pd.DataFrame: The cleaned and processed DataFrame.
    """

    columns = [
        'Molecule ChEMBL ID',
        'Molecule Name',
        'Smiles',
        'Comment',
        'Standard Type',
        'Standard Units',
        'Standard Relation',
        'Standard Value'
    ]

    # Read the CSV file
    data = pd.read_csv(file_path, sep=None, engine='python', usecols=columns)
    logging.info(f"Total molecules read from CSV: {len(data)}")

    # Clean quotes and whitespace in string columns
    data = data.apply(lambda col: col.str.replace('"', '').replace("'", "").str.strip()
                      if col.dtype == 'object' else col)

    # Drop rows with missing SMILES
    data = data.dropna(subset=['Smiles'])
    logging.info(f"Molecules after dropping missing SMILES: {len(data)}")

    # Remove invalid SMILES
    data = data[data['Smiles'].apply(lambda x: Chem.MolFromSmiles(x) is not None)]
    logging.info(f"Molecules after removing invalid SMILES: {len(data)}")

    # Keep only rows with Standard Units = 'nm'
    data = data[data['Standard Units'].str.strip().str.lower() == 'nm']
    logging.info(f"Molecules with 'nm' as Standard Units: {len(data)}")

    # Normalize Standard Relation symbols and convert Standard Value to numeric
    data['Standard Relation'] = data['Standard Relation'].replace({'>>': '>', '<<': '<'}, regex=False)
    data['Standard Value'] = pd.to_numeric(data['Standard Value'], errors='coerce')
    data = data.dropna(subset=['Standard Value'])
    logging.info(f"Molecules after converting Standard Value to numeric: {len(data)}")

    # Clean and standardize SMILES
    data['Smiles'] = data['Smiles'].apply(clean_and_standardize_smiles)
    data = data.dropna(subset=['Smiles'])
    logging.info(f"Molecules after SMILES cleaning: {len(data)}")

    # Classify activity
    data = classify_activity(data, ic50_thresholds)

    # Update responses using comments
    data = update_response_with_comments(data)

    # Keep only rows outside the Gray Area
    data = data[data['Response'] != 'Gray Area'].reset_index(drop=True)
    logging.info(f"Molecules outside of 'Gray Area': {len(data)}")

    # Remove duplicates based on SMILES and Molecule ChEMBL ID
    data = data.drop_duplicates(subset=['Smiles', 'Molecule ChEMBL ID']).reset_index(drop=True)
    logging.info(f"Molecules after removing duplicates: {len(data)}")

    # Log summary
    active_count = (data['Response'] == 'Active').sum()
    inactive_count = (data['Response'] == 'Inactive').sum()
    total = len(data)
    if total > 0:
        logging.info(f"Active molecules: {active_count} ({100 * active_count / total:.2f}%), "
                     f"Inactive molecules: {inactive_count} ({100 * inactive_count / total:.2f}%)")
    else:
        logging.info("No molecules left after processing.")

    # Save final data to CSV
    output_path = os.path.join(results_folder, "preprocessed_data.csv")
    data.to_csv(output_path, index=False)
    logging.info(f"Preprocessed data saved to {output_path}")

    return data

def classify_activity(df, thresholds):
    """
    Classifies compounds in the DataFrame based on their 'Standard Value'
    (Active, Inactive, Gray Area).
    """
    df['Response'] = 'Gray Area'
    df.loc[df['Standard Value'] < thresholds['lower_cutoff'], 'Response'] = 'Active'
    df.loc[df['Standard Value'] > thresholds['upper_cutoff'], 'Response'] = 'Inactive'
    return df

def update_response_with_comments(df):
    """
    Updates the 'Response' column based on keywords found in the 'Comment' column.
    """
    inactive_terms = ['not active', 'inactive', 'no activity', 'lack of activity', 'failed']
    active_terms = ['active', 'potent', 'good activity']

    inactive_pattern = r'\b(?:' + '|'.join(map(re.escape, inactive_terms)) + r')\b'
    active_pattern = r'\b(?:' + '|'.join(map(re.escape, active_terms)) + r')\b'

    df.loc[df['Comment'].str.contains(inactive_pattern, flags=re.IGNORECASE, na=False), 'Response'] = 'Inactive'
    df.loc[df['Comment'].str.contains(active_pattern, flags=re.IGNORECASE, na=False), 'Response'] = 'Active'

    return df

def clean_and_standardize_smiles(smiles):
    """
    Parses the SMILES string with RDKit, selects the largest fragment, and
    generates a canonical SMILES. Returns None if there's an error.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None
        largest_frag = max(Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True), key=lambda m: m.GetNumAtoms())
        return Chem.MolToSmiles(largest_frag, canonical=True)
    except Exception as e:
        logging.warning(f"Error cleaning SMILES: {e}")
        return None
