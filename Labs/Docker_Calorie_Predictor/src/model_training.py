import csv
import json
import pickle
import argparse

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_PATH = "src/data/exercise_dataset.csv"
DEFAULT_CONFIG_PATH = "config/training_config.json"


def load_dataset(path):
    """
    Features: [calories_per_kg, weight_lbs]  (both meaningful numerics)
    Target:   calories burned

    Returns:
        X            - np.array (N, 2)
        y            - np.array (N,)
        activity_data - list of {"name": str, "cal_per_kg": float}
    """
    weight_cols = [130, 155, 180, 205]
    activity_data = []
    rows = []

    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for line in reader:
            name = line[0].strip()
            try:
                cal_per_kg = float(line[5])
            except (ValueError, IndexError):
                continue
            activity_data.append({"name": name, "cal_per_kg": cal_per_kg})
            for w_idx, w in enumerate(weight_cols):
                try:
                    cal = float(line[w_idx + 1])
                except ValueError:
                    continue
                rows.append([cal_per_kg, float(w), cal])

    data = np.array(rows)
    X = data[:, :2]   # cal_per_kg, weight_lbs
    y = data[:, 2]    # calories
    return X, y, activity_data


def load_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to training config file")
    args = parser.parse_args()

    config = load_config(args.config)
    data_path = config.get("dataset_path", DATA_PATH)

    X, y, activity_data = load_dataset(data_path)
    print(f"Dataset: {X.shape[0]} samples, {len(activity_data)} activities")

    with open(config.get("activity_output", "activity_data.json"), "w", encoding="utf-8") as f:
        json.dump(activity_data, f)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(config.get("test_size", 0.2)),
        random_state=int(config.get("random_state", 42)),
    )

    scaler_X = StandardScaler()
    X_train_s = scaler_X.fit_transform(X_train)
    X_test_s = scaler_X.transform(X_test)

    scaler_y = StandardScaler()
    y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_s = scaler_y.transform(y_test.reshape(-1, 1)).ravel()

    with open(config.get("scaler_x_output", "scaler_X.pkl"), "wb") as f:
        pickle.dump(scaler_X, f)
    with open(config.get("scaler_y_output", "scaler_y.pkl"), "wb") as f:
        pickle.dump(scaler_y, f)

    import tensorflow as tf

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(2,)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(1),
    ])

    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.fit(
        X_train_s,
        y_train_s,
        epochs=int(config.get("epochs", 50)),
        batch_size=int(config.get("batch_size", 32)),
        validation_split=float(config.get("validation_split", 0.1)),
        verbose=1,
    )

    preds_s = model.predict(X_test_s, verbose=0).ravel()
    preds = scaler_y.inverse_transform(preds_s.reshape(-1, 1)).ravel()

    mae_cal = mean_absolute_error(y_test, preds)
    rmse_cal = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)

    print(f"Test MAE: {mae_cal:.2f} calories")
    print(f"Test RMSE: {rmse_cal:.2f} calories")
    print(f"Test R2: {r2:.4f}")

    metrics = {
        "mae": float(mae_cal),
        "rmse": float(rmse_cal),
        "r2": float(r2),
        "samples": int(X.shape[0]),
        "activities": int(len(activity_data)),
        "config_used": args.config,
    }

    with open(config.get("metrics_output", "training_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    model_output = config.get("model_output", "exercise_model.keras")
    model.save(model_output)
    print(f"Model saved to {model_output}")
