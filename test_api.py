from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["data_mode"] == "synthetic_demo"

def test_analysis():
    payload = {
        "sleep_hours": 7.5, "activity_index": 76,
        "stress_index": 25, "radiation_index": 18,
        "hr_deviation_index": 5
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    assert "analysis" in response.json()

def test_validation_rejects_out_of_range():
    payload = {
        "sleep_hours": 99, "activity_index": 76,
        "stress_index": 25, "radiation_index": 18,
        "hr_deviation_index": 5
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422

def test_forecast_requires_three_records():
    response = client.post("/api/forecast", json={"history": []})
    assert response.status_code == 422
