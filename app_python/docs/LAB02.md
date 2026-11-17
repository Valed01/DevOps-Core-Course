# Лаба 2 — Контейнеризация с Docker

## 1. Решения в Dockerfile

Файл: [`app_python/Dockerfile`](../Dockerfile)

```dockerfile
FROM python:3.15.2-slim-trixie # фиксированный образ слим для быстрой установки
WORKDIR /app                   # настройка директории
RUN useradd --uid 10001 --create-home --shell /bin/bash app # создание нового пользователя что бы не запускать приложение от root
COPY requirements.txt .        # копирование зависимостей отдельным слоем т.к. они изменяются реже основного кода
USER 10001                     # выбор юзера
RUN pip install --user -r requirements.txt # установка зависимостей
COPY . .                       # копирование кода приложения
EXPOSE 5000                    # фиксирование порта
CMD ["python", "app.py"]       # запуск через exec-форму т.к. у приложения PID 2
```

### `.dockerignore`

Файл: [`app_python/.dockerignore`](../.dockerignore)

```gitignore
.git
.venv
venv/
__pycache__/
.env
*.pyc
docs/
tests/
README.md
.idea/
.vscode/
```

---

## 2. Сборка и запуск — подтверждение работы (задание 2.4)

### Лог сборки (конец)

```text
$ docker build -t devops-info-service:lab02 ./app_python
 => [3/6] RUN useradd --uid 10001 --create-home --shell /bin/bas  0.3s
 => [4/6] COPY requirements.txt .                                 0.0s
 => [5/6] RUN pip install --user -r requirements.txt             15.5s
 => [6/6] COPY . .                                                0.0s
 => exporting to image                                            3.7s
 => => exporting layers                                           1.1s
 => => exporting manifest sha256:37efda9865e9844d4b060a11a1763d8  0.0s
 => => exporting config sha256:054c2875b4e21e5be04f9a06948d02e47  0.0s
 => => exporting attestation manifest sha256:ce65cbf804d954dded1  0.0s
 => => exporting manifest list sha256:358b07bb86a453fd0e95548f92  0.0s
 => => naming to docker.io/library/devops-info-service:lab02      0.0s
 => => unpacking to docker.io/library/devops-info-service:lab02   2.6s
```

### Запуск

```text
$ docker run -d --rm -p 5000:5000 --name lab02 devops-info-service:lab02
dd20da23343201475d7143fed856552522d46f2e7c0445abd88e195ca842a05a
```

### `GET /`

```text
$ curl -s http://localhost:5000/ | jq .
```

