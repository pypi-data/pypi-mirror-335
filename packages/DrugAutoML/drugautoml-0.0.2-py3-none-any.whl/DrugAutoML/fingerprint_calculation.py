import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
import logging

# ----------------------------------------------------------------------
# LOG CONFIGURATION
# ----------------------------------------------------------------------
results_folder = "results"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

log_file = os.path.join(results_folder, "fingerprint.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)


# ----------------------------------------------------------------------

def get_fingerprint(mol):
    """
    Generates a Morgan (ECFP4, 2048-bit) fingerprint for the given molecule
    using rdFingerprintGenerator.

    Parameters:
        mol (rdkit.Chem.rdchem.Mol): RDKit molecule object.

    Returns:
        list: A list of bits (0/1) representing the 2048-bit ECFP4 fingerprint.
    """
    # Explicitly pass the required parameters:
    # radius = 2, countSimulation=False, includeChirality=False,
    # useBondTypes=True, onlyNonzeroInvariants=False, includeRingMembership=True,
    # countBounds=None, fpSize=2048.
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=2,  # ECFP radius
        countSimulation=False,
        includeChirality=False,
        useBondTypes=True,
        onlyNonzeroInvariants=False,
        includeRingMembership=True,
        countBounds=None,
        fpSize=2048
    )
    fp = generator.GetFingerprint(mol)
    return list(fp)


def smiles_to_fingerprints(df, smiles_col='Smiles'):
    """
    Calculates the Morgan (ECFP4, 2048-bit) fingerprint for each SMILES string
    in the given DataFrame using rdFingerprintGenerator, and saves the results.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing SMILES strings.
        smiles_col (str): Column name in df that contains SMILES strings.

    Returns:
        pd.DataFrame: DataFrame containing SMILES and the 2048-bit ECFP4 fingerprints.
    """
    logging.info("Starting fingerprint calculation.")
    logging.info(f"DataFrame has {len(df)} rows.")

    fingerprints = []
    invalid_count = 0

    for index, row in df.iterrows():
        smiles = row[smiles_col]
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logging.warning(f"Invalid SMILES encountered at row {index}: {smiles}")
            invalid_count += 1
            continue

        bit_list = get_fingerprint(mol)
        fingerprint_data = [smiles] + bit_list
        if index == 0:
            # Prepare column names only once
            column_names = ["Smiles"] + [f"ECFP{i + 1}" for i in range(len(bit_list))]
        fingerprints.append(fingerprint_data)

    if invalid_count > 0:
        logging.info(f"Total invalid SMILES encountered: {invalid_count}")

    if not fingerprints:
        logging.warning("No valid fingerprints were generated.")
        return pd.DataFrame()

    fingerprint_df = pd.DataFrame(fingerprints, columns=column_names)

    output_path = os.path.join(results_folder, "fingerprint_data.csv")
    fingerprint_df.to_csv(output_path, index=False)
    logging.info(f"Fingerprint data saved to {output_path}")
    logging.info(f"Fingerprint calculation completed. Final DataFrame size: {len(fingerprint_df)}")

    return fingerprint_df
