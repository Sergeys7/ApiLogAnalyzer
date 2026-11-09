import csv


def read_logs(file_path):
    logs = []

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            logs.append(row)

    return logs


def parse_log_integer(value):
    if type(value) is int:
        return value

    if type(value) is str:
        text = value.strip()

        digits = text[1:] if text.startswith("-") else text

        if digits and digits.isascii() and digits.isdecimal():
            return int(text)

    raise ValueError("Ожидается целое число")


def validate_log(log):
    if "status_code" not in log:
        return {"status_code": None, "duration_ms": None, "error": "Отсутствует поле status_code"}

    if "duration_ms" not in log:
        return {"status_code": None, "duration_ms": None, "error": "Отсутствует поле duration_ms"}

    try:
        status_code = parse_log_integer(log["status_code"])
        duration_ms = parse_log_integer(log["duration_ms"])

    except (ValueError, TypeError):
        return {
            "status_code": None,
            "duration_ms": None,
            "error": "Ошибочный статус и/или длительность",
        }

    # Здесь две проверки диапазонов
    if not 100 <= status_code <= 599:
        return {"status_code": None, "duration_ms": None, "error": "Недопустимый HTTP-код"}

    if duration_ms < 0:
        return {"status_code": None, "duration_ms": None, "error": "Отрицательная длительность"}

    # Здесь результат успешной проверки
    return {"status_code": status_code, "duration_ms": duration_ms, "error": None}


def analyze_logs(logs, limit_ms=200):
    total_count = len(logs)
    valid_count = 0
    error_count = 0
    success_count = 0
    http_error_count = 0
    server_error_count = 0
    duration_sum = 0
    errors = []
    slow_count = 0

    for log in logs:
        validation = validate_log(log)
        error = validation["error"]

        if error is None:
            valid_count += 1

            status_code = validation["status_code"]
            if 200 <= status_code <= 299:
                success_count += 1
            elif 400 <= status_code <= 599:
                http_error_count += 1
                if 500 <= status_code <= 599:
                    server_error_count += 1

            duration = validation["duration_ms"]
            duration_sum += duration

            if duration > limit_ms:
                slow_count += 1

        else:
            error_count += 1

            errors.append({"id": log.get("id", "не указан"), "reason": error})

    if valid_count > 0:
        avg_duration_ms = duration_sum / valid_count
    else:
        avg_duration_ms = None

    return {
        "total_count": total_count,
        "valid_count": valid_count,
        "error_count": error_count,
        "success_count": success_count,
        "http_error_count": http_error_count,
        "server_error_count": server_error_count,
        "avg_duration_ms": avg_duration_ms,
        "slow_count": slow_count,
        "errors": errors,
    }


def print_report(result):

    print("Всего записей:", result["total_count"])
    print("Корректных записей:", result["valid_count"])
    print("Ошибочных записей:", result["error_count"])
    print("Успешных HTTP-ответов:", result["success_count"])
    print("HTTP-ошибок:", result["http_error_count"])
    print("SERVER-ошибок:", result["server_error_count"])

    duration = result["avg_duration_ms"]
    if duration is not None:
        print("Средняя длительность:", duration, "мс")
    else:
        print("Средняя длительность: нет данных")

    print("Список ошибок:")

    for error in result["errors"]:
        print(error["id"], "-", error["reason"])


if __name__ == "__main__":
    logs = read_logs("api_logs.csv")
    result = analyze_logs(logs)
    print_report(result)
