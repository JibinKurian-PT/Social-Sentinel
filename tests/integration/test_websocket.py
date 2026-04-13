import pytest # type: ignore
import json
from fastapi.testclient import TestClient # type: ignore
from src.api.main import app

def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as websocket:
        # Test subscribe message
        data = {"type": "subscribe", "keywords": ["test"]}
        websocket.send_text(json.dumps(data))
        
        # Expect a confirmation back
        response_str = websocket.receive_text()
        response = json.loads(response_str)
        
        assert response["type"] == "subscribed"
        assert response["keywords"] == ["test"]

def test_websocket_ping():
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as websocket:
        # Test ping
        data = {"type": "ping"}
        websocket.send_text(json.dumps(data))
        
        # Expect pong
        response = websocket.receive_json()
        assert response["type"] == "pong"
