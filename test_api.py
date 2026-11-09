from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0"}


def test_hello():
    response = client.get("/hello/Petr")

    assert response.status_code == 200
    assert response.json() == {"message": "Привет, Petr"}


def test_status():
    response = client.get("/status/200")

    assert response.status_code == 200

    result = response.json()

    assert result["code"] == 200
    assert result["is_error"] is False

    response = client.get("/status/500")

    assert response.status_code == 200

    result = response.json()

    assert result["code"] == 500
    assert result["is_error"] is True


def test_status_invalid():
    response = client.get("/status/abc")

    assert response.status_code == 422


def test_analyze_invalid_body():
    data = {"id": "1", "status_code": "200", "duration_ms": "120"}

    response = client.post("/analyze", json=data)

    assert response.status_code == 422


def test_analyze_valid_body():
    logs = [
        {"id": "1", "status_code": "200", "duration_ms": "120"},
        {"id": "2", "status_code": "500", "duration_ms": "300"},
        {"id": "3", "status_code": "429", "duration_ms": "abc"},
    ]

    response = client.post("/analyze", json=logs)

    assert response.status_code == 200

    result = response.json()

    assert result["total_count"] == 3
    assert result["valid_count"] == 2
    assert result["error_count"] == 1
    assert result["success_count"] == 1
    assert result["http_error_count"] == 1
    assert result["server_error_count"] == 1
    assert result["avg_duration_ms"] == 210

    assert len(result["errors"]) == 1
    assert result["errors"][0]["id"] == "3"
    assert result["errors"][0]["reason"] == "Ошибочный статус и/или длительность"


def test_analyze_null_duration():
    logs = [{"id": "8", "status_code": "200", "duration_ms": None}]

    response = client.post("/analyze", json=logs)

    assert response.status_code == 200

    result = response.json()

    assert result["valid_count"] == 0
    assert result["error_count"] == 1
    assert result["errors"][0]["id"] == "8"
    assert result["errors"][0]["reason"] == "Ошибочный статус и/или длительность"


def test_status_query():
    response = client.get("/status", params={"code": 404})

    assert response.status_code == 200
    assert response.json() == {"code": 404, "is_error": True}


def test_check_duration():
    response = client.get("/check-duration", params={"duration_ms": 300})

    assert response.status_code == 200

    result = response.json()

    assert result["limit_ms"] == 200
    assert result["slow"] is True

    response = client.get("/check-duration", params={"duration_ms": 300, "limit_ms": 500})

    assert response.status_code == 200

    result = response.json()

    assert result["limit_ms"] == 500
    assert result["slow"] is False


def test_analyze_custom_limit():
    logs = [{"id": "1", "status_code": "200", "duration_ms": "300"}]

    response = client.post("/analyze", params={"limit_ms": 500}, json=logs)

    assert response.status_code == 200

    result = response.json()

    assert result["slow_count"] == 0


def test_analyze_negative_limit():
    logs = [{"id": "1", "status_code": "200", "duration_ms": "50"}]

    response = client.post("/analyze", params={"limit_ms": -100}, json=logs)

    assert response.status_code == 422
