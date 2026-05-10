# TestProject

Backend-сервис для сбора статистики с устройств и расчета аналитики по этим данным.

Проект написан на FastAPI, использует SQLAlchemy для работы с базой данных, SQLite как простое файловое хранилище, Redis как брокер сообщений и Celery для фонового расчета аналитики.

## Что умеет сервис

- Создавать пользователей.
- Создавать устройства.
- Назначать устройство пользователю.
- Принимать статистику устройства по трем показателям: `x`, `y`, `z`.
- Запускать расчет аналитики по устройству в фоне через Celery.
- Запускать расчет аналитики по всем устройствам пользователя в фоне через Celery.
- Проверять статус фоновой задачи и получать результат по `task_id`.

Для каждого показателя сервис считает:

- `minimum`
- `maximum`
- `count`
- `sum`
- `median`

## Архитектура

Проект разделен на несколько слоев:

```text
HTTP API -> services -> db/models -> database
          -> Celery tasks -> Redis -> Celery worker
          -> schemas
```

Основной HTTP-сервис не рассчитывает аналитику прямо во время запроса. Вместо этого API ставит задачу в очередь Celery и сразу возвращает клиенту `task_id`.

Расчет выполняет отдельный Celery worker. Результат задачи сохраняется в Redis result backend, после чего его можно получить через API.

## Асинхронность и Celery

В проекте используется не `asyncio`, а фоновая обработка через Celery.

Задачи в `app/tasks/analytics.py` являются обычными синхронными Python-функциями. Декоратор `@celery_app.task` регистрирует их как Celery-задачи, чтобы их можно было отправлять в очередь:

```python
task = analyze_user_task.delay(user_id)
```

После вызова `.delay()` задача попадает в Redis, а отдельный Celery worker забирает ее и выполняет в другом процессе.

Для аналитических задач настроены:

- автоматические повторы при исключениях;
- максимум 3 retry;
- задержка перед повтором;
- `retry_backoff`;
- `retry_jitter`;
- `soft_time_limit`;
- `time_limit`.

Ситуации вроде `User not found` или `Device not found` возвращаются как обычный результат задачи и не ретраятся.

## Основные эндпоинты

```text
GET  /health

POST /users
POST /users/{user_id}/analytics/tasks

POST /devices
POST /devices/{device_id}/assign/{user_id}
POST /devices/{device_id}/stats
POST /devices/{device_id}/analytics/tasks

GET  /tasks/{task_id}
```

Swagger UI доступен по адресу:

```text
http://127.0.0.1:8000/docs
```

## Примеры запросов

### Создать пользователя

```http
POST /users
```

```json
{
  "username": "alice"
}
```

Пример ответа:

```json
{
  "id": 1,
  "username": "alice"
}
```

### Создать устройство

```http
POST /devices
```

```json
{
  "identifier": "device-001"
}
```

Пример ответа:

```json
{
  "id": 1,
  "identifier": "device-001"
}
```

### Назначить устройство пользователю

```http
POST /devices/1/assign/1
```

Пример ответа:

```json
{
  "status": "assigned"
}
```

### Добавить статистику устройства

```http
POST /devices/1/stats
```

```json
{
  "x": 10,
  "y": 20,
  "z": 30
}
```

Пример ответа:

```json
{
  "status": "ok"
}
```

### Запустить аналитику по устройству

```http
POST /devices/1/analytics/tasks
```

Можно передать временной диапазон query-параметрами:

```text
POST /devices/1/analytics/tasks?start=2026-05-10T00:00:00&end=2026-05-10T23:59:59
```

Пример ответа:

```json
{
  "task_id": "0f3a9b3c-2c61-4db5-a09d-8f7c4e73d7f6",
  "status": "started"
}
```

### Запустить аналитику по пользователю

```http
POST /users/1/analytics/tasks
```

Пример ответа:

```json
{
  "task_id": "7df81e7b-5a3d-438a-97d8-25c087bb7d74",
  "status": "started"
}
```

### Проверить статус задачи

