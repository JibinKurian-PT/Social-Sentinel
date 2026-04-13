import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app
from src.config import settings

# Sample API Key from settings or mock
API_KEY = settings.API_KEY

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(client):
    """Verify health endpoint is reachable without auth."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["services"]["api"] == "online"

@pytest.mark.asyncio
async def test_prometheus_metrics(client):
    """Verify metrics endpoint is active and public."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    # Prometheus format usually starts with comments or metrics
    assert "# HELP" in response.text or "python_info" in response.text

@pytest.mark.asyncio
async def test_authentication_missing(client):
    """Verify protected endpoints require an API Key."""
    response = await client.get("/api/v1/sentiment/history")
    if settings.API_KEY_ENABLED and settings.API_KEY:
        assert response.status_code == 401
    else:
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_authentication_success(client):
    """Verify protected endpoints work with valid API Key."""
    if not settings.API_KEY_ENABLED or not settings.API_KEY:
        pytest.skip("API Key authentication not enabled")
        
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.get("/api/v1/sentiment/stats", headers=headers)
    assert response.status_code == 200
    assert "stats" in response.json()

@pytest.mark.asyncio
async def test_trends_pagination(client):
    """Verify pagination parameters (limit/offset) on trends router."""
    headers = {"X-API-Key": settings.API_KEY} if settings.API_KEY_ENABLED else {}
    response = await client.get("/api/v1/trends/hourly", params={"limit": 5, "offset": 0}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "aggregates" in data
    assert len(data["aggregates"]) <= 5

@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Verify that multiple rapid requests respond correctly."""
    headers = {"X-API-Key": settings.API_KEY} if settings.API_KEY_ENABLED else {}
    for _ in range(5):
        response = await client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_geo_geocoding_response(client):
    """Verify geo endpoint structure."""
    headers = {"X-API-Key": settings.API_KEY} if settings.API_KEY_ENABLED else {}
    response = await client.get("/api/v1/geo?limit=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    if data:
        item = data[0]
        assert "location" in item
        assert "latitude" in item
        assert "longitude" in item

@pytest.mark.asyncio
async def test_topics_endpoint(client):
    """Verify topics extraction router."""
    headers = {"X-API-Key": settings.API_KEY} if settings.API_KEY_ENABLED else {}
    response = await client.get("/api/v1/topics", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
