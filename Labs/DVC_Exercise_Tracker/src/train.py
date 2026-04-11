"""
Train a Random Forest Regressor to predict calories burned from
activity (label-encoded), weight_lbs, weight_kg, and cal_per_kg.

Input:  data/processed.csv
Output: model/model.pkl, model/metrics.json
"""

import argparse
import json
import pathlib
import pickle

import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def load_params(params_path: str = "params.yaml") -> dict:
    with open(params_path) as f:
        return yaml.safe_load(f)


def train(processed_path: str, params: dict) -> None:
    df = pd.read_csv(processed_path)

    # Encode activity names
    le = LabelEncoder()
    df["activity_encoded"] = le.fit_transform(df["activity"])

    features = ["activity_encoded", "weight_lbs", "weight_kg", "cal_per_kg"]
    target = "calories"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=params["train"]["test_size"],
        random_state=params["train"]["random_state"],
    )

    model = RandomForestRegressor(
        n_estimators=params["train"]["n_estimators"],
        max_depth=params["train"]["max_depth"],
        random_state=params["train"]["random_state"],
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        "mae": round(mean_absolute_error(y_test, y_pred), 4),
        "rmse": round(root_mean_squared_error(y_test, y_pred), 4),
        "r2": round(r2_score(y_test, y_pred), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    # Save artifacts
    model_dir = pathlib.Path(params["model"]["dir"])
    model_dir.mkdir(parents=True, exist_ok=True)

    with open(model_dir / "model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(model_dir / "label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)
    with open(model_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to {model_dir}/model.pkl")
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    args = parser.parse_args()

    params = load_params(args.params)
    train(params["data"]["processed"], params)
