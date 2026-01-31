# train.py
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from data import load_data, split_data

def fit_model(X_train, y_train):
    """
    Train a Random Forest Regressor and save the model to a file.
    """
    model = RandomForestRegressor(n_estimators=100, random_state=12)
    model.fit(X_train, y_train)
    
    os.makedirs("../model", exist_ok=True)
    joblib.dump(model, "../model/calorie_model.pkl")

if __name__ == "__main__":
    X, y, activity_encoder = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    fit_model(X_train, y_train)
    
    # Save encoder
    joblib.dump(activity_encoder, "../model/activity_encoder.pkl")
    
    # Save reverse encoder for API display
    reverse_encoder = {v: k for k, v in activity_encoder.items()}
    joblib.dump(reverse_encoder, "../model/activity_decoder.pkl")
    
    print("Model trained and saved!")
    print(f"Number of activities: {len(activity_encoder)}")
    print(f"Sample activities: {list(activity_encoder.keys())[:5]}")