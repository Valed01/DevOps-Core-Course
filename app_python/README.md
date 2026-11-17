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
