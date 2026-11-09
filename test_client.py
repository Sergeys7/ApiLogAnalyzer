import pytest
import httpx

from unittest.mock import patch
from client import analyze_remote


def test_analyze_remote():
    logs = [{"id": "1", "status_code": "500", "duration_ms": "300"}]

    with patch("client.httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"slow_count": 0, "server_error_count": 1}

        status, result = analyze_remote(logs, limit_ms=350)

        assert status == 200
        assert result["slow_count"] == 0
        assert result["server_error_count"] == 1

        mock_post.assert_called_once_with(
            "http://127.0.0.1:8000/analyze",
            params={"limit_ms": 350},
            json=logs,
            timeout=5.0,
        )


def test_connect_error():
    logs = [{"id": "1", "status_code": "200", "duration_ms": "120"}]

    with patch("client.httpx.post") as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(httpx.ConnectError):
            analyze_remote(logs)


def test_read_timeout():
    logs = [{"id": "1", "status_code": "200", "duration_ms": "120"}]

    with patch("client.httpx.post") as mock_post:
        mock_post.side_effect = httpx.ReadTimeout("Read timed out")

        with pytest.raises(httpx.ReadTimeout):
            analyze_remote(logs)

        assert mock_post.call_count == 1


def test_http_status_error():
    logs = [{"id": "1", "status_code": "200", "duration_ms": "120"}]

    request = httpx.Request("POST", "http://127.0.0.1:8000/analyze")

    response = httpx.Response(status_code=404, request=request)

    with patch("client.httpx.post", return_value=response):
        with pytest.raises(httpx.HTTPStatusError) as error:
            analyze_remote(logs)

    assert error.value.response.status_code == 404


def test_api_url_from_environment(monkeypatch):
    logs = [{"id": "1", "status_code": "200", "duration_ms": "120"}]

    test_url = "https://api.example.test/analyze"

    monkeypatch.setenv("API_URL", test_url)

    with patch("client.httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "slow_count": 0,
            "server_error_count": 0,
        }

        status, result = analyze_remote(logs, limit_ms=350)

        mock_post.assert_called_once_with(
            test_url,
            params={"limit_ms": 350},
            json=logs,
            timeout=5.0,
        )

        assert status == 200
        assert result["slow_count"] == 0


def test_retry_after_connect_error():
    logs = [{"id": "1", "status_code": "500", "duration_ms": "300"}]

    request = httpx.Request("POST", "http://127.0.0.1:8000/analyze")

    response = httpx.Response(
        status_code=200,
        json={
            "slow_count": 0,
            "server_error_count": 1,
        },
        request=request,
    )

    with patch("client.httpx.post") as mock_post:
        mock_post.side_effect = [
            httpx.ConnectError("Connection refused"),
            response,
        ]

        status, result = analyze_remote(logs, limit_ms=500)

        assert status == 200
        assert result["slow_count"] == 0
        assert result["server_error_count"] == 1

        assert mock_post.call_count == 2


def test_retry_exhausted():
    logs = [{"id": "1", "status_code": "500", "duration_ms": "300"}]

    with patch("client.httpx.post") as mock_post:
        mock_post.side_effect = [
            httpx.ConnectError("First connection failed"),
            httpx.ConnectError("Second connection failed"),
        ]

        with pytest.raises(httpx.ConnectError):
            analyze_remote(logs, limit_ms=500)

        assert mock_post.call_count == 2
