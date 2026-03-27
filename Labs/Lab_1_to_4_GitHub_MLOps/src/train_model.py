import argparse
import json
from pathlib import Path

import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_models(random_state: int) -> dict:
    return {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=random_state),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=50, random_state=random_state),
    }


def build_preprocessor(categorical_columns: list, numeric_columns: list) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
            ("num", StandardScaler(), numeric_columns),
        ]
    )


def evaluate_regression(y_true, y_pred) -> dict:
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(rmse),
        "r2": float(r2_score(y_true, y_pred)),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", type=str, required=True, help="Timestamp from GitHub Actions")
    parser.add_argument(
        "--config",
        type=str,
        default="config/training_config.json",
        help="Path to training config JSON",
    )
    args = parser.parse_args()

    timestamp = args.timestamp
    config = load_config(args.config)

    config_path = Path(args.config).resolve()
    lab_root = config_path.parents[1]
    dataset_path = Path(config["dataset_path"])
    if not dataset_path.is_absolute():
        dataset_path = (lab_root / dataset_path).resolve()

    df = pd.read_csv(dataset_path)

    target_column = config["target_column"]
    feature_columns = config["feature_columns"]
    categorical_columns = config.get("categorical_columns", [])
    numeric_columns = [c for c in feature_columns if c not in categorical_columns]

    X = df[feature_columns]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(config["test_size"]),
        random_state=int(config["random_state"]),
    )

    preprocessor = build_preprocessor(categorical_columns, numeric_columns)
    candidate_models = make_models(int(config["random_state"]))
    selected_names = config.get("models", list(candidate_models.keys()))

    model_scores = {}
    best_model_name = None
    best_pipeline = None
    best_metrics = None

    for model_name in selected_names:
        estimator = candidate_models[model_name]
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        metrics = evaluate_regression(y_test, predictions)
        model_scores[model_name] = metrics

        if best_metrics is None or metrics[config["selection_metric"]] < best_metrics[config["selection_metric"]]:
            best_model_name = model_name
            best_pipeline = pipeline
            best_metrics = metrics

    model_filename = f"model_{timestamp}_{best_model_name}_exercise_calories.joblib"
    dump(best_pipeline, model_filename)

    summary = {
        "dataset_path": str(dataset_path),
        "target_column": target_column,
        "feature_columns": feature_columns,
        "test_size": float(config["test_size"]),
        "random_state": int(config["random_state"]),
        "selection_metric": config["selection_metric"],
        "selected_model": best_model_name,
        "selected_model_filename": model_filename,
        "candidate_metrics": model_scores,
        "n_samples": int(df.shape[0]),
        "n_features": int(len(feature_columns)),
    }

    with open(f"{timestamp}_train_summary.json", "w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, indent=4)

    print(f"✓ Model: {best_model_name}")
    print(f"✓ RMSE: {best_metrics['rmse']:.4f}")
    print(f"✓ R2: {best_metrics['r2']:.4f}")
