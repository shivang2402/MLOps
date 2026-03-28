from pathlib import Path

from src.train_model import load_config


def test_dataset_exists():
    data_path = Path(__file__).resolve().parents[1] / "src" / "data" / "exercise_dataset.csv"
    assert data_path.exists(), f"Dataset not found: {data_path}"


def test_config_has_required_keys():
    config_path = Path(__file__).resolve().parents[1] / "config" / "training_config.json"
    config = load_config(str(config_path))

    for required_key in ["dataset_path", "target_column", "feature_columns", "models", "selection_metric"]:
        assert required_key in config, f"Missing key: {required_key}"


def test_config_models_not_empty():
    config_path = Path(__file__).resolve().parents[1] / "config" / "training_config.json"
    config = load_config(str(config_path))
    assert len(config["models"]) > 0, "models list empty in config"
