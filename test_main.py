import pytest
from main import validate_log, analyze_logs, read_logs


def test_valid_log():
    log = {"id": "1", "status_code": "200", "duration_ms": "120"}

    result = validate_log(log)

    assert result["status_code"] == 200
    assert result["duration_ms"] == 120
    assert result["error"] is None


def test_duration_absence():
    log = {"id": "1", "status_code": "200"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Отсутствует поле duration_ms"


def test_status_absence():
    log = {"id": "1", "duration_ms": "120"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Отсутствует поле status_code"


def test_invalid_number():
    log = {"id": "1", "status_code": "200", "duration_ms": "abc"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Ошибочный статус и/или длительность"


def test_invalid_status_code():
    log = {"id": "1", "status_code": "700", "duration_ms": "120"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Недопустимый HTTP-код"


def test_negative_duration():
    log = {"id": "1", "status_code": "200", "duration_ms": "-5"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Отрицательная длительность"


def test_boundaries():
    log = {"id": "1", "status_code": "100", "duration_ms": "0"}

    result = validate_log(log)

    assert result["status_code"] == 100
    assert result["duration_ms"] == 0
    assert result["error"] is None

    log = {"id": "1", "status_code": "599", "duration_ms": "0"}

    result = validate_log(log)

    assert result["status_code"] == 599
    assert result["duration_ms"] == 0
    assert result["error"] is None

    log = {"id": "1", "status_code": "99", "duration_ms": "120"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Недопустимый HTTP-код"

    log = {"id": "1", "status_code": "600", "duration_ms": "120"}

    result = validate_log(log)

    assert result["status_code"] is None
    assert result["duration_ms"] is None
    assert result["error"] == "Недопустимый HTTP-код"


def test_analyze_logs():
    logs = [
        {"id": "1", "status_code": "200", "duration_ms": "120"},
        {"id": "2", "status_code": "500", "duration_ms": "300"},
        {"id": "3", "status_code": "201", "duration_ms": "80"},
        {"id": "4", "status_code": "429", "duration_ms": "abc"},
        {"id": "5", "status_code": "404", "duration_ms": "100"},
        {"id": "6", "status_code": "302", "duration_ms": "50"},
    ]

    result = analyze_logs(logs)

    assert result["total_count"] == 6
    assert result["valid_count"] == 5
    assert result["error_count"] == 1
    assert result["success_count"] == 2
    assert result["http_error_count"] == 2
    assert result["avg_duration_ms"] == 130
    assert len(result["errors"]) == 1
    assert result["errors"][0]["id"] == "4"
    assert result["errors"][0]["reason"] == "Ошибочный статус и/или длительность"


def test_analyze_logs_empty():
    logs = []

    result = analyze_logs(logs)

    assert result["total_count"] == 0
    assert result["valid_count"] == 0
    assert result["error_count"] == 0
    assert result["success_count"] == 0
    assert result["http_error_count"] == 0
    assert result["avg_duration_ms"] is None


def test_read_logs():
    result = read_logs("api_logs.csv")

    assert len(result) == 6
    assert result[0]["status_code"] == "200"
    assert result[3]["duration_ms"] == "abc"


def test_analyze_logs_empty_errors():
    logs = []

    result = analyze_logs(logs)

    assert result["errors"] == []


def test_missing_id():
    logs = [{"status_code": "200", "duration_ms": "abc"}]

    result = analyze_logs(logs)

    assert result["error_count"] == 1
    assert result["errors"][0]["id"] == "не указан"
    assert result["errors"][0]["reason"] == "Ошибочный статус и/или длительность"


def test_slow_count():
    logs = [
        {"id": "1", "status_code": "200", "duration_ms": "120"},
        {"id": "2", "status_code": "500", "duration_ms": "300"},
        {"id": "3", "status_code": "429", "duration_ms": "abc"},
    ]

    result = analyze_logs(logs)

    assert result["slow_count"] == 1

    result = analyze_logs(logs, 500)

    assert result["slow_count"] == 0


def test_server_count():
    logs = [
        {"id": "1", "status_code": "200", "duration_ms": "80"},
        {"id": "2", "status_code": "404", "duration_ms": "90"},
        {"id": "3", "status_code": "500", "duration_ms": "150"},
        {"id": "4", "status_code": "503", "duration_ms": "210"},
        {"id": "5", "status_code": "700", "duration_ms": "100"},
        {"id": "6", "status_code": "500", "duration_ms": "abc"},
    ]

    result = analyze_logs(logs)

    assert result["total_count"] == 6
    assert result["valid_count"] == 4
    assert result["error_count"] == 2
    assert result["http_error_count"] == 3
    assert result["server_error_count"] == 2


@pytest.mark.parametrize(
    "status_code, duration_ms",
    [
        (200.8, 120),
        (200, 12.6),
    ],
)
def test_validate_log_rejects_fractional_values(status_code, duration_ms):
    log = {
        "status_code": status_code,
        "duration_ms": duration_ms,
    }

    result = validate_log(log)

    assert result["error"] is not None


@pytest.mark.parametrize("duration_ms", [True, False])
def test_validate_log_rejects_bool(duration_ms):
    log = {
        "status_code": 200,
        "duration_ms": duration_ms,
    }

    result = validate_log(log)

    assert result["error"] is not None


@pytest.mark.parametrize("value", [200.0, 200.8, True, False, None, "abc"])
def test_validate_log_rejects_invalid_types(value):
    log = {
        "status_code": 200,
        "duration_ms": value,
    }

    result = validate_log(log)

    assert result["error"] is not None
