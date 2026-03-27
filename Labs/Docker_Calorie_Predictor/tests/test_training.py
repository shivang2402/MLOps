from pathlib import Path

from src.model_training import load_config, load_dataset


def test_load_dataset_shape_and_values():
    data_path = Path(__file__).resolve().parents[1] / "src" / "data" / "exercise_dataset.csv"
    x, y, activity_data = load_dataset(str(data_path))

    assert x.shape[1] == 2
    assert y.shape[0] == x.shape[0]
    assert len(activity_data) > 0
    assert activity_data[0]["name"]


def test_config_has_expected_keys():
    config_path = Path(__file__).resolve().parents[1] / "config" / "training_config.json"
    config = load_config(str(config_path))

    for required_key in ["dataset_path", "epochs", "batch_size", "model_output", "metrics_output"]:
        assert required_key in config
