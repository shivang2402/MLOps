# Lab 1-4: GitHub Actions ML Pipeline with Exercise Calorie Prediction

Complete MLOps lab combining Labs 1-4 concepts with custom CSV dataset and model comparison.

## Lab Coverage

### Lab 1: Testing & Code Quality
- Unit tests in `tests/`
- Pytest configuration
- CI runs automated tests
- Test coverage for config loading, data validation, and app routes

### Lab 2: Model Training & Versioning
- `src/train_model.py` trains multiple regression models
- Automatic model selection based on RMSE metric
- Versioned model artifacts with timestamp
- Training metrics saved to JSON

### Lab 3: Reproducibility & Pipeline
- `config/training_config.json` drives all hyperparameters
- Config-based feature selection and preprocessing
- One-command reproducible training and evaluation
- `src/evaluate_model.py` computes regression metrics (MAE/RMSE/R2/MAPE)

### Lab 4: CI/CD & Workflow Automation
- GitHub Actions workflow (`.github/workflows/lab_1_to_4_ci.yml`)
- Triggers on code push and manual workflow dispatch
- Pipeline stages:
  1. Install dependencies
  2. Run tests
  3. Train model
  4. Evaluate model
  5. Upload artifacts
- Supports containerization (ready for Docker integration)

## Dataset

- **Source:** Exercise calorie burn data (248 activities)
- **Features:** Activity type, weight breakpoints (130-205 lbs), calories per kg
- **Target:** Calories burned per hour at 205 lbs
- **Location:** `src/data/exercise_dataset.csv`

## Models

Configuration supports automatic comparison of:
- Linear Regression
- Random Forest
- Gradient Boosting

Best model is automatically selected by RMSE and saved for serving.

## Local Execution

### Run Tests

```bash
pip install -r requirements.txt
pytest -v
```

### Train Model

```bash
timestamp=$(date '+%Y%m%d%H%M%S')
python src/train_model.py --timestamp "$timestamp" --config "config/training_config.json"
```

Outputs:
- `model_<timestamp>_<selected_model>_exercise_calories.joblib`
- `<timestamp>_train_summary.json`

### Evaluate Model

```bash
python src/evaluate_model.py --timestamp "$timestamp" --config "config/training_config.json"
```

Outputs:
- `<timestamp>_metrics.json`

### Run Flask App

```bash
# First: train model to generate artifacts
# Then:
python src/main.py
# Visit: http://localhost:5001/predict
```

## File Structure

```
Lab_1_to_4_GitHub_MLOps/
├── src/
│   ├── data/
│   │   └── exercise_dataset.csv
│   ├── templates/
│   │   └── predict.html
│   ├── train_model.py          (Lab 2/3: model training + selection)
│   ├── evaluate_model.py       (Lab 3: metrics computation)
│   └── main.py                 (Lab 4: Flask app)
├── config/
│   └── training_config.json    (Lab 3: reproducible config)
├── tests/
│   ├── conftest.py
│   ├── test_training.py        (Lab 1: training tests)
│   └── test_app.py             (Lab 1: app tests)
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
        └── lab_1_to_4_ci.yml   (Lab 4: CI workflow)
```

## Customizations from Original Lab 2

1. **Dataset**: Real exercise calorie data instead of synthetic
2. **Models**: Multiple regression models with automatic selection
3. **Metrics**: Expanded evaluation (MAE/RMSE/R2/MAPE/within 50 cal %)
4. **Config**: JSON-driven hyperparameters and feature selection
5. **Tests**: Unit tests for config, data, and Flask routes
6. **Workflow**: Complete GitHub Actions pipeline with artifact upload
7. **App**: Flask app with config-driven preprocessing

## Next Steps for Submission

1. Initialize a new GitHub repository
2. Push this Lab_1_to_4_GitHub_MLOps folder to main branch
3. GitHub Actions workflow runs automatically
4. Access model artifacts and metrics from workflow runs

## Example Prediction

- Activity: "Running, 5 mph"
- Weight: 180 lbs
- Predicted Calories: ~540 cal/hr
