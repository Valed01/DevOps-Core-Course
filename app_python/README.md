## Overview
Это приложение на фреймворке FastAPI позволяет получать базовые сведения о системе и состоянии самого приложения.

## Prerequisites
Python 3.14.10, Linux

## Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
Запуск по умолчанию:
```bash
python app.py
```

Запуск с другим портом:
```bash
PORT=8080 python app.py
```

## API Endpoints

| Method | Path      | Description                    |
|--------|-----------|--------------------------------|
| GET    | `/`       | Service and system information |
| GET    | `/health` | Health check                   |

## Configuration

| Variable | Default   | Description                                    |
|----------|-----------|------------------------------------------------|
| `HOST`   | `0.0.0.0` | Адрес, на котором слушает сервер               |
| `PORT`   | `5000`    | Порт сервера                                   |
| `DEBUG`  | `False`   | `true` включает автоперезагрузку при изменениях |

## Docker

Dockerfile: [`Dockerfile`](Dockerfile) (одностадийный) и [`Dockerfile.multi`](Dockerfile.multi) (multi-stage, из него собран опубликованный образ).

### Сборка

Из корня репозитория:
```bash
docker build -f app_python/Dockerfile.multi -t devops-info-service:lab02-multi ./app_python
```

### Запуск

```bash
docker run -d --rm -p 5000:5000 --name lab02-multi devops-info-service:lab02-multi
curl -s http://localhost:5000/health
```

Порт `host:container` — `5000:5000`; приложение внутри контейнера слушает `5000` и работает от непривилегированного пользователя (UID `10001`).

### Скачивание из реестра

Образ опубликован в GHCR и доступен без авторизации:
```bash
docker pull ghcr.io/valed01/devops-info-service:1.0.0
docker run -d --rm -p 5000:5000 ghcr.io/valed01/devops-info-service:1.0.0
```

Страница пакета: https://github.com/users/Valed01/packages/container/package/devops-info-service
