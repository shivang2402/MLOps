import csv
import json
import pickle

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_PATH = "src/data/exercise_dataset.csv"


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


if __name__ == "__main__":
    X, y, activity_data = load_dataset(DATA_PATH)
    print(f"Dataset: {X.shape[0]} samples, {len(activity_data)} activities")

    # Save activity data (name + cal_per_kg) for the serving container
    with open("activity_data.json", "w") as f:
        json.dump(activity_data, f)
    print("Activity data saved to activity_data.json")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler_X = StandardScaler()
    X_train_s = scaler_X.fit_transform(X_train)
    X_test_s = scaler_X.transform(X_test)

    scaler_y = StandardScaler()
    y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_s = scaler_y.transform(y_test.reshape(-1, 1)).ravel()

    with open("scaler_X.pkl", "wb") as f:
        pickle.dump(scaler_X, f)
    with open("scaler_y.pkl", "wb") as f:
        pickle.dump(scaler_y, f)
    print("Scalers saved")

    # Regression neural network
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, input_shape=(2,), activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(1),          # linear output for regression
    ])

    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.fit(
        X_train_s, y_train_s,
        epochs=100,
        validation_data=(X_test_s, y_test_s),
        verbose=1,
    )

    # Evaluate in original calorie scale
    preds_s = model.predict(X_test_s).ravel()
    preds = scaler_y.inverse_transform(preds_s.reshape(-1, 1)).ravel()
    mae_cal = np.mean(np.abs(preds - y_test))
    print(f"Test MAE: {mae_cal:.1f} calories")

    model.save("exercise_model.keras")
    print("Model saved to exercise_model.keras")
