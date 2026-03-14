import json
import pickle

import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Load model and scalers once at startup
model = tf.keras.models.load_model("exercise_model.keras")

with open("scaler_X.pkl", "rb") as f:
    scaler_X = pickle.load(f)
with open("scaler_y.pkl", "rb") as f:
    scaler_y = pickle.load(f)
with open("activity_data.json") as f:
    activity_data = json.load(f)   # list of {"name": str, "cal_per_kg": float}

activity_names = [a["name"] for a in activity_data]


@app.route("/")
def home():
    return "Welcome to the Exercise Calorie Predictor API! Visit /predict"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html", activities=activity_names)

    if request.method == "POST":
        try:
            activity_id = int(request.form["activity_id"])
            weight_lbs = float(request.form["weight_lbs"])

            if activity_id < 0 or activity_id >= len(activity_data):
                return jsonify({"error": "Invalid activity selection"}), 400
            if weight_lbs <= 0:
                return jsonify({"error": "Weight must be a positive number"}), 400

            cal_per_kg = activity_data[activity_id]["cal_per_kg"]
            X_input = np.array([[cal_per_kg, weight_lbs]])
            X_scaled = scaler_X.transform(X_input)
            pred_scaled = model.predict(X_scaled, verbose=0)
            calories = scaler_y.inverse_transform(pred_scaled)[0][0]

            return jsonify({
                "activity": activity_names[activity_id],
                "weight_lbs": weight_lbs,
                "calories_burned": round(float(calories), 1),
            })
        except (KeyError, ValueError) as e:
            return jsonify({"error": str(e)}), 400

    return "Unsupported HTTP method", 405


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
