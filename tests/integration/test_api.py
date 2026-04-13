import pytest # type: ignore

def test_health_endpoint(client):
    response = client.get("/health")
    # Even if DB is offline in test env, endpoint should return 200
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data

def test_analyze_sentiment_single(client):
    payload = {"text": "What a beautiful day!"}
    response = client.post("/api/v1/sentiment/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] in ["positive", "negative", "neutral"]
    assert "polarity" in data
    assert "confidence" in data

def test_analyze_sentiment_batch(client, sample_texts):
    payload = {"texts": sample_texts}
    response = client.post("/api/v1/sentiment/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "metrics" in data
    assert len(data["results"]) == len(sample_texts)

def test_trends_hourly(client):
    response = client.get("/api/v1/trends/hourly?hours=5")
    assert response.status_code == 200
    data = response.json()
    assert data["timeframe"] == "5h"
    assert "aggregates" in data

def test_geo_mock(client):
    response = client.get("/api/v1/geo")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
