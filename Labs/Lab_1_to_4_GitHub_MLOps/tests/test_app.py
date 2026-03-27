import os
import pytest


@pytest.mark.skip(reason="Requires trained model artifact")
def test_app_routes():
    """Test Flask app routes - requires model artifact"""
    from src.main import create_app
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.skip(reason="Requires trained model artifact")
def test_predict_get():
    """Test predict endpoint - requires model artifact"""
    from src.main import create_app
    app = create_app()
    client = app.test_client()
    response = client.get("/predict")
    assert response.status_code == 200
