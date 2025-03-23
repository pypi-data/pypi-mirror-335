# DrugAutoML: An Open-Source Automated Machine Learning and Statistical Evaluation Tool for Bioactivity Prediction in Drug Discovery

**Version:** 0.0.3  
**License:** MIT  

---

## Overview

DrugAutoML is an open-source Python package designed to automate machine learning (ML) pipelines for bioactivity prediction in drug discovery. Unlike general-purpose AutoML frameworks, DrugAutoML integrates domain-specific data preprocessing, feature engineering, hyperparameter tuning, and model interpretation tailored to chemical and bioactivity datasets. It streamlines the entire workflow—from reading and cleaning raw data to generating interpretable models—making predictive modeling more accessible, reproducible, and transparent.

**Key highlights include:**
- **Automated Data Preprocessing:** Cleans and filters chemical data from ChEMBL, ensuring valid SMILES strings, consistent bioactivity units, and user-defined activity thresholds (e.g., IC50).  
- **Fingerprint Calculation:** Computes Extended Connectivity Fingerprints (ECFP4, 2048 bits) using RDKit for robust molecular feature representation.  
- **Stratified Data Splitting:** Performs stratified train–test splits and cross-validation folds to avoid data leakage and maintain class balance.  
- **Model Selection & Hyperparameter Optimization:** Evaluates multiple ML algorithms (e.g., Random Forest, XGBoost, LightGBM, SVC, etc.) via Bayesian optimization (Hyperopt) to maximize accuracy while minimizing computational cost.  
- **Performance Evaluation & Explainability:** Generates a wide range of performance metrics (e.g., ACC, PREC, REC, F1, ROC AUC, PRC AUC) and interprets predictions through SHAP, enabling insight into which molecular features drive bioactivity.  
- **Automated Reports & Visualizations:** Saves classification reports, confusion matrices, ROC & PRC curves, and SHAP plots, providing an end-to-end view of the modeling process.

---

## Background

**Why DrugAutoML?**  
Traditional drug discovery workflows are resource-intensive, often involving extensive experimental screening of chemical libraries. Machine learning approaches have gained popularity to expedite early-stage screening, but building reliable ML pipelines can be time-consuming and error-prone—especially when dealing with chemical structures and large-scale bioactivity data. General-purpose AutoML frameworks are not fully optimized for drug discovery tasks, lacking specialized preprocessing, domain-specific hyperparameter search spaces, and interpretability tools crucial for identifying relevant chemical features.

**How it works**  
1. **Data Input and Preprocessing (Module 1):** Loads SMILES and bioactivity data, cleans invalid or ambiguous entries, and applies user-defined thresholds (e.g., IC50 < 100 nM as "Active").  
2. **Fingerprint Calculation (Module 2):** Converts SMILES to ECFP4 fingerprints for machine-readable chemical representations.  
3. **Data Splitting (Module 3):** Ensures stratified train–test splits and creates cross-validation folds.  
4. **Model Selection (Module 4):** Tests multiple ML models with Bayesian hyperparameter optimization, automatically handling class imbalance.  
5. **Model Interpretation (Module 5):** Evaluates predictive performance (accuracy, precision, recall, etc.) and computes SHAP values to highlight feature contributions.

---

## Dependencies

- Python 3.6+
- RDKit
- NumPy, Pandas, scikit-learn
- XGBoost, LightGBM, Hyperopt
- Matplotlib, Seaborn, SHAP

(Most dependencies will install automatically upon package installation.)

---

## Quick Start

Below is a minimal example demonstrating a typical workflow:

```python
import DrugAutoML as da

# 1. Define the path to your CSV file and activity thresholds
file_path = "/path/to/your/chembl_data.csv"
ic50_thresholds = {"lower_cutoff": 100, "upper_cutoff": 1000}

# 2. Preprocess the data
preprocessed_df = da.load_and_prepare_data(file_path, ic50_thresholds)

# 3. Calculate ECFP4 fingerprints
fingerprint_df = da.smiles_to_fingerprints(preprocessed_df)

# 4. Split data into training/test sets and create CV folds
data_dict = da.split_data(test_size=0.2, n_splits=5)
folds = data_dict["folds"]

# 5. Run model selection (example with 3 iteration)
results = da.run_model_selection(folds=folds, models_to_run="auto", max_evals=3)

# 6. Interpret model performance on the test set
interpretation_results = da.interpret_model(model_name="XGB")

# 7. View results
print("Best Parameters:", interpretation_results["best_params"])
print("Test Set Performance:", interpretation_results["performance"])
```

---

## Detailed Modules

- **data_preprocessing:** Cleans CSV data, filters invalid SMILES, categorizes compounds into Active/Inactive.
- **fingerprint_calculation:** Converts SMILES strings into 2048-bit ECFP4 fingerprints.
- **data_splitting:** Performs stratified splits and cross-validation folds to prevent data leakage.
- **model_selection:** Hyperparameter optimization, performance logging, and best model parameter saving.
- **model_interpretation:** Re-trains models, evaluates test sets, generates reports, and computes SHAP values.

---

## License

DrugAutoML is released under the MIT License. You are free to use, modify, and distribute this software.

---

## Contributing

We welcome contributions and bug reports! Please submit issues or pull requests on our GitHub repository.

---

## More Information & Documentation

For detailed documentation, examples, source code, and additional resources, please visit our [GitHub repository](https://github.com/aycapmkcu/DrugAutoML).

---

Thank you for using DrugAutoML!

We hope DrugAutoML accelerates your drug discovery research by simplifying and automating key bioactivity modeling steps.