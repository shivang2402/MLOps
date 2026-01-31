# Calorie Burn Estimator API

## Overview

This project uses a **Calories Burned During Exercise** dataset from Kaggle to predict calories burned based on physical activity and body weight.

## What I Built

A REST API that:
- Predicts calories burned for 248 different physical activities
- Recommends activities based on target calorie goals
- Uses a Random Forest Regressor model trained on real exercise data

## Dataset

**Source:** [Kaggle - Calories Burned During Exercise and Activities](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities)

**File:** `exercise_dataset.csv`

**Features:**
| Column | Description |
|--------|-------------|
| Activity, Exercise or Sport (1 hour) | Name of the activity |
| 130 lb | Calories burned for a 130 lb person |
| 155 lb | Calories burned for a 155 lb person |
| 180 lb | Calories burned for a 180 lb person |
| 205 lb | Calories burned for a 205 lb person |
| Calories per kg | Calories burned per kilogram of body weight |

**Size:** 248 activities

## Project Structure

```
FastAPI_Calorie_Estimator/
├── data/
│   └── exercise_dataset.csv
├── model/
│   ├── calorie_model.pkl
│   ├── activity_encoder.pkl
│   └── activity_decoder.pkl
├── src/
│   ├── data.py
│   ├── main.py
│   ├── predict.py
│   └── train.py
├── README.md
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/activities` | List all 248 supported activities |
| POST | `/predict` | Predict calories burned for an activity |
| POST | `/recommend` | Recommend activities to burn target calories |

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/shivang2402/MLOps.git
cd MLOps/Labs/FastAPI_Calorie_Estimator
```

### 2. Create and activate virtual environment

```bash
# Create environment
python3 -m venv fastapi_lab1_env

# Activate (macOS/Linux)
source fastapi_lab1_env/bin/activate

# Activate (Windows)
fastapi_lab1_env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install pandas
```

### 4. Train the model

```bash
cd src
python train.py
```

You should see:
```
Model trained and saved!
Number of activities: 248
Sample activities: ['Cycling, mountain bike, bmx', ...]
```

### 5. Run the API server

```bash
uvicorn main:app --reload
```

Server will start at `http://127.0.0.1:8000`

### 6. Test the API

Open your browser and go to: **http://127.0.0.1:8000/docs**

This opens the interactive Swagger UI where you can test all endpoints.

## Usage Examples

### Predict Calories

**Request:**
```json
POST /predict
{
  "activity": "Running, 5 mph (12 minute mile)",
  "weight_kg": 70
}
```

**Response:**
```json
{
  "calories_burned": 530.9,
  "activity": "Running, 5 mph (12 minute mile)",
  "weight_kg": 70
}
```

### Get Recommendations

**Request:**
```json
POST /recommend
{
  "target_calories": 500,
  "weight_kg": 70,
  "top_n": 5
}
```

**Response:**
```json
{
  "target_calories": 500,
  "weight_kg": 70,
  "recommendations": [
    {"activity": "Running, 5 mph (12 minute mile)", "calories_burned": 530.9},
    {"activity": "Swimming laps, freestyle, slow", "calories_burned": 493.2},
    ...
  ]
}
```

## Model Details

- **Algorithm:** Random Forest Regressor
- **Features:** Activity (encoded), Weight (kg)
- **Target:** Calories burned per hour
- **Training/Test Split:** 70/30

## Modifications from Original Lab

This lab includes the following modifications from the original FastAPI Lab 1:

1. **Different Dataset:** Used Kaggle's "Calories Burned During Exercise" dataset instead of the Iris dataset
2. **Different Model Type:** Regression (Random Forest Regressor) instead of Classification (Decision Tree Classifier)
3. **Additional Endpoints:** Added `/activities` and `/recommend` endpoints
4. **Real-world Application:** Practical calorie estimation instead of flower classification
