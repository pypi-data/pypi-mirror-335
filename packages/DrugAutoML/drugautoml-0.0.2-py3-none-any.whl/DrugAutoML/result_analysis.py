import os
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

from rdkit import Chem
from rdkit.Chem import AllChem, Draw

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, roc_curve, auc, precision_recall_curve,
    confusion_matrix, classification_report, matthews_corrcoef, cohen_kappa_score
)


def result_analysis(cv_results, train_df, test_df, model_choice=None, results_folder="results",
                    original_test_data=None, shap_path=None):
    """
    Retrains the selected (or majority-vote selected) model on the training data,
    evaluates it on the test data, and produces the following outputs:
      - A CSV file with test performance metrics.
      - A CSV file containing actual labels, predicted labels, and prediction probabilities.
      - Merges original molecular data with test results.
      - Generates side-by-side ROC and PRC curves in a single figure.
      - Generates a confusion matrix plot and saves the classification report.
      - Produces a SHAP summary plot displaying feature contributions.

    Parameters:
      cv_results (dict): CV results from the AutoML pipeline.
      train_df (pd.DataFrame): Training data with 'Response' and ECFP columns.
      test_df (pd.DataFrame): Test data with 'Response' and ECFP columns.
      model_choice (str, optional): Preferred model key; if not provided, the best model is chosen by majority vote.
      results_folder (str): Folder to save output files.
      original_test_data (pd.DataFrame, optional): Original preprocessed molecular data.
      shap_path (str, optional): File path to save the SHAP summary plot.

    Returns:
      tuple: (metrics_df, model_instance)
    """
    plt.style.use("ggplot")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # --- Model Selection ---
    if model_choice is None:
        metric_keys = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision", "mcc"]
        votes = {}
        for metric in metric_keys:
            best_val = -np.inf
            best_model_for_metric = None
            for model_name, res in cv_results.items():
                val = res["mean_metrics"].get(f"{metric}_cv_mean", -np.inf)
                if val > best_val:
                    best_val = val
                    best_model_for_metric = model_name
            votes[best_model_for_metric] = votes.get(best_model_for_metric, 0) + 1
        model_choice = max(votes.items(), key=lambda x: x[1])[0]
        print("Default best model selected by majority vote:", model_choice)
        print("Votes:", votes)
    else:
        print("User-selected model:", model_choice)

    if model_choice not in cv_results:
        raise ValueError(f"Model '{model_choice}' not found in cv_results. Available models: {list(cv_results.keys())}")

    selected_cv = cv_results[model_choice]
    model_instance = copy.deepcopy(selected_cv["best_model"]["learner"])
    model_instance.set_params(**selected_cv["best_params"])
    # No scaler is used since we preserve binary fingerprint values.

    # --- Prepare Training and Test Data ---
    X_train_df = train_df.drop(columns=["Response"]).copy()
    y_train = train_df["Response"]
    X_test_df = test_df.drop(columns=["Response"]).copy()
    y_test = test_df["Response"]
    # Use data as-is without scaling.

    # --- Train the Model ---
    model_instance.fit(X_train_df, y_train)
    y_pred = model_instance.predict(X_test_df)
    if hasattr(model_instance, "predict_proba"):
        y_prob = model_instance.predict_proba(X_test_df)[:, 1]
    else:
        decision = model_instance.decision_function(X_test_df)
        y_prob = 1 / (1 + np.exp(-decision))

    # --- Calculate Performance Metrics ---
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec_val = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc_val = roc_auc_score(y_test, y_prob)
    prc_auc_val = average_precision_score(y_test, y_prob)
    mcc = matthews_corrcoef(y_test, y_pred)
    kappa = cohen_kappa_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, zero_division=0)

    metrics_dict = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec_val,
        "F1": f1,
        "ROC-AUC": roc_auc_val,
        "PRC-AUC": prc_auc_val,
        "MCC": mcc,
        "Cohen's Kappa": kappa
    }
    metrics_df = pd.DataFrame([metrics_dict])
    metrics_csv = os.path.join(results_folder, "test_performance_metrics.csv")
    metrics_df.to_csv(metrics_csv, index=False)
    print("[INFO] Test performance metrics saved to", metrics_csv)

    predictions_df = pd.DataFrame({
        "Actual": y_test,
        "Predicted": y_pred,
        "Probability": y_prob
    })
    predictions_csv = os.path.join(results_folder, "test_predictions.csv")
    predictions_df.to_csv(predictions_csv, index=False)
    print("[INFO] Test predictions saved to", predictions_csv)

    # --- Generate Combined ROC and PRC Plot ---
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc_plot = auc(fpr, tpr)
    precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_prob)
    prc_auc_plot = auc(recall_vals, precision_vals)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    # ROC curve
    ax1.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc_plot:.3f})", lw=2)
    ax1.plot([0, 1], [0, 1], "k--", lw=1)
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title("ROC Curve")
    ax1.legend(loc="lower right")
    # PRC curve
    ax2.plot(recall_vals, precision_vals, label=f"PR curve (AP = {prc_auc_plot:.3f})", lw=2)
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.set_title("Precision-Recall Curve")
    ax2.legend(loc="lower left")
    plt.tight_layout()
    combined_path = os.path.join(results_folder, "roc_prc_combined.png")
    plt.savefig(combined_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("[INFO] ROC and PRC curves saved to", combined_path)

    # --- Confusion Matrix Plot ---
    plt.figure(figsize=(7.5, 6.2))
    plt.imshow(conf_matrix, cmap=plt.cm.Blues, interpolation='none', aspect='auto')
    plt.title("Confusion Matrix")
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ["Inactive", "Active"])
    plt.yticks(tick_marks, ["Inactive", "Active"])
    thresh = conf_matrix.max() / 2.
    for i in range(conf_matrix.shape[0]):
        for j in range(conf_matrix.shape[1]):
            plt.text(j, i, format(conf_matrix[i, j], "d"),
                     horizontalalignment="center",
                     color="darkred" if conf_matrix[i, j] > thresh else "black",
                     fontweight="bold")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    cm_path = os.path.join(results_folder, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("[INFO] Confusion matrix plot saved to", cm_path)

    # --- Save Classification Report ---
    report_path = os.path.join(results_folder, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write(class_report)
    print("[INFO] Classification report saved to", report_path)

    # --- SHAP Summary Plot ---
    try:
        if model_choice in ["RF", "ETs", "GB", "XGB", "LGBM"]:
            explainer = shap.TreeExplainer(model_instance)
        elif model_choice in ["LRC", "SGD"]:
            explainer = shap.LinearExplainer(model_instance, X_train_df, feature_perturbation="interventional")
        else:
            explainer = shap.KernelExplainer(lambda x: model_instance.predict(x), X_train_df)
        shap_values = explainer.shap_values(X_test_df)
        plt.figure(figsize=(6, 6))
        shap.summary_plot(shap_values, X_test_df, show=False, plot_type="dot")
        shap_summary_path = os.path.join(results_folder, "shap_summary.png")
        plt.savefig(shap_summary_path, dpi=300, bbox_inches="tight")
        plt.close()
        print("[INFO] SHAP summary plot saved to", shap_summary_path)
    except Exception as e:
        print("[WARNING] SHAP summary plot could not be generated:", e)

    return metrics_df, model_instance
