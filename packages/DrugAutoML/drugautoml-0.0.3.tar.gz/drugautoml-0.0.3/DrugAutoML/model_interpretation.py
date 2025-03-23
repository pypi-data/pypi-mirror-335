import os
import json
import logging
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, auc, precision_recall_curve, average_precision_score,
    classification_report, confusion_matrix
)

from model_selection import build_model
from data_splitting import split_data, load_and_merge_data

# LOG CONFIGURATION
results_folder = "results"
plots_folder = os.path.join(results_folder, "plots")
os.makedirs(plots_folder, exist_ok=True)

log_file = os.path.join(results_folder, "model_interpretation.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode="a")
    ]
)

def get_best_params(model_name):
    json_path = os.path.join(results_folder, f"best_params_{model_name}.json")
    if not os.path.exists(json_path):
        logging.error(f"Best params JSON file not found for model {model_name}: {json_path}")
        return None
    with open(json_path, "r") as f:
        best_params = json.load(f)
    logging.info(f"Best parameters for {model_name} loaded from {json_path}.")
    return best_params

def load_train_test_data():
    try:
        train_X = pd.read_csv(os.path.join(results_folder, "train_X.csv"))
        train_y = pd.read_csv(os.path.join(results_folder, "train_y.csv")).squeeze()
        test_X = pd.read_csv(os.path.join(results_folder, "test_X.csv"))
        test_y = pd.read_csv(os.path.join(results_folder, "test_y.csv")).squeeze()
        train_X = train_X.reset_index(drop=True)
        test_X = test_X.reset_index(drop=True)
        if isinstance(test_y, pd.Series):
            test_y = test_y.reset_index(drop=True)
        logging.info("Train and test data loaded and reindexed successfully.")
        return train_X, train_y, test_X, test_y
    except Exception as e:
        logging.error(f"Error loading train/test data: {e}")
        return None, None, None, None

