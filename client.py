import httpx
import os


def analyze_remote(logs, limit_ms=200):
    url = os.getenv("API_URL", "http://127.0.0.1:8000/analyze")

    for attempt in range(2):
        try:
            response = httpx.post(
                url,
                params={"limit_ms": limit_ms},
                json=logs,
                timeout=5.0,
            )

            response.raise_for_status()

            return response.status_code, response.json()

        except httpx.ConnectError:
            if attempt == 1:
                raise


if __name__ == "__main__":
    logs = [{"id": "1", "status_code": "500", "duration_ms": "300"}]

    try:
        status, result = analyze_remote(logs, limit_ms=500)

        print("HTTP:", status)
        print("Медленных:", result["slow_count"])
        print("Серверных ошибок:", result["server_error_count"])

    except httpx.ConnectError:
        print("Ошибка: сервер недоступен")

    except httpx.ReadTimeout:
        print("Ошибка: превышено время ожидания ответа")

    except httpx.HTTPStatusError as error:
        print("Ошибка HTTP:", error.response.status_code)

    except httpx.RequestError as error:
        print("Сетевая ошибка:", type(error).__name__)
