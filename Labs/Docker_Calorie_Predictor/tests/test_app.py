import numpy as np

import src.main as app_module


class DummyScaler:
    def transform(self, x):
        return x

    def inverse_transform(self, x):
        return x


class DummyModel:
    def predict(self, x, verbose=0):
        return np.array([[123.4]])


def test_predict_post_success(monkeypatch):
    def fake_artifacts():
        model = DummyModel()
        scaler_x = DummyScaler()
        scaler_y = DummyScaler()
        activity_data = [{"name": "Running", "cal_per_kg": 1.8}]
        return model, scaler_x, scaler_y, activity_data

    monkeypatch.setattr(app_module, "load_artifacts", fake_artifacts)
    app = app_module.create_app()
    client = app.test_client()

    response = client.post("/predict", data={"activity_id": "0", "weight_lbs": "180"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["activity"] == "Running"
    assert "calories_burned" in payload


def test_predict_post_invalid_weight(monkeypatch):
    def fake_artifacts():
        model = DummyModel()
        scaler_x = DummyScaler()
        scaler_y = DummyScaler()
        activity_data = [{"name": "Running", "cal_per_kg": 1.8}]
        return model, scaler_x, scaler_y, activity_data

    monkeypatch.setattr(app_module, "load_artifacts", fake_artifacts)
    app = app_module.create_app()
    client = app.test_client()

    response = client.post("/predict", data={"activity_id": "0", "weight_lbs": "0"})
    assert response.status_code == 400
