# data.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def load_data():
    """
    Load the exercise calorie dataset and prepare it for training.
    Returns:
        X (numpy.ndarray): Features (activity_encoded, weight_kg)
        y (numpy.ndarray): Target (calories burned)
        activity_encoder (dict): Mapping of activities to integers
    """
    df = pd.read_csv("../data/exercise_dataset.csv")
    
    # Rename columns for easier access
    df.columns = ['activity', '130lb', '155lb', '180lb', '205lb', 'calories_per_kg']
    
    # Create activity encoder
    activities = df['activity'].unique()
    activity_encoder = {act: i for i, act in enumerate(activities)}
    
    # Reshape data: each row becomes (activity, weight) -> calories
    weights_lb = [130, 155, 180, 205]
    weights_kg = [w * 0.453592 for w in weights_lb]  # Convert to kg
    
    data = []
    for _, row in df.iterrows():
        activity_encoded = activity_encoder[row['activity']]
        for weight_lb, weight_kg in zip(weights_lb, weights_kg):
            calories = row[f'{weight_lb}lb']
            data.append([activity_encoded, weight_kg, calories])
    
    data = np.array(data)
    X = data[:, :2]  # activity_encoded, weight_kg
    y = data[:, 2]   # calories
    
    return X, y, activity_encoder

def split_data(X, y):
    """
    Split the data into training and testing sets.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=12)
    return X_train, X_test, y_train, y_test