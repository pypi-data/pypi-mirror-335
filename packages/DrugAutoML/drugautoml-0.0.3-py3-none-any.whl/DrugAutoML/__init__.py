# DrugAutoML/__init__.py

__version__ = "0.0.3"

# Importing key functions from the package modules.
from .data_preprocessing import load_and_prepare_data
from .fingerprint_calculation import smiles_to_fingerprints
from .data_splitting import split_data
from .model_selection import run_model_selection, build_model
from .model_interpretation import interpret_model
