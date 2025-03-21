import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, auc, precision_recall_curve, average_precision_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from hyperopt import fmin, tpe, hp, Trials, STATUS_OK

# ---------------------------------------------------------------------
# LOG CONFIGURATION
# ---------------------------------------------------------------------
results_folder = "results"
plots_folder = os.path.join(results_folder, "plots")
os.makedirs(plots_folder, exist_ok=True)

log_file = os.path.join(results_folder, "model_selection.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)

# ---------------------------------------------------------------------
# SEARCH SPACES & OBJECTIVE FUNCTIONS
# ---------------------------------------------------------------------
# 1. Logistic Regression (LRC)
space_lrc = {
    'C': hp.loguniform('C', np.log(1), np.log(4)),
    'penalty': hp.choice('penalty', ['l1', 'l2']),
    'class_weight': hp.choice('class_weight', [None, 'balanced'])
}
def objective_lrc(params, X_train, y_train, X_val, y_val):
    model = LogisticRegression(
        C=params['C'],
        penalty=params['penalty'],
        solver='liblinear',
        max_iter=5000,
        class_weight=params['class_weight'],
        dual=False
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 2. Random Forest (RF)
space_rf = {
    'n_estimators': hp.choice('n_estimators', [100, 200, 300, 500]),
    'max_depth': hp.choice('max_depth', [None, 20, 30]),
    'max_features': hp.choice('max_features', ['sqrt', 'log2']),
    'class_weight': hp.choice('class_weight', [None, 'balanced'])
}
def objective_rf(params, X_train, y_train, X_val, y_val):
    model = RandomForestClassifier(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        max_features=params['max_features'],
        class_weight=params['class_weight']
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 3. Extra Trees (ET)
space_et = {
    'n_estimators': hp.choice('n_estimators', [100, 200, 300, 500]),
    'max_depth': hp.choice('max_depth', [None, 20, 30]),
    'max_features': hp.choice('max_features', ['sqrt', 'log2']),
    'class_weight': hp.choice('class_weight', [None, 'balanced'])
}
def objective_et(params, X_train, y_train, X_val, y_val):
    model = ExtraTreesClassifier(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        max_features=params['max_features'],
        class_weight=params['class_weight']
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 4. Support Vector Classifier (SVC)
space_svc = {
    'C': hp.loguniform('C', np.log(10), np.log(100)),
    'gamma': hp.loguniform('gamma', np.log(1e-4), np.log(0.05)),
    'kernel': hp.choice('kernel', ['linear', 'rbf']),
    'class_weight': hp.choice('class_weight', [None, 'balanced'])
}
def objective_svc(params, X_train, y_train, X_val, y_val):
    model = SVC(
        C=params['C'],
        kernel=params['kernel'],
        gamma=params['gamma'],
        class_weight=params['class_weight'],
        probability=True
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 5. AdaBoost (AB)
space_ab = {
    'n_estimators': hp.choice('n_estimators', [200, 300, 400]),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.5), np.log(1)),
    'base_class_weight': hp.choice('base_class_weight', [None, 'balanced'])
}
def objective_ab(params, X_train, y_train, X_val, y_val):
    base_est = DecisionTreeClassifier(max_depth=1, class_weight=params['base_class_weight'])
    model = AdaBoostClassifier(
        estimator=base_est,
        n_estimators=params['n_estimators'],
        learning_rate=params['learning_rate']
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 6. XGBoost (XGB)
space_xgb = {
    'max_depth': hp.choice('max_depth', [5, 6, 7]),
    'n_estimators': hp.choice('n_estimators', [150, 200, 250, 300]),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.01), np.log(0.3)),
    'gamma': hp.loguniform('gamma', np.log(0.001), np.log(0.05)),
    'subsample': hp.uniform('subsample', 0.6, 0.9),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.6, 0.9),
    'scale_pos_weight': hp.loguniform('scale_pos_weight', np.log(1.0), np.log(3.0))
}
def objective_xgb(params, X_train, y_train, X_val, y_val):
    model = XGBClassifier(
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        n_estimators=params['n_estimators'],
        gamma=params['gamma'],
        subsample=params['subsample'],
        colsample_bytree=params['colsample_bytree'],
        scale_pos_weight=params['scale_pos_weight'],
        eval_metric='logloss',
        verbosity=0
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# 7. LightGBM (LGBM)
space_lgbm = {
    'n_estimators': hp.choice('n_estimators', [500, 600]),
    'max_depth': hp.choice('max_depth', [None, 10]),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.05), np.log(0.08)),
    'num_leaves': hp.choice('num_leaves', [127]),
    'scale_pos_weight': hp.loguniform('scale_pos_weight', np.log(3.5), np.log(4.5))
}
def objective_lgbm(params, X_train, y_train, X_val, y_val):
    model = LGBMClassifier(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        num_leaves=params['num_leaves'],
        scale_pos_weight=params['scale_pos_weight'],
        eval_metric='logloss',
        verbose=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return {'loss': -acc, 'status': STATUS_OK}

# ---------------------------------------------------------------------
# BUILD MODEL FROM BEST PARAMETERS
# ---------------------------------------------------------------------
def build_model(model_name, best_params):
    if model_name == 'LRC':
        model = LogisticRegression(
            C=best_params['C'],
            penalty=best_params['penalty'],
            solver='liblinear',
            max_iter=5000,
            class_weight=best_params['class_weight'],
            dual=False
        )
    elif model_name == 'RF':
        model = RandomForestClassifier(
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            max_features=best_params['max_features'],
            class_weight=best_params['class_weight']
        )
    elif model_name == 'ET':
        model = ExtraTreesClassifier(
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            max_features=best_params['max_features'],
            class_weight=best_params['class_weight']
        )
    elif model_name == 'SVC':
        model = SVC(
            C=best_params['C'],
            kernel=best_params['kernel'],
            gamma=best_params['gamma'],
            class_weight=best_params['class_weight'],
            probability=True
        )
    elif model_name == 'AB':
        base_est = DecisionTreeClassifier(max_depth=1, class_weight=best_params['base_class_weight'])
        model = AdaBoostClassifier(
            estimator=base_est,
            n_estimators=best_params['n_estimators'],
            learning_rate=best_params['learning_rate']
        )
    elif model_name == 'XGB':
        model = XGBClassifier(
            max_depth=best_params['max_depth'],
            learning_rate=best_params['learning_rate'],
            n_estimators=best_params['n_estimators'],
            gamma=best_params['gamma'],
            subsample=best_params['subsample'],
            colsample_bytree=best_params['colsample_bytree'],
            scale_pos_weight=best_params['scale_pos_weight'],
            eval_metric='logloss',
            verbosity=0
        )
    elif model_name == 'LGBM':
        model = LGBMClassifier(
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            learning_rate=best_params['learning_rate'],
            num_leaves=best_params['num_leaves'],
            scale_pos_weight=best_params['scale_pos_weight'],
            eval_metric='logloss',
            verbose=-1
        )
    else:
        raise ValueError(f"Unknown model name: {model_name}")
    return model

# ---------------------------------------------------------------------
# MAIN FUNCTION: RUN MODEL SELECTION
# ---------------------------------------------------------------------
def run_model_selection(folds, models_to_run=None, max_evals=20, random_state=42):
    """
    Runs hyperparameter optimization (Hyperopt) for each model on each fold.
    Evaluates metrics: Accuracy, Precision, Recall, F1, ROC AUC, PRC AUC.
    For each model:
      - Plots individual ROC & PRC curves for each fold (no average curves).
      - Saves per-fold validation results to CSV.
      - Creates side-by-side bar charts for metric pairs:
         (Accuracy, F1), (Precision, Recall), (ROC AUC, PRC AUC)
        with error bars (std) and labeling only the mean (3 decimals) on top.
      - Additionally, for each model, the best hyperparameters (based on highest accuracy across folds)
        are saved as a JSON file in the results folder.
    """
    if models_to_run is None or models_to_run == "auto":
        models_to_run = ["LRC", "RF", "ET", "SVC", "AB", "XGB", "LGBM"]

    model_configs = {
        "LRC": (space_lrc, objective_lrc),
        "RF": (space_rf, objective_rf),
        "ET": (space_et, objective_et),
        "SVC": (space_svc, objective_svc),
        "AB":  (space_ab, objective_ab),
        "XGB": (space_xgb, objective_xgb),
        "LGBM": (space_lgbm, objective_lgbm)
    }

    all_metrics = []
    metric_names = ["accuracy", "precision", "recall", "f1", "roc_auc", "prc_auc"]

    # 1) Hyperopt & Fold-Based Training
    for model_name in models_to_run:
        logging.info(f"Starting model: {model_name}")
        space, objective_func = model_configs[model_name]
        roc_curves = []
        prc_curves = []

        for fold_dict in folds:
            fold_id = fold_dict["fold"]
            X_train_fold = fold_dict["train_X"]
            y_train_fold = fold_dict["train_y"]
            X_val_fold = fold_dict["val_X"]
            y_val_fold = fold_dict["val_y"]

            def hyperopt_objective(params):
                return objective_func(params, X_train_fold, y_train_fold, X_val_fold, y_val_fold)

            trials = Trials()
            best = fmin(
                fn=hyperopt_objective,
                space=space,
                algo=tpe.suggest,
                max_evals=max_evals,
                trials=trials,
                rstate=np.random.default_rng(random_state)
            )

            # Map hyperopt indices to actual values
            if model_name == "LRC":
                penalty_opts = ['l1', 'l2']
                class_weight_opts = [None, 'balanced']
                best['penalty'] = penalty_opts[int(best['penalty'])]
                best['class_weight'] = class_weight_opts[int(best['class_weight'])]
            if model_name == "RF":
                n_estimators_opts = [100, 200, 300, 500]
                max_depth_opts = [None, 20, 30]
                max_features_opts = ['sqrt', 'log2']
                class_weight_opts = [None, 'balanced']
                best['n_estimators'] = n_estimators_opts[int(best['n_estimators'])]
                best['max_depth'] = max_depth_opts[int(best['max_depth'])]
                best['max_features'] = max_features_opts[int(best['max_features'])]
                best['class_weight'] = class_weight_opts[int(best['class_weight'])]
            if model_name == "ET":
                n_estimators_opts = [100, 200, 300, 500]
                max_depth_opts = [None, 20, 30]
                max_features_opts = ['sqrt', 'log2']
                class_weight_opts = [None, 'balanced']
                best['n_estimators'] = n_estimators_opts[int(best['n_estimators'])]
                best['max_depth'] = max_depth_opts[int(best['max_depth'])]
                best['max_features'] = max_features_opts[int(best['max_features'])]
                best['class_weight'] = class_weight_opts[int(best['class_weight'])]
            if model_name == "SVC":
                kernel_opts = ['linear', 'rbf']
                class_weight_opts = [None, 'balanced']
                best['kernel'] = kernel_opts[int(best['kernel'])]
                best['class_weight'] = class_weight_opts[int(best['class_weight'])]
            if model_name == "AB":
                n_estimators_opts = [200, 300, 400]
                base_class_weight_opts = [None, 'balanced']
                best['n_estimators'] = n_estimators_opts[int(best['n_estimators'])]
                best['base_class_weight'] = base_class_weight_opts[int(best['base_class_weight'])]
            if model_name == "XGB":
                max_depth_opts = [5, 6, 7]
                n_estimators_opts = [150, 200, 250, 300]
                best['max_depth'] = max_depth_opts[int(best['max_depth'])]
                best['n_estimators'] = n_estimators_opts[int(best['n_estimators'])]
            if model_name == "LGBM":
                n_estimators_opts = [500, 600]
                max_depth_opts = [None, 10]
                num_leaves_opts = [127]
                best['n_estimators'] = n_estimators_opts[int(best['n_estimators'])]
                best['max_depth'] = max_depth_opts[int(best['max_depth'])]
                best['num_leaves'] = num_leaves_opts[int(best['num_leaves'])]

            best_model = build_model(model_name, best)
            best_model.fit(X_train_fold, y_train_fold)
            val_preds = best_model.predict(X_val_fold)
            try:
                val_probs = best_model.predict_proba(X_val_fold)[:, 1]
            except:
                try:
                    val_probs = best_model.decision_function(X_val_fold)
                except:
                    logging.warning("No predict_proba or decision_function; using binary preds for AUC")
                    val_probs = val_preds

            acc = accuracy_score(y_val_fold, val_preds)
            prec = precision_score(y_val_fold, val_preds, zero_division=0)
            rec = recall_score(y_val_fold, val_preds, zero_division=0)
            f1_val = f1_score(y_val_fold, val_preds, zero_division=0)
            if len(np.unique(y_val_fold)) == 1:
                roc_auc_val = np.nan
                prc_auc_val = np.nan
                logging.warning(f"Fold {fold_id} for {model_name}: Only one class in validation set.")
            else:
                fpr, tpr, _ = roc_curve(y_val_fold, val_probs)
                roc_auc_val = auc(fpr, tpr)
                precision_curve, recall_curve, _ = precision_recall_curve(y_val_fold, val_probs)
                prc_auc_val = average_precision_score(y_val_fold, val_probs)

            roc_curves.append((fpr, tpr, roc_auc_val, fold_id))
            prc_curves.append((recall_curve, precision_curve, prc_auc_val, fold_id))

            metrics_dict = {
                "model": model_name,
                "fold": fold_id,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1": f1_val,
                "roc_auc": roc_auc_val,
                "prc_auc": prc_auc_val,
                "best_params": best
            }
            all_metrics.append(metrics_dict)

        # Plot ROC & PRC curves for the current model
        sns.set(style="whitegrid", font_scale=1.2)
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        for fpr, tpr, roc_auc_val, fold_id in roc_curves:
            axes[0].plot(fpr, tpr, lw=2, label=f"Fold {fold_id} (AUC={roc_auc_val:.2f})")
        axes[0].plot([0, 1], [0, 1], 'k--', lw=2)
        axes[0].set_xlabel("False Positive Rate", fontsize=14)
        axes[0].set_ylabel("True Positive Rate", fontsize=14)
        axes[0].legend(loc="lower right", fontsize=12)
        for recall_curve, precision_curve, prc_auc_val, fold_id in prc_curves:
            axes[1].plot(recall_curve, precision_curve, lw=2, label=f"Fold {fold_id} (AUC={prc_auc_val:.2f})")
        axes[1].set_xlabel("Recall", fontsize=14)
        axes[1].set_ylabel("Precision", fontsize=14)
        axes[1].legend(loc="lower left", fontsize=12)
        plt.tight_layout()
        plot_path = os.path.join(plots_folder, f"{model_name}_combined_roc_prc.png")
        plt.savefig(plot_path, dpi=150)
        plt.close(fig)

        # ----- Yeni: Her model için, fold sonuçları arasından en iyi accuracy'ye sahip fold'un best_params'ını seçip JSON'a kaydediyoruz. -----
        model_results = [m for m in all_metrics if m["model"] == model_name]
        if model_results:
            best_model_result = max(model_results, key=lambda x: x["accuracy"])
            json_path = os.path.join(results_folder, f"best_params_{model_name}.json")
            with open(json_path, "w") as fp:
                json.dump(best_model_result["best_params"], fp, indent=4)
            logging.info(f"Best parameters for model {model_name} saved to {json_path}")
        # ------------------------------------------------------------------------------------------------------------

    # 3) Save per-fold validation results for each metric
    results_df = pd.DataFrame(all_metrics)
    for metric in metric_names:
        metric_df = results_df[['model', 'fold', metric]]
        metric_file = os.path.join(results_folder, f"validation_{metric}.csv")
        metric_df.to_csv(metric_file, index=False)
        logging.info(f"Validation results for {metric} saved to {metric_file}")

    # 4) Create summary (mean ± std)
    summary_df = results_df.groupby("model")[metric_names].agg(['mean', 'std'])
    summary_path = os.path.join(results_folder, "validation_summary.csv")
    summary_df.to_csv(summary_path)
    logging.info(f"Validation summary saved to {summary_path}")

    # 5) Generate side-by-side bar charts for metric pairs
    metric_pairs = [
        ("accuracy", "f1"),
        ("precision", "recall"),
        ("roc_auc", "prc_auc")
    ]
    nice_names = {
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1",
        "roc_auc": "ROC AUC",
        "prc_auc": "PRC AUC"
    }
    sns.set(style="whitegrid", font_scale=1.2)
    for left_metric, right_metric in metric_pairs:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        # LEFT METRIC
        left_sorted = summary_df.sort_values(by=(left_metric, 'mean'), ascending=False)
        left_models = left_sorted.index.tolist()
        left_means = left_sorted[(left_metric, 'mean')].values
        left_stds = left_sorted[(left_metric, 'std')].values
        left_palette = sns.color_palette("Dark2", len(left_models))
        ax_left = axes[0]
        x_left = np.arange(len(left_models))
        bars_left = ax_left.bar(
            x_left, left_means, yerr=left_stds, capsize=5,
            color=left_palette, alpha=0.9
        )
        for idx, rect in enumerate(bars_left):
            height = rect.get_height()
            ax_left.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.03,
                f"{height:.3f}",
                ha='center', va='bottom', fontsize=10
            )
        ax_left.set_xticks(x_left)
        ax_left.set_xticklabels(left_models, rotation=45, ha="right", fontsize=11)
        ax_left.set_ylabel(f"Mean {nice_names[left_metric]} Value", fontsize=12)
        ax_left.set_ylim([0, 1.05])
        # RIGHT METRIC
        right_sorted = summary_df.sort_values(by=(right_metric, 'mean'), ascending=False)
        right_models = right_sorted.index.tolist()
        right_means = right_sorted[(right_metric, 'mean')].values
        right_stds = right_sorted[(right_metric, 'std')].values
        right_palette = sns.color_palette("Dark2", len(right_models))
        ax_right = axes[1]
        x_right = np.arange(len(right_models))
        bars_right = ax_right.bar(
            x_right, right_means, yerr=right_stds, capsize=5,
            color=right_palette, alpha=0.9
        )
        for idx, rect in enumerate(bars_right):
            height = rect.get_height()
            ax_right.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.03,
                f"{height:.3f}",
                ha='center', va='bottom', fontsize=10
            )
        ax_right.set_xticks(x_right)
        ax_right.set_xticklabels(right_models, rotation=45, ha="right", fontsize=11)
        ax_right.set_ylabel(f"Mean {nice_names[right_metric]} Value", fontsize=12)
        ax_right.set_ylim([0, 1.05])
        plt.tight_layout()
        fig_name = f"bar_pair_{left_metric}_{right_metric}.png"
        fig_path = os.path.join(plots_folder, fig_name)
        plt.savefig(fig_path, dpi=150)
        plt.close(fig)
        logging.info(f"Bar charts for {left_metric} & {right_metric} saved to {fig_path}")

    return {
        "results_df": results_df,
        "summary_df": summary_df
    }
