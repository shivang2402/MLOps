import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    summary_path = Path(f"{timestamp}_train_summary.json")
    if not summary_path.exists():
        raise FileNotFoundError(f"Training summary missing: {summary_path}")

    with open(summary_path, "r", encoding="utf-8") as summary_file:
        train_summary = json.load(summary_file)

    model_filename = train_summary["selected_model_filename"]
    model = joblib.load(model_filename)

    df = pd.read_csv(dataset_path)
    X = df[config["feature_columns"]]
    y = df[config["target_column"]]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=float(config["test_size"]),
        random_state=int(config["random_state"]),
    )

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    eps = 1e-8
    mape = (abs((y_test - y_pred) / (y_test + eps))).mean() * 100
    within_50_cal = (abs(y_test - y_pred) <= 50).mean() * 100

    metrics = {
        "dataset": str(dataset_path),
        "target_column": config["target_column"],
        "selected_model": train_summary["selected_model"],
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(rmse),
        "r2": float(r2_score(y_test, y_pred)),
        "mape_percent": float(mape),
        "within_50_calories_percent": float(within_50_cal),
    }

    with open(f"{timestamp}_metrics.json", "w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=4)

    print(f"✓ Metrics: {metrics['mae']:.2f} MAE, {metrics['r2']:.4f} R2")