```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "dd20da233432",
    "platform": "Linux",
    "platform_version": "#1 SMP PREEMPT_DYNAMIC Tue, 03 Nov 2026 12:37:21 +0000",
    "architecture": "x86_64",
    "cpu_count": 12,
    "python_version": "3.15.2"
  },
  "runtime": {
    "uptime_seconds": 32,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-11-17T03:37:03.954835+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "172.17.0.1",
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

### `GET /health`

```text
$ curl -s http://localhost:5000/health | jq -c .
{"status":"OK","timestamp":"2026-11-17T03:38:05.065281+00:00","uptime_seconds":93}
```

### Контейнер работает не от root

```text
$ docker run --rm devops-info-service:lab02 id -u
10001
```

### Размер образа

```text
$ docker images devops-info-service --format '{{.Tag}}\t{{.Size}}'
lab02	219MB
lab02-multi	225MB
```

### Слои (`docker history`)

```text
$ docker history devops-info-service:lab02
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
c6f140ebef32   8 minutes ago    CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      8 minutes ago    EXPOSE [5000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      8 minutes ago    COPY . . # buildkit                             28.7kB    buildkit.dockerfile.v0
<missing>      8 minutes ago    RUN /bin/sh -c pip install --user -r require…   25.8MB    buildkit.dockerfile.v0
<missing>      8 minutes ago    USER 10001                                      0B        buildkit.dockerfile.v0
<missing>      36 minutes ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      36 minutes ago   RUN /bin/sh -c useradd --uid 10001 --create-…   69.6kB    buildkit.dockerfile.v0
<missing>      38 minutes ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      11 days ago      CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      11 days ago      RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      11 days ago      RUN /bin/sh -c set -eux;   savedAptMark="$(a…   45.1MB    buildkit.dockerfile.v0
<missing>      11 days ago      ENV PYTHON_SHA256=8b5536d280142ecf6cdfe15d12…   0B        buildkit.dockerfile.v0
<missing>      11 days ago      ENV PYTHON_VERSION=3.15.2                       0B        buildkit.dockerfile.v0
<missing>      11 days ago      RUN /bin/sh -c set -eux;  apt-get update;  a…   4.93MB    buildkit.dockerfile.v0
<missing>      11 days ago      ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      11 days ago      ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      12 days ago      # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.7MB    debuerreotype 0.17
```

### Самый большой слой

Самый большой слой - `debian.sh ... 'trixie'` (**87.7MB**): это корневая ФС Debian из базового образа, а не мои зависимости (`pip install` - 25.8MB) и не код (`COPY . .` - 28.7kB).

---

## 3. Multi-stage сборка (задание 3.3)

### `Dockerfile.multi`

Файл: [`app_python/Dockerfile.multi`](../Dockerfile.multi)

```dockerfile
# syntax=docker/dockerfile:1

# ---------- Стадия 1: builder ----------
FROM python:3.15.2-slim-trixie AS builder
WORKDIR /app
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install -r requirements.txt

# ---------- Стадия 2: runtime ----------
FROM python:3.15.2-slim-trixie AS runtime
RUN useradd --uid 10001 --create-home --shell /bin/bash app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
USER 10001
EXPOSE 5000
CMD ["python", "app.py"]
```

### Сборка и запуск

```text
$ docker build -f app_python/Dockerfile.multi -t devops-info-service:lab02-multi ./app_python
$ docker run -d --rm -p 5000:5000 --name lab02-multi devops-info-service:lab02-multi
```

### Сравнение размеров

```text
$ docker images devops-info-service --format '{{.Tag}}\t{{.Size}}'
lab02-multi    225MB
lab02    219MB
```

| Образ | Размер | Слой с зависимостями |
|---|---|---|
| `lab02` (одностадийный) | 219MB | `pip install --user` - 25.8MB |
| `lab02-multi` | 225MB | `COPY /opt/venv` - 33.2MB |

### Вывод

<!-- TODO: абзац своими словами — уменьшил / примерно так же / увеличил и почему (компилируемые wheel, инструменты сборки, pip внутри venv) -->

### `GET /health` из multi-stage контейнера

```text
$ curl -s localhost:5000/health
{"status":"OK","timestamp":"2026-11-17T04:11:39.453524+00:00","uptime_seconds":47}
```

---

## 4. Сканирование Trivy

### 4.2 — Таблица по уровням критичности

Образ: `devops-info-service:lab02-multi` · Trivy 0.76.2 · сканирование 2026-11-17

```text
$ trivy image devops-info-service:lab02-multi
...
devops-info-service:lab02-multi (debian 13.7)
Total: 211 (UNKNOWN: 5, LOW: 65, MEDIUM: 93, HIGH: 48, CRITICAL: 0)
...
Python (python-pkg)
Total: 8 (UNKNOWN: 0, LOW: 1, MEDIUM: 2, HIGH: 5, CRITICAL: 0)
```

| Критичность | ОС (debian 13.7) | Python-пакеты | Всего |
| ----------- | ---------------: | ------------: | ----: |
| CRITICAL    |                0 |             0 |     0 |
| HIGH        |               48 |             5 |    53 |
| MEDIUM      |               93 |             2 |    95 |
| LOW         |               65 |             1 |    66 |
| UNKNOWN     |                5 |             0 |     5 |
| **Всего**   |          **211** |         **8** | **219** |

Пакеты из `requirements.txt` (fastapi, uvicorn, pydantic, starlette и др. в `/opt/venv`) - **0 находок**. Почти все уязвимости приходят из базового образа Debian, а 8 Python-находок - из `msgpack`, `setuptools` и `urllib3`, которые не входят в мои зависимости.

---

## 5. Публикация в реестре (задание 5.4)

Реестр: **GHCR** стратегия тегирования: **SemVer** (`1.0.0` - совпадает с `"version": "1.0.0"` в ответе `GET /`).

### Логин, тег и push

Токен (PAT classic, `write:packages`) вводится через `read -rs`, чтобы не попасть в историю shell, и передаётся через `--password-stdin`:

```text
$ read -rs "GHCR_PAT?PAT: "
$ echo "$GHCR_PAT" | docker login ghcr.io -u Valed01 --password-stdin
Login Succeeded

$ docker tag devops-info-service:lab02-multi ghcr.io/valed01/devops-info-service:1.0.0
$ docker push ghcr.io/valed01/devops-info-service:1.0.0
The push refers to repository [ghcr.io/valed01/devops-info-service]
44136fa355b3: Mounted from linkwarden/linkw
37fb86c2a767: Pushed
02eda710b2e8: Pushed
490d435ea363: Pushed
ba56bf6127ad: Pushed
f01b8d07ba2a: Pushed
2e7409f36052: Pushed
b77003139ce3: Pushed
2b07422484ed: Pushed
1affd845ad18: Pushed
1.0.0: digest: sha256:790d30fbcfc4514933a692f30bc1da06e53150960794544e6410e4f0f2aa02a1 size: 856
```

### Pull без авторизации

После push пакет переключён в **Public** (Package settings → Change visibility). Проверка без закэшированных учётных данных:

```text
$ docker logout ghcr.io
Removing login credentials for ghcr.io
$ docker rmi ghcr.io/valed01/devops-info-service:1.0.0
Untagged: ghcr.io/valed01/devops-info-service:1.0.0
$ docker pull ghcr.io/valed01/devops-info-service:1.0.0
1.0.0: Pulling from valed01/devops-info-service
Digest: sha256:790d30fbcfc4514933a692f30bc1da06e53150960794544e6410e4f0f2aa02a1
Status: Downloaded newer image for ghcr.io/valed01/devops-info-service:1.0.0
ghcr.io/valed01/devops-info-service:1.0.0
```

Digest при pull совпадает с digest из push - скачан именно опубликованный образ.

### URL реестра

- Пакет: https://github.com/users/Valed01/packages/container/package/devops-info-service
- Образ: `ghcr.io/valed01/devops-info-service:1.0.0`

### Раздел Docker в README

См. [`app_python/README.md` → Docker](../README.md#docker): сборка, запуск и публичный pull.

---

## 6. Проблемы и решения

### 6.1 `useradd: invalid user ID 'id'`

**Симптом:** сборка падала на шаге создания пользователя:

```text
 > [3/6] RUN useradd -uid 10001 --create-home --shell /bin/bash app:
0.361 useradd: invalid user ID 'id'
ERROR: failed to build: ... exit code: 3
```

**Причина:** короткие флаги состоят из одной буквы, поэтому `-uid` разбирается как `-u id` (UID = строка `id`), а `10001` становится лишним аргументом.

**Решение:** длинная форма с двумя дефисами - `--uid 10001` (или короткая `-u 10001`).

### 6.2 Контейнер молча умирал: `ModuleNotFoundError: No module named 'uvicorn'`

**Симптом:** `docker run -d --rm ...` возвращал ID контейнера, но `curl -s localhost:5000/` ничего не выводил. В `docker ps` контейнера не было, `docker logs` - `No such container`: из-за `--rm` упавший контейнер удалялся вместе с логами. Запуск без `-d` показал ошибку:

```text
  File "/app/app.py", line 9, in <module>
    import uvicorn
ModuleNotFoundError: No module named 'uvicorn'
```

**Причина:** `RUN pip install --user` выполнялся **до** `USER 10001`, то есть от root, и пакеты ставились в `/root/.local`. Приложение запускалось от `app` и искало пакеты в `/home/app/.local`, где пусто (а к `/root` у него нет доступа).

**Решение:** перенёс `USER 10001` выше `pip install --user`, чтобы пакеты ставились в домашний каталог того же пользователя, от которого работает приложение. `COPY` от `USER` не зависит (файлы всегда принадлежат root), поэтому код по-прежнему доступен приложению только на чтение.

**Вывод для отладки:** при проблемах запускать контейнер без `-d` и `--rm`, иначе ошибка старта не видна.

### 6.3 Multi-stage: снова `No module named 'uvicorn'`

**Симптом:** образ `lab02-multi` собирался, но контейнер падал с той же ошибкой, что в 6.2.

**Причина:** в runtime-стадии было `ENV PATH="/opt/venv:$PATH"`. Исполняемые файлы venv лежат в `/opt/venv/bin`, а не в корне venv, поэтому `python` из `CMD` находился как системный `/usr/local/bin/python`, который не видит пакеты из venv.

**Решение:** `ENV PATH="/opt/venv/bin:$PATH"`. Проверка: `docker run --rm devops-info-service:lab02-multi which python` → `/opt/venv/bin/python`.

### 6.4 `unknown shorthand flag: 'f' in -f` при запуске

**Симптом:** `docker run -f app_python/Dockerfile.multi ...` → `unknown shorthand flag: 'f'`.

**Причина:** `-f` (путь к Dockerfile) - флаг `docker build`. `docker run` запускает уже собранный образ и Dockerfile не использует. Кроме того, в команде был указан тег `lab02` (одностадийный образ) вместо `lab02-multi`.

**Решение:** `-f` - только при сборке, при запуске - нужный тег: `docker run ... devops-info-service:lab02-multi`.

### 6.5 GHCR: `docker pull` → `denied`

**Симптом:** проверка публичного доступа (`logout` → `rmi` → `pull`) падала с `error from registry: denied`.

**Причина:** образ ни разу не был загружен: `docker push` был запущен без аргумента и завершился ошибкой `requires 1 argument`, а `docker tag` создаёт только локальное имя. Скачивать из реестра было нечего.

**Решение:** заново `docker login`, `docker tag` и `docker push` с полным именем `ghcr.io/valed01/devops-info-service:1.0.0`, затем переключение пакета в Public и только после этого проверка pull без авторизации. Отдельно учтено, что путь в GHCR должен быть в нижнем регистре (`valed01`, а не `Valed01`).
