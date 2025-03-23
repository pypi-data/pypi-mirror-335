import os
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit, RepeatedStratifiedKFold
from sklearn.metrics import (accuracy_score, roc_auc_score, f1_score,
                             precision_score, recall_score,
                             log_loss, matthews_corrcoef, cohen_kappa_score,
                             average_precision_score)
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
import warnings

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier
import xgboost as xgb
import lightgbm as lgb

warnings.filterwarnings("ignore")

def run_autoML_pipeline(preprocessed_data, fingerprint_df, results_folder="results",
                        test_size=0.2, n_folds=5, n_repeats=1, random_state=42, max_evals=3):
    """
    Executes the AutoML pipeline without scaling, preserving the original binary fingerprint values.
    Splits the data into training and test sets, and performs hyperparameter optimization.
    The train and test datasets are saved in the results folder.
    """
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # Align indices
    preprocessed_data = preprocessed_data.reset_index(drop=True)
    fingerprint_df = fingerprint_df.reset_index(drop=True)

    # Merge the "Response" column (map Active/Inactive to 1/0)
    data = fingerprint_df.copy()
    data["Response"] = preprocessed_data["Response"]
    data["Response"] = data["Response"].map({'Active': 1, 'Inactive': 0})

    indices = np.arange(len(data))
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    for train_idx, test_idx in sss.split(indices, data["Response"]):
        pass

    X = data.drop(columns=["Response", "Smiles"])
    y = data["Response"]

    X_train = X.iloc[train_idx]
    y_train = y.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_test = y.iloc[test_idx]

    # *** Remove StandardScaler: Use original binary features ***
    train_df = X_train.copy()
    train_df["Response"] = y_train.values
    test_df = X_test.copy()
    test_df["Response"] = y_test.values

    # Save datasets
    train_df.to_csv(os.path.join(results_folder, "train_data.csv"), index=False)
    test_df.to_csv(os.path.join(results_folder, "test_data.csv"), index=False)

    cv = RepeatedStratifiedKFold(n_splits=n_folds, n_repeats=n_repeats, random_state=random_state)

    # Define classifiers and hyperparameter spaces
    classifiers = {
        "LRC": {
            "model": LogisticRegression(random_state=random_state, max_iter=1000, class_weight='balanced'),
            "space": {
                "lr_C": hp.loguniform("lr_C", -4, 4)
            }
        },
        "RF": {
            "model": RandomForestClassifier(random_state=random_state, class_weight='balanced'),
            "space": {
                "rf_n_estimators": hp.quniform("rf_n_estimators", 50, 300, 10),
                "rf_max_depth": hp.quniform("rf_max_depth", 3, 15, 1)
            }
        },
        "ETs": {
            "model": ExtraTreesClassifier(random_state=random_state, class_weight='balanced'),
            "space": {
                "et_n_estimators": hp.quniform("et_n_estimators", 50, 300, 10),
                "et_max_depth": hp.quniform("et_max_depth", 3, 15, 1)
            }
        },
        "AB": {
            "model": AdaBoostClassifier(random_state=random_state),
            "space": {
                "ab_n_estimators": hp.quniform("ab_n_estimators", 50, 300, 10),
                "ab_learning_rate": hp.loguniform("ab_learning_rate", -3, 0)
            }
        },
        "SVC": {
            "model": SVC(random_state=random_state, class_weight='balanced', probability=True),
            "space": {
                "svc_C": hp.loguniform("svc_C", -4, 4),
                "svc_gamma": hp.loguniform("svc_gamma", -4, 0)
            }
        },
        "KNN": {
            "model": KNeighborsClassifier(),
            "space": {
                "knn_n_neighbors": hp.quniform("knn_n_neighbors", 3, 15, 1)
            }
        },
        "GB": {
            "model": GradientBoostingClassifier(random_state=random_state),
            "space": {
                "gb_n_estimators": hp.quniform("gb_n_estimators", 50, 300, 10),
                "gb_learning_rate": hp.loguniform("gb_learning_rate", -3, 0),
                "gb_max_depth": hp.quniform("gb_max_depth", 3, 15, 1),
                "gb_max_features": hp.uniform("gb_max_features", 0.5, 1.0),
                "gb_subsample": hp.uniform("gb_subsample", 0.5, 1.0)
            }
        },
        "SGD": {
            "model": SGDClassifier(random_state=random_state, class_weight='balanced'),
            "space": {
                "sgd_alpha": hp.loguniform("sgd_alpha", -4, 0)
            }
        },
        "XGB": {
            "model": xgb.XGBClassifier(random_state=random_state, use_label_encoder=False, eval_metric="logloss"),
            "space": {
                "xgb_n_estimators": hp.quniform("xgb_n_estimators", 50, 300, 10),
                "xgb_learning_rate": hp.loguniform("xgb_learning_rate", -3, 0),
                "xgb_max_depth": hp.quniform("xgb_max_depth", 3, 15, 1),
                "xgb_min_child_weight": hp.quniform("xgb_min_child_weight", 1, 10, 1)
            }
        },
        "LGBM": {
            "model": lgb.LGBMClassifier(random_state=random_state, class_weight='balanced', verbose=-1),
            "space": {
                "lgb_n_estimators": hp.quniform("lgb_n_estimators", 50, 300, 10),
                "lgb_learning_rate": hp.loguniform("lgb_learning_rate", -3, 0),
                "lgb_max_depth": hp.quniform("lgb_max_depth", 3, 15, 1)
            }
        }
    }

    cv_results = {}

    for clf_name, clf_info in classifiers.items():
        model = clf_info["model"]
        space = clf_info["space"]

        def objective(params):
            new_params = {}
            for k, v in params.items():
                new_key = k.split("_", 1)[-1] if "_" in k else k
                if new_key in ["n_estimators", "max_depth", "n_neighbors", "iterations", "depth", "min_child_weight"]:
                    new_params[new_key] = int(v)
                else:
                    new_params[new_key] = v
            model.set_params(**new_params)

            fold_metrics = {m: [] for m in [
                "neg_log_loss", "accuracy", "roc_auc", "f1",
                "precision", "recall", "mcc", "cohen_kappa",
                "average_precision"
            ]}
            fold_details = []

            for fold_idx, (tr_idx, val_idx) in enumerate(cv.split(X_train.values, y_train)):
                X_cv_train = X_train.values[tr_idx]
                y_cv_train = y_train.iloc[tr_idx]
                X_cv_val = X_train.values[val_idx]
                y_cv_val = y_train.iloc[val_idx]

                model.fit(X_cv_train, y_cv_train)

                if hasattr(model, "predict_proba"):
                    y_prob_cv = model.predict_proba(X_cv_val)
                    y_prob_pos = y_prob_cv[:, 1]
                else:
                    decision = model.decision_function(X_cv_val)
                    y_prob_cv = 1 / (1 + np.exp(-decision))
                    y_prob_pos = y_prob_cv if len(y_prob_cv.shape) == 1 else y_prob_cv[:, 1]

                try:
                    neg_ll = -log_loss(y_cv_val, np.column_stack([1 - y_prob_pos, y_prob_pos]), labels=[0, 1])
                except Exception:
                    neg_ll = np.nan

                preds = model.predict(X_cv_val)
                acc_val = accuracy_score(y_cv_val, preds)
                try:
                    roc_val = roc_auc_score(y_cv_val, y_prob_pos)
                except Exception:
                    roc_val = np.nan
                f1_val = f1_score(y_cv_val, preds, zero_division=0, pos_label=1)
                prec_val = precision_score(y_cv_val, preds, zero_division=0, pos_label=1)
                rec_val = recall_score(y_cv_val, preds, zero_division=0, pos_label=1)
                mcc_val = matthews_corrcoef(y_cv_val, preds)
                kappa_val = cohen_kappa_score(y_cv_val, preds)
                try:
                    ap_val = average_precision_score(y_cv_val, y_prob_pos)
                except Exception:
                    ap_val = np.nan

                fold_details.append({
                    "fold_idx": fold_idx,
                    "params": new_params,
                    "y_true_val": y_cv_val.values,
                    "y_prob_val": y_prob_pos,
                    "metrics": {
                        "neg_log_loss": neg_ll,
                        "accuracy": acc_val,
                        "roc_auc": roc_val,
                        "f1": f1_val,
                        "precision": prec_val,
                        "recall": rec_val,
                        "mcc": mcc_val,
                        "cohen_kappa": kappa_val,
                        "average_precision": ap_val
                    }
                })

                for m in fold_metrics:
                    fold_metrics[m].append(fold_details[-1]["metrics"][m])

            mean_metrics = {m: np.nanmean(fold_metrics[m]) for m in fold_metrics}
            return {
                "loss": -mean_metrics["neg_log_loss"],
                "status": STATUS_OK,
                "metrics": mean_metrics,
                "fold_details": fold_details,
                "params_used": new_params
            }

        trials = Trials()
        best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=max_evals,
                    trials=trials, rstate=np.random.default_rng(random_state))

        metric_keys = [
            "neg_log_loss", "accuracy", "roc_auc", "f1",
            "precision", "recall", "mcc", "cohen_kappa", "average_precision"
        ]
        metrics_list = [t["result"]["metrics"] for t in trials.trials]
        mean_metrics_cv = {
            f"{mk}_cv_mean": np.mean([m[mk] for m in metrics_list if m[mk] is not None])
            for mk in metric_keys
        }
        std_metrics_cv = {
            f"{mk}_cv_stdev": np.std([m[mk] for m in metrics_list if m[mk] is not None])
            for mk in metric_keys
        }

        final_params = {}
        for k, v in best.items():
            new_key = k.split("_", 1)[-1] if "_" in k else k
            if new_key in ["n_estimators", "max_depth", "n_neighbors", "iterations", "depth", "min_child_weight"]:
                final_params[new_key] = int(v)
            else:
                final_params[new_key] = v

        model.set_params(**final_params)
        model.fit(X_train.values, y_train)
        cv_results[clf_name] = {
            "best_params": final_params,
            "mean_metrics": mean_metrics_cv,
            "std_metrics": std_metrics_cv,
            "all_trial_details": [t["result"] for t in trials.trials],
            "best_model": {"learner": model, "preprocs": None}  # No scaler used.
        }

        print(f"{clf_name}")
        print("Mean CV metrics:")
        print(mean_metrics_cv)
        print("Std CV metrics:")
        print(std_metrics_cv)
        print("Best model details:")
        print(cv_results[clf_name]["best_model"])
        print("\n" + "-" * 80 + "\n")

    return cv_results
