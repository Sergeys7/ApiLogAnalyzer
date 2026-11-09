import httpx


if __name__ == "__main__":
    try:
        response = httpx.get("http://127.0.0.1:8000/unknown", timeout=5.0)

        response.raise_for_status()

        print("HTTP:", response.status_code)

    except httpx.HTTPStatusError as error:
        print("Ошибка HTTP:", error.response.status_code)