```http
GET /tasks/0f3a9b3c-2c61-4db5-a09d-8f7c4e73d7f6
```

Пока задача выполняется:

```json
{
  "task_id": "0f3a9b3c-2c61-4db5-a09d-8f7c4e73d7f6",
  "status": "STARTED",
  "ready": false
}
```

Когда задача завершилась:

```json
{
  "task_id": "0f3a9b3c-2c61-4db5-a09d-8f7c4e73d7f6",
  "status": "SUCCESS",
  "ready": true,
  "result": {
    "x": {
      "minimum": 10.0,
      "maximum": 10.0,
      "count": 1,
      "sum": 10.0,
      "median": 10.0
    },
    "y": {
      "minimum": 20.0,
      "maximum": 20.0,
      "count": 1,
      "sum": 20.0,
      "median": 20.0
    },
    "z": {
      "minimum": 30.0,
      "maximum": 30.0,
      "count": 1,
      "sum": 30.0,
      "median": 30.0
    }
  }
}
```

## Структура проекта

```text
app/
  api/
    devices.py        # HTTP-роуты для устройств
    stats.py          # HTTP-роуты для статистики и запуска аналитики устройства
    tasks.py          # HTTP-роут для проверки Celery task_id
    users.py          # HTTP-роуты для пользователей и запуска аналитики пользователя

  core/
    celery_app.py     # настройка Celery, Redis broker/result backend
    database.py       # engine, Base, SessionLocal, init_db, DATABASE_URL

  db/
    base.py           # импорт моделей для регистрации в SQLAlchemy metadata
    session.py        # совместимый экспорт SessionLocal/get_db
    models/
      device.py       # ORM-модель Device
      statistic.py    # ORM-модель Statistic
      user.py         # ORM-модель User

  schemas/
    device.py         # Pydantic-схемы устройств
    statistic.py      # Pydantic-схемы статистики
    user.py           # Pydantic-схемы пользователей

  services/
    analytics.py      # аналитика по устройству
    user_analytics.py # аналитика по пользователю
    metrics.py        # общий расчет метрик
    devices.py        # бизнес-логика устройств
    statistics.py     # бизнес-логика статистики
    users.py          # бизнес-логика пользователей

  tasks/
    analytics.py      # Celery-задачи для фоновой аналитики

  main.py             # создание FastAPI-приложения и подключение роутеров
```

## Настройки окружения

Приложение использует следующие переменные окружения:

```text
DATABASE_URL
CELERY_BROKER_URL
CELERY_RESULT_BACKEND
```

Значения по умолчанию:

```text
DATABASE_URL=sqlite:///./data/app.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

В Docker Compose для API и worker используются адреса Redis внутри compose-сети:

```text
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## Запуск через Docker Compose

Основной способ запуска проекта:

```powershell
docker compose up --build
```

Будут запущены три сервиса:

- `api` - FastAPI-приложение на порту `8000`;
- `worker` - Celery worker для фоновых задач;
- `redis` - брокер сообщений и result backend.

API будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Проверка:

```powershell
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

Остановить контейнеры:

```powershell
docker compose down
```

Остановить контейнеры и удалить локальную SQLite-базу:

```powershell
docker compose down
Remove-Item -Recurse -Force .\data
```

## Локальный запуск без Docker

Создать и активировать виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

Для полноценной работы Celery локально нужен запущенный Redis.

Запустить API:

```powershell
uvicorn app.main:app --reload
```

Запустить Celery worker в отдельном терминале:

```powershell
celery -A app.core.celery_app.celery_app worker --loglevel=info
```

## Ограничения текущей реализации

- SQLite удобен для демонстрации, но для реального параллельного API + Celery worker лучше использовать PostgreSQL.
- Результаты Celery-задач хранятся в Redis result backend, а не в отдельной таблице БД.
- Celery-задачи синхронные. Это нормально для текущей архитектуры, потому что SQLAlchemy и сервисный слой тоже синхронные.
- Миграции БД не настроены: таблицы создаются через `Base.metadata.create_all()`.
