
# ApiLogAnalyzer

Учебный проект для анализа журналов HTTP-запросов с использованием Python, FastAPI и HTTPX.

## Возможности

- Чтение HTTP-журналов из CSV.
- Валидация HTTP-статусов и длительности запросов.
- Подсчёт успешных запросов, ошибок и медленных запросов.
- REST API для анализа записей.
- HTTP-клиент с обработкой ошибок и повторными попытками соединения.
- Автоматические тесты на pytest.

## Технологии

Python 3.12, FastAPI, Uvicorn, HTTPX, Pydantic, pytest.

## Установка

Создать виртуальное окружение:

```powershell
python -m venv .venv
```

Активировать его в PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
python -m pip install -r requirements.txt
```

## Запуск API

```powershell
python -m uvicorn api:app --reload
```

Адрес сервера:

http://127.0.0.1:8000

Интерактивная документация FastAPI:

http://127.0.0.1:8000/docs

## Запуск HTTP-клиента

В отдельном терминале, с активированным виртуальным окружением:

```powershell
python client.py
```

По умолчанию клиент обращается к:

http://127.0.0.1:8000/analyze

Адрес можно изменить переменной окружения:

```powershell
$env:API_URL = "http://127.0.0.1:8000/analyze"
python client.py
```

## Запуск тестов

```powershell
python -m pytest -q
```

Для подробного вывода:

```powershell
python -m pytest -v
```

## Архитектура

- `main.py` — бизнес-логика, валидация и анализ журналов.
- `api.py` — REST API на FastAPI.
- `client.py` — HTTP-клиент.
- `test_main.py` — тесты бизнес-логики.
- `test_api.py` — тесты API.
- `test_client.py` — тесты HTTP-клиента.

## Ограничения

- Retry применяется только к ошибкам установления соединения.
- Максимальное количество попыток подключения — две.
- Постоянное хранилище данных не используется.
- Проект предназначен для обучения и демонстрации backend-навыков.
