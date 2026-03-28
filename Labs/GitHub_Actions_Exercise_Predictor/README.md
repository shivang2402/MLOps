# GitHub Actions Lab: Exercise Calorie Predictor

## Overview
An ML pipeline that trains multiple regression models on exercise calorie data, selects the best one by RMSE, and serves predictions through a Flask app. GitHub Actions automates the full cycle — tests, training, evaluation, and artifact upload.

## Modifications from Original Lab
1. **Different Dataset** — Real exercise calorie burn data (248 activities) instead of synthetic/Iris
2. **Different Task** — Multi-model regression with automatic selection instead of single-model classification
3. **Fixed Jinja template** — Original used `enumerate()` in the template loop which isn't valid Jinja2; replaced with `loop.index0`
4. **Fixed inference input** — Original passed `[cal_per_kg, weight_lbs]` as a numpy array but the model is a sklearn Pipeline expecting a DataFrame with all training feature columns; now builds the correct DataFrame and scales prediction by user weight
5. **Config-driven training** — Hyperparameters, feature selection, and model list controlled via JSON config
6. **Activity metadata export** — Training now generates `activity_data.json` so the Flask app doesn't depend on the raw CSV at runtime

## Labs 1–4 Coverage Map
1. **Lab 1 (Testing + Code quality)**
	- Unit tests under `tests/`
	- CI runs `pytest`
2. **Lab 2 (Model training + versioned artifacts)**
	- `src/train_model.py` trains Linear Regression, Random Forest, and Gradient Boosting
	- Best model auto-selected by RMSE, saved with timestamp
3. **Lab 3 (Pipeline repeatability + config)**
	- `config/training_config.json` drives all hyperparameters and feature selection
	- `src/evaluate_model.py` computes MAE/RMSE/R2
4. **Lab 4 (CI/CD + workflow automation)**
	- GitHub Actions workflow: `.github/workflows/lab_1_to_4_ci.yml`
	- Pipeline: install → test → train → evaluate → upload artifacts

## Dataset
**Source:** [Kaggle — Calories Burned During Exercise](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities)

| Column | Description |
|--------|-------------|
| Activity | Name of the exercise (248 activities) |
| 130 lb – 205 lb | Calories burned at each body weight |
| Calories per kg | Normalised burn rate |

**Target:** Calories burned per hour at 205 lb

## Model
- **Algorithm:** Best of Linear Regression / Random Forest / Gradient Boosting (auto-selected)
- **Features:** Activity name (one-hot encoded), weight breakpoints (130/155/180 lb), calories per kg
- **Preprocessing:** sklearn Pipeline with `ColumnTransformer` (OneHotEncoder + StandardScaler)
- **Inference:** Model predicts 205 lb baseline, then scales proportionally to user weight

## Directory Structure
```
GitHub_Actions_Exercise_Predictor/
├── src/
│   ├── data/
│   │   └── exercise_dataset.csv
│   ├── templates/
│   │   └── predict.html
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── main.py
├── config/
│   └── training_config.json
├── tests/
│   ├── conftest.py
│   ├── test_training.py
│   └── test_app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup & Run

### Run Tests
```bash
pip install -r requirements.txt
pytest -v
```

### Train Model
```bash
timestamp=$(date '+%Y%m%d%H%M%S')
python src/train_model.py --timestamp "$timestamp" --config config/training_config.json
```

Generated artifacts:
- `model_<timestamp>_<model_name>_exercise_calories.joblib`
- `<timestamp>_train_summary.json`
- `activity_data.json`

### Evaluate Model
```bash
python src/evaluate_model.py --timestamp "$timestamp" --config config/training_config.json
```

### Run Flask App
```bash
ln -sf model_*_exercise_calories.joblib exercise_model.joblib
python src/main.py
```

Open [http://localhost:5001/predict](http://localhost:5001/predict)

## Tech Stack
- Python 3.10, scikit-learn, Flask, pandas, joblib
- GitHub Actions CI/CD
- Dataset: [Kaggle Exercise Dataset](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities)
