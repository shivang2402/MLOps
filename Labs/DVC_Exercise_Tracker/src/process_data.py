"""
Reshape the exercise dataset from wide format (one column per weight)
to long format (one row per activity-weight combination) and engineer features.

Input:  data/exercise_dataset.csv   (248 rows × 6 cols)
Output: data/processed.csv          (992 rows × 4 cols)
"""

import argparse
import pathlib

import pandas as pd
import yaml


def load_params(params_path: str = "params.yaml") -> dict:
    with open(params_path) as f:
        return yaml.safe_load(f)


def process(raw_path: str, out_path: str, test_size: float) -> None:
    df = pd.read_csv(raw_path)

    # Rename columns for convenience
    df.columns = ["activity", "cal_130", "cal_155", "cal_180", "cal_205", "cal_per_kg"]

    # Melt wide → long: one row per (activity, weight)
    weight_cols = {"cal_130": 130, "cal_155": 155, "cal_180": 180, "cal_205": 205}
    records = []
    for col, weight in weight_cols.items():
        tmp = df[["activity", col, "cal_per_kg"]].copy()
        tmp = tmp.rename(columns={col: "calories"})
        tmp["weight_lbs"] = weight
        records.append(tmp)

    long = pd.concat(records, ignore_index=True)

    # Feature: weight in kg
    long["weight_kg"] = (long["weight_lbs"] * 0.453592).round(2)

    # Keep useful columns
    long = long[["activity", "weight_lbs", "weight_kg", "cal_per_kg", "calories"]]

    # Shuffle with fixed seed for reproducibility
    long = long.sample(frac=1, random_state=42).reset_index(drop=True)

    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out_path, index=False)
    print(f"Processed {len(long)} rows → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    args = parser.parse_args()

    params = load_params(args.params)
    process(
        raw_path=params["data"]["raw"],
        out_path=params["data"]["processed"],
        test_size=params["train"]["test_size"],
    )
