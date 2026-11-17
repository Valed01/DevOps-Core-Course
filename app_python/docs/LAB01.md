# Lab 01 — DevOps Info Service

## 1. Framework Selection

Я выбрал **FastAPI**: это лёгкий и быстрый фреймворк, заточенный именно под API. Он из коробки поддерживает `async`, валидирует данные через Pydantic и автоматически генерирует OpenAPI-документацию (`/docs`). Flask проще, но async и документацию в нём пришлось бы добавлять вручную, а Django для сервиса из двух эндпоинтов избыточен.

| Критерий                 | Flask 3.1      | FastAPI 0.136  | Django 5.2               |
| ------------------------ | -------------- | -------------- | ------------------------ |
| Тип                      | Микрофреймворк | API-фреймворк  | Full-stack               |
| Размер / легковесность   | Очень лёгкий   | Лёгкий         | Тяжёлый                  |
| Асинхронность            | Ограниченная   | Отличная       | Поддерживается           |
| Скорость                 | Хорошая        | Очень высокая  | Хорошая                  |
| REST API                 | Вручную        | Встроено       | Через DRF                |
| ORM                      | Сторонняя      | Сторонняя      | Встроенная               |
| Админка                  | Нет            | Нет            | Встроенная               |
| Валидация                | Вручную        | Pydantic       | Forms/Models             |
| OpenAPI / документация   | Вручную        | Автоматическая | Доп. библиотеки          |
| Порог входа              | Низкий         | Средний        | Средний/высокий          |
| Основное применение      | Микросервисы   | API, SaaS      | CRM, ERP, веб-приложения |

## 2. Best Practices Applied

- **Конфигурация через переменные окружения (`HOST`, `PORT`, `DEBUG`)** — один и тот же код запускается в разных окружениях без правок.
- **`DEBUG` приводится к bool через сравнение строки** — `bool("False")` в Python равно `True`, и так легко случайно включить отладку в продакшене.
- **Зафиксированные версии зависимостей (`==`)** — сборка воспроизводима и не сломается от нового релиза библиотеки.
- **Datetime с часовым поясом (UTC)** — смешение naive и aware datetime даёт `TypeError`, а UTC не зависит от настроек сервера.
- **JSON-обработчики ошибок 404 и 500** — клиент всегда получает ответ в едином формате, а не HTML-страницу.
- **Логирование через `logging` (уровень INFO, формат со временем и уровнем) вместо `print()`** — логи можно фильтровать по уровню, и по времени видно, когда что произошло.
- **Дешёвый `/health`** — без обращений к БД и внешним сервисам, чтобы его можно было часто дёргать из liveness/readiness-проб.
- **Блок `if __name__ == "__main__"`** — сервер стартует только при прямом запуске, а импорт модуля (тесты, `uvicorn app:app`) его не запускает.
- **Импорты сгруппированы по PEP 8** — стандартная библиотека → сторонние пакеты, так проще читать и видеть зависимости.
- **`.gitignore` для `venv/`, `__pycache__/`, `*.pyc`, `*.log`, IDE** — в репозиторий не попадают артефакты сборки и локальные файлы.

## 3. API Documentation

### `GET /` — информация о сервисе и системе

Запрос:

```bash
curl -s http://localhost:5000/
```

Ответ (`200 OK`):

```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "arch",
    "platform": "Linux",
    "platform_version": "#1 SMP PREEMPT_DYNAMIC Tue, 03 Nov 2026 12:37:21 +0000",
    "architecture": "x86_64",
    "cpu_count": 12,
    "python_version": "3.14.10"
  },
  "runtime": {
    "uptime_seconds": 16,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-11-17T00:35:21.251752+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "curl/8.23.0",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    { "path": "/", "method": "GET", "description": "Service and system information" },
    { "path": "/health", "method": "GET", "description": "Health check" }
  ]
}
```

### `GET /health` — проверка состояния

Запрос:

```bash
curl -s http://localhost:5000/health
```

Ответ (`200 OK`):

```json
{
  "status": "OK",
  "timestamp": "2026-11-17T00:36:39.064877+00:00",
  "uptime_seconds": 94
}
```

### Ошибка — несуществующий путь

Запрос:

```bash
curl -s http://localhost:5000/nope
```

Ответ (`404 Not Found`):

```json
{
  "error": "Not Found",
  "message": "Endpoint does not exist",
  "path": "/nope",
  "timestamp": "2026-11-17T01:07:32.411494+00:00"
}
```

## 4. Testing Evidence

**1. Полный JSON корневого эндпоинта**

```console
$ curl -s http://localhost:5000/ | jq .
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "arch",
    "platform": "Linux",
    "platform_version": "#1 SMP PREEMPT_DYNAMIC Tue, 03 Nov 2026 12:37:21 +0000",
    "architecture": "x86_64",
    "cpu_count": 12,
    "python_version": "3.14.10"
  },
  "runtime": {
    "uptime_seconds": 16,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-11-17T00:35:21.251752+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "curl/8.23.0",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {
      "path": "/",
      "method": "GET",
      "description": "Service and system information"
    },
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check"
    }
  ]
}
```

**2. Health check**

```console
$ curl -s http://localhost:5000/health | jq .
{
  "status": "OK",
  "timestamp": "2026-11-17T00:36:39.064877+00:00",
  "uptime_seconds": 94
}
```

**3. Обработчик 404**

```console
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:5000/nope
HTTP 404
```

**4. Смена порта через `PORT`**

Терминал 1:

```console
$ PORT=8080 python app.py
INFO:     Started server process [274194]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     127.0.0.1:49088 - "GET /health HTTP/1.1" 200 OK
```

Терминал 2:

```console
$ curl -s http://localhost:8080/health | jq .
{
  "status": "OK",
  "timestamp": "2026-11-17T01:07:32.403455+00:00",
  "uptime_seconds": 0
}
```

**Структура проекта**

```console
$ find app_python -maxdepth 2 -type f | sort
app_python/app.py
app_python/docs/LAB01.md
app_python/.gitignore
app_python/.gitkeep
app_python/__pycache__/app.cpython-314.pyc
app_python/README.md
app_python/requirements.txt
app_python/tests/__init__.py
```

## 5. Challenges & Solutions

**Проблема:** расчёт аптайма. Сначала я не понимал, от какой точки считать время работы сервиса.
**Решение:** зафиксировал `START_TIME = datetime.now(timezone.utc)` на уровне модуля, то есть в момент старта приложения, а аптайм считаю при каждом запросе как разницу между текущим временем и `START_TIME`. Обе даты с часовым поясом UTC, иначе вычитание падает с `TypeError`.

## 6. GitHub Community

**GitHub username:** Valed01
