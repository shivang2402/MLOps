import json
import os
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_artifacts():
    model_path = os.getenv("MODEL_PATH", "exercise_model.joblib")
    config_path = os.getenv("CONFIG_PATH", "config/training_config.json")

    model = joblib.load(model_path)
    config = load_config(config_path)

    with open("activity_data.json", "r", encoding="utf-8") as f:
        activity_data = json.load(f)

    return model, activity_data, config


def create_app():
    app = Flask(__name__)
    model, activity_data, config = load_artifacts()
    activity_names = [a["name"] for a in activity_data]

    @app.route("/")
    def home():
        return "Welcome to Exercise Calorie Predictor! Visit /predict"

    @app.route("/predict", methods=["GET", "POST"])
    def predict():
        if request.method == "GET":
            return render_template("predict.html", activities=activity_names)

        if request.method == "POST":
            try:
                activity_id = int(request.form["activity_id"])
                weight_lbs = float(request.form["weight_lbs"])

                if activity_id < 0 or activity_id >= len(activity_data):
                    return jsonify({"error": "Invalid activity"}), 400
                if weight_lbs <= 0:
                    return jsonify({"error": "Weight must be positive"}), 400

                cal_per_kg = activity_data[activity_id]["cal_per_kg"]
                x_input = np.array([[cal_per_kg, weight_lbs]])
                pred = model.predict(x_input)[0]

                return jsonify({
                    "activity": activity_names[activity_id],
                    "weight_lbs": weight_lbs,
                    "calories_burned": round(float(pred), 1),
                })
            except (KeyError, ValueError) as e:
                return jsonify({"error": str(e)}), 400

        return "Unsupported method", 405

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5001)