def interpret_model(model_name, random_state=42):
    """
    For the selected model (e.g., "RF", "XGB", "LRC", "SVC", etc.):
      1. Load train/test data.
      2. Load best parameters from best_params_{model_name}.json.
      3. Retrain the model on the full training set.
      4. Evaluate the model on the test set, compute metrics, generate a classification report,
         confusion matrix, ROC & PRC curves, and a SHAP summary plot. All plots are saved.
      5. Save test set predictions (Actual, Predicted, Probability).
      6. Report active molecules (Actual == 1 and Predicted == 1) with key details.
    """
    train_X, train_y, test_X, test_y = load_train_test_data()
    if train_X is None or test_X is None:
        logging.error("Train or test data not available. Exiting interpretation.")
        return None

    best_params = get_best_params(model_name)
    if best_params is None:
        logging.error("No best parameters found. Exiting interpretation.")
        return None

    model = build_model(model_name, best_params)
    model.fit(train_X, train_y)
    logging.info(f"Model {model_name} trained on full training data.")

    test_preds = model.predict(test_X)
    try:
        test_probs = model.predict_proba(test_X)[:, 1]
    except Exception:
        try:
            test_probs = model.decision_function(test_X)
        except Exception:
            logging.warning("No predict_proba or decision_function available; using predictions as probabilities.")
            test_probs = test_preds.astype(float)

    acc = accuracy_score(test_y, test_preds)
    prec = precision_score(test_y, test_preds, zero_division=0)
    rec = recall_score(test_y, test_preds, zero_division=0)
    f1_val = f1_score(test_y, test_preds, zero_division=0)
    if len(np.unique(test_y)) == 1:
        roc_auc_val = np.nan
        prc_auc_val = np.nan
        logging.warning("Test set contains only one class. ROC AUC and PRC AUC cannot be computed.")
    else:
        fpr, tpr, _ = roc_curve(test_y, test_probs)
        roc_auc_val = auc(fpr, tpr)
        precision_curve, recall_curve, _ = precision_recall_curve(test_y, test_probs)
        prc_auc_val = average_precision_score(test_y, test_probs)

    performance = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1_val,
        "roc_auc": roc_auc_val,
        "prc_auc": prc_auc_val
    }
    perf_metrics_df = pd.DataFrame([performance])
    perf_metrics_path = os.path.join(results_folder, "performance_metrics.csv")
    perf_metrics_df.to_csv(perf_metrics_path, index=False)
    logging.info("Performance metrics saved.")

    class_report = classification_report(test_y, test_preds, target_names=["Inactive", "Active"])
    class_report_path = os.path.join(results_folder, "classification_report.txt")
    with open(class_report_path, "w") as f:
        f.write(class_report)
    logging.info("Classification report saved.")

    cm = confusion_matrix(test_y, test_preds, labels=[0, 1])
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Inactive", "Active"],
                yticklabels=["Inactive", "Active"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    cm_path = os.path.join(plots_folder, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    plt.clf()
    plt.close()
    logging.info("Confusion matrix saved.")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    if not np.isnan(roc_auc_val):
        axes[0].plot(fpr, tpr, label=f"ROC AUC = {roc_auc_val:.2f}")
        axes[0].plot([0, 1], [0, 1], "k--")
        axes[0].set_xlabel("False Positive Rate")
        axes[0].set_ylabel("True Positive Rate")
        axes[0].set_title("ROC Curve")
        axes[0].legend(loc="lower right")
    if not np.isnan(prc_auc_val):
        axes[1].plot(recall_curve, precision_curve, label=f"PRC AUC = {prc_auc_val:.2f}")
        axes[1].set_xlabel("Recall")
        axes[1].set_ylabel("Precision")
        axes[1].set_title("Precision-Recall Curve")
        axes[1].legend(loc="upper right")
    roc_prc_path = os.path.join(plots_folder, "roc_prc_curves.png")
    plt.tight_layout()
    plt.savefig(roc_prc_path, dpi=150)
    plt.clf()
    plt.close(fig)
    logging.info("ROC and PRC curves saved.")

    try:
        if model_name in ["RF", "ET", "XGB", "LGBM", "AB"]:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(test_X)
            shap_vals = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
            logging.info(f"TreeExplainer successful, SHAP values shape: {np.shape(shap_vals)}")
        elif model_name == "LRC":
            try:
                explainer = shap.LinearExplainer(model, train_X, feature_perturbation="interventional")
                shap_vals = explainer.shap_values(test_X)
                logging.info(f"LinearExplainer successful for {model_name}, SHAP values shape: {np.shape(shap_vals)}")
            except Exception as e:
                logging.warning(f"LinearExplainer failed for {model_name}: {e}. Falling back to KernelExplainer.")
                background = train_X.sample(n=min(100, len(train_X)), random_state=random_state)
                explainer = shap.KernelExplainer(model.predict_proba, background)
                shap_values = explainer.shap_values(test_X, nsamples=100)
                shap_vals = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
                logging.info(f"KernelExplainer fallback successful, SHAP values shape: {np.shape(shap_vals)}")
        elif model_name == "SVC":
            if hasattr(model, "coef_"):
                try:
                    explainer = shap.LinearExplainer(model, train_X, feature_perturbation="interventional")
                    shap_vals = explainer.shap_values(test_X)
                    logging.info(f"LinearExplainer successful for SVC, SHAP values shape: {np.shape(shap_vals)}")
                except Exception as e:
                    logging.warning(f"LinearExplainer failed for SVC: {e}. Using KernelExplainer instead.")
                    background = train_X.sample(n=min(100, len(train_X)), random_state=random_state)
                    explainer = shap.KernelExplainer(model.predict_proba, background)
                    shap_values = explainer.shap_values(test_X, nsamples=100)
                    shap_vals = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
                    logging.info(f"KernelExplainer fallback for SVC successful, SHAP values shape: {np.shape(shap_vals)}")
            else:
                background = train_X.sample(n=min(100, len(train_X)), random_state=random_state)
                explainer = shap.KernelExplainer(model.predict_proba, background)
                shap_values = explainer.shap_values(test_X, nsamples=100)
                shap_vals = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
                logging.info(f"KernelExplainer used for SVC, SHAP values shape: {np.shape(shap_vals)}")
        else:
            background = train_X.sample(n=min(100, len(train_X)), random_state=random_state)
            explainer = shap.KernelExplainer(model.predict_proba, background)
            shap_values = explainer.shap_values(test_X, nsamples=100)
            shap_vals = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
            logging.info(f"Default KernelExplainer used, SHAP values shape: {np.shape(shap_vals)}")

        plt.figure()
        shap.summary_plot(shap_vals, test_X, show=False)
        shap_path = os.path.join(plots_folder, "shap_summary.png")
        plt.savefig(shap_path, dpi=150, bbox_inches="tight")
        plt.clf()
        plt.close('all')
        logging.info(f"SHAP summary plot saved to {shap_path}")
    except Exception as e:
        logging.warning(f"SHAP explanation failed: {e}")
        shap_path = None

    predictions_df = pd.DataFrame({
        "Actual": test_y,
        "Predicted": test_preds,
        "Probability": test_probs
    })
    test_predictions_path = os.path.join(results_folder, "test_predictions.csv")
    predictions_df.to_csv(test_predictions_path, index=False)
    logging.info("Test predictions saved.")

    preprocessed_path = os.path.join(results_folder, "preprocessed_data.csv")
    active_report_path = None
    if os.path.exists(preprocessed_path):
        merged_df = load_and_merge_data()
        full_preprocessed_df = pd.read_csv(preprocessed_path)
        full_merged = pd.merge(merged_df, full_preprocessed_df, on="Smiles", how="left")
        test_indices = predictions_df.index
        test_merged = full_merged.loc[test_indices].copy()
        test_merged["Predicted"] = predictions_df["Predicted"].values
        test_merged["Actual"] = predictions_df["Actual"].values
        active_molecules = test_merged[(test_merged["Predicted"] == 1) & (test_merged["Actual"] == 1)]
        required_cols = ["Molecule ChEMBL ID", "Molecule Name", "Smiles", "Standard Value", "Predicted"]
        missing_cols = [col for col in required_cols if col not in active_molecules.columns]
        if missing_cols:
            logging.error(f"Missing columns for active report: {missing_cols}. Active report not generated.")
        else:
            active_report = active_molecules[required_cols]
            active_report_path = os.path.join(results_folder, "active_molecules_report.csv")
            active_report.to_csv(active_report_path, index=False)
            logging.info("Active molecules report saved.")
    else:
        logging.error("preprocessed_data.csv not found; active molecules report not generated.")

    logging.info("Model interpretation completed.")
    return {
        "best_params": best_params,
        "performance": performance,
        "classification_report_path": class_report_path,
        "confusion_matrix_path": cm_path,
        "roc_prc_curve_path": roc_prc_path,
        "shap_summary_path": shap_path,
        "test_predictions_path": test_predictions_path,
        "active_molecules_report_path": active_report_path
    }
