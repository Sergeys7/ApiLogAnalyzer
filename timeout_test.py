import httpx


if __name__ == "__main__":
    try:
        response = httpx.get("http://127.0.0.1:8000/slow", timeout=0.5)

        print("HTTP:", response.status_code)

    except httpx.ReadTimeout:
        print("Ошибка: сервер не ответил вовремя")
