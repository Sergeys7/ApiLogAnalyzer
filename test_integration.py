from unittest.mock import patch
from fastapi.testclient import TestClient

from api import app
from client import analyze_remote


def test_client_api_integration(monkeypatch):
    logs = [
        {
            "id": "1",
            "status_code": "500",
            "duration_ms": "300",
        }
    ]

    monkeypatch.setenv("API_URL", "http://testserver/analyze")

    with TestClient(app) as server:

        def send_to_app(url, **kwargs):
            assert url == "http://testserver/analyze"

            kwargs.pop("timeout", None)

            return server.post("/analyze", **kwargs)

        with patch("client.httpx.post", side_effect=send_to_app):
            status, result = analyze_remote(logs, limit_ms=200)

    assert status == 200
    assert result["slow_count"] == 1
    assert result["server_error_count"] == 1
