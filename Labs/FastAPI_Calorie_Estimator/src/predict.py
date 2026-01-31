# predict.py
import joblib
import numpy as np

def predict_data(X):
    """
    Predict calories burned for the input data.
    Args:
        X (numpy.ndarray): Input data [activity_encoded, weight_kg]
    Returns:
        y_pred (numpy.ndarray): Predicted calories burned.
    """
    model = joblib.load("../model/calorie_model.pkl")
    y_pred = model.predict(X)
    return y_pred

def get_encoders():
    """Load and return the encoders."""
    activity_encoder = joblib.load("../model/activity_encoder.pkl")
    activity_decoder = joblib.load("../model/activity_decoder.pkl")
    return activity_encoder, activity_decoder