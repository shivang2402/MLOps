# DVC Lab: Exercise Calorie Tracker

## Overview

A data-versioning project that uses **DVC (Data Version Control)** with **Google Cloud Storage** to track and version an exercise calorie dataset through a reproducible ML pipeline. The pipeline reshapes raw calorie data, engineers features, and trains a Random Forest Regressor to predict calories burned per hour.

## Modifications from Original Lab 1

1. **Different Dataset** — Exercise calorie dataset (248 activities, 992 samples after reshaping) instead of a placeholder `data.txt`
2. **DVC Pipeline** — Added `dvc.yaml` with two stages (`process` → `train`) instead of only tracking a single file with `dvc add`
3. **Parameterized Config** — `params.yaml` controls data paths, train/test split, and model hyperparameters; DVC tracks param changes automatically
4. **ML Model** — Random Forest Regressor that predicts calories burned, with metrics tracked in `model/metrics.json`
5. **Feature Engineering** — Wide-to-long reshape (4 weight breakpoints per activity) and lb-to-kg conversion in `src/process_data.py`

## Dataset

**Source:** [Kaggle — Calories Burned During Exercise](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities)

**File:** `data/exercise_dataset.csv`

| Column | Description |
|--------|-------------|
| Activity, Exercise or Sport (1 hour) | Name of the activity |
| 130 lb – 205 lb | Calories burned at each body weight |
| Calories per kg | Calories burned per kilogram of body weight |

**Raw:** 248 activities | **Processed:** 248 activities x 4 weight breakpoints = **992 samples**

## Project Structure

```
DVC_Exercise_Tracker/
├── data/
│   └── exercise_dataset.csv
├── src/
│   ├── process_data.py
│   └── train.py
├── model/                  # generated after pipeline run
│   ├── model.pkl
│   ├── label_encoder.pkl
│   └── metrics.json
├── keys/                   # gitignored
│   └── dvc-key.json
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/shivang2402/MLOps.git
cd MLOps/Labs/DVC_Exercise_Tracker
```

### 2. Create and activate virtual environment

```bash
python3 -m venv dvc_env

# macOS / Linux
source dvc_env/bin/activate

# Windows
dvc_env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## GCS Remote Setup

### 1. Create a Google Cloud Storage bucket

```bash
gcloud storage buckets create gs://<your-bucket-name> \
  --project=<your-project-id> \
  --location=us-east1 \
  --uniform-bucket-level-access
```

For this project we used:
```bash
gcloud storage buckets create gs://mlops-dvc-exercise-shiv \
  --project=gen-lang-client-0329498639 \
  --location=us-east1 \
  --uniform-bucket-level-access
```

### 2. Create a service account and download key

```bash
# Create the service account
gcloud iam service-accounts create dvc-lab \
  --display-name="DVC Lab Service Account" \
  --project=<your-project-id>

# Grant storage admin role
gcloud projects add-iam-policy-binding <your-project-id> \
  --member="serviceAccount:dvc-lab@<your-project-id>.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Download the JSON key
gcloud iam service-accounts keys create keys/dvc-key.json \
  --iam-account=dvc-lab@<your-project-id>.iam.gserviceaccount.com
```

> **Note:** Never commit `keys/dvc-key.json` to git. It is already in `.gitignore`.

### 3. Configure DVC remote

```bash
dvc init
dvc remote add -d myremote gs://<your-bucket-name>
dvc remote modify myremote credentialpath keys/dvc-key.json
```

## Running the Pipeline

### Run all stages

```bash
dvc repro
```

**Output:**
```
Running stage 'process':
> python src/process_data.py
Processed 992 rows → data/processed.csv
Generating lock file 'dvc.lock'
Updating lock file 'dvc.lock'

Running stage 'train':
> python src/train.py
Model saved to model/model.pkl
Metrics: {'mae': 5.441, 'rmse': 19.0079, 'r2': 0.9957, 'train_samples': 694, 'test_samples': 298}
Updating lock file 'dvc.lock'
```

### View metrics

```bash
dvc metrics show
```

**Output:**
```
Path                mae    r2      rmse     test_samples    train_samples
model/metrics.json  5.441  0.9957  19.0079  298             694
```

### Pipeline Results

| Metric | Value |
|--------|-------|
| MAE | 5.441 |
| RMSE | 19.008 |
| R2 | 0.9957 |
| Train samples | 694 |
| Test samples | 298 |

### Push data and artifacts to GCS

```bash
dvc push
```

**Output:**
```
3 files pushed
```

GCS bucket contents after push (`gs://mlops-dvc-exercise-shiv/`):
```
files/md5/2d/2bed97978d76c30f8bb3289c7714f7   # data/processed.csv
files/md5/8a/aef62799cb74b4bc7d530bbe763988   # model/label_encoder.pkl
files/md5/d2/86ba42370ccd367c0422ff5cd03686   # model/model.pkl
```

### Pull data from GCS (on another machine)

```bash
dvc pull
```

**Verification (delete local, pull back):**
```
$ rm -rf data/processed.csv model/model.pkl model/label_encoder.pkl
$ dvc pull
A       data/processed.csv
A       model/label_encoder.pkl
A       model/model.pkl
3 files added
```

## Data Versioning Workflow

### Track a new version

```bash
# Change params (e.g., n_estimators: 100 → 200, max_depth: 10 → 15)
dvc repro          # re-runs only affected stages
dvc metrics diff   # compare old vs new
git add dvc.lock params.yaml model/metrics.json
git commit -m "Pipeline v2: 200 estimators, depth 15"
dvc push
```

### Version comparison (v1 → v2)

Changing `n_estimators: 100 → 200` and `max_depth: 10 → 15`:

```bash
$ dvc repro
Stage 'process' didn't change, skipping
Running stage 'train':
> python src/train.py
Metrics: {'mae': 5.4722, 'rmse': 19.3739, 'r2': 0.9956}

$ dvc metrics diff
Path                Metric    HEAD     workspace    Change
model/metrics.json  mae       5.441    5.4722       0.0312
model/metrics.json  r2        0.9957   0.9956       -0.0001
model/metrics.json  rmse      19.0079  19.3739      0.366

$ dvc push
1 file pushed
```

DVC only re-ran `train` (data didn't change) and only pushed 1 new artifact (updated model).

### Revert to a previous version

```bash
git checkout <commit-hash>
dvc checkout
```

## Model Details

- **Algorithm:** Random Forest Regressor (scikit-learn)
- **Features:** activity (label-encoded), weight_lbs, weight_kg, cal_per_kg
- **Target:** Calories burned per hour
- **Train/Test Split:** 70/30 (694 train, 298 test)
- **Hyperparameters:** configurable in `params.yaml` (v1: 100 trees/depth 10, v2: 200 trees/depth 15)
- **v1 Metrics:** MAE 5.44, RMSE 19.01, R2 0.9957
- **v2 Metrics:** MAE 5.47, RMSE 19.37, R2 0.9956

## Tech Stack

- Python 3.10+, scikit-learn, pandas
- DVC 3.x with Google Cloud Storage backend
- Dataset: [Kaggle Exercise Dataset](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities)
