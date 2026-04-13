import pytest # type: ignore
from fastapi.testclient import TestClient # type: ignore
from src.api.main import app

@pytest.fixture
def client():
    """Returns a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_texts():
    return [
        "I love this amazing product!",
        "This is terrible and broken.",
        "It's just okay, nothing special."
    ]
