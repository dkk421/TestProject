# TestProject

Backend-сервис для сбора статистики с устройств и расчета аналитики по этим данным.

Проект написан на **FastAPI**, использует **SQLAlchemy** для работы с базой данных и **SQLite** как простое файловое хранилище. Приложение можно запускать локально или через Docker Compose.

## Что умеет сервис

- Создавать пользователей.
- Создавать устройства.
- Назначать устройство пользователю.
- Принимать статистику устройства по трем показателям: `x`, `y`, `z`.
- Считать аналитику по одному устройству.
- Считать аналитику по всем устройствам пользователя.

Пример статистики:

```json
{
  "x": 1.0,
  "y": 2.0,
  "z": 3.0
}
```

Для каждого показателя сервис считает:

- `minimum`
- `maximum`
- `count`
- `sum`
- `median`

## API

Основные эндпоинты:

```text
GET  /health

POST /users
GET  /users/{user_id}/analytics

POST /devices
POST /devices/{device_id}/assign/{user_id}

POST /devices/{device_id}/stats
GET  /devices/{device_id}/analytics
```

Создание пользователя:

```json
POST /users

{
  "username": "alice"
}
```

Создание устройства:

```json
POST /devices

{
  "identifier": "device-001"
}
```

Добавление статистики:

```json
POST /devices/1/stats

{
  "x": 10,
  "y": 20,
  "z": 30
}
```

## Структура проекта

```text
app/
  api/
    devices.py        # HTTP-роуты для устройств
    stats.py          # HTTP-роуты для статистики и аналитики устройств
    users.py          # HTTP-роуты для пользователей

  core/
    database.py       # engine, Base, SessionLocal, init_db, DATABASE_URL

  db/
    base.py           # импорт всех моделей для регистрации в SQLAlchemy metadata
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
    devices.py        # логика устройств
    statistics.py     # логика статистики
    users.py          # логика пользователей

  main.py             # создание FastAPI-приложения и подключение роутеров
```

## Архитектура

Проект разделен на несколько слоев:

```text
HTTP API -> services -> db/models -> database
          -> schemas
```

### `api`

Слой `api` отвечает только за HTTP-интерфейс: принимает запросы, получает `db`-сессию через dependency injection и вызывает сервисы.

Роутеры не создают ORM-объекты напрямую и не делают `db.add()` / `db.commit()`. Это сделано специально, чтобы HTTP-слой не смешивался с бизнес-логикой.

### `services`

В сервисах находится основная логика приложения:

- создание пользователей;
- создание устройств;
- назначение устройств пользователям;
- создание статистики;
- проверка существования сущностей;
- расчет аналитики.

Такой подход упрощает тестирование и развитие проекта: если позже изменится API или появятся фоновые задачи, бизнес-логику не придется вынимать из роутеров.

### `schemas`

Pydantic-схемы описывают входные и выходные данные API.

Например, пользователь создается через JSON body:

```json
{
  "username": "alice"
}
```

Это лучше, чем передавать `username` через query-параметр, потому что `POST /users` создает ресурс, а тело запроса естественно описывает создаваемую сущность.

### `db/models`

ORM-модели описывают таблицы базы данных:

- `User`
- `Device`
- `Statistic`

Pydantic-схемы и ORM-модели разделены намеренно: схемы описывают API-контракт, а модели описывают структуру хранения.

### `db/base.py`

Файл `app/db/base.py` импортирует все модели в одном месте.

Это нужно SQLAlchemy: перед вызовом `Base.metadata.create_all(...)` все модели должны быть импортированы, иначе SQLAlchemy не узнает о таблицах.

Именно поэтому в `init_db()` есть импорт:

```python
import app.db.base
```

Он выглядит необычно, но здесь он нужен для регистрации моделей.

### `core/database.py`

В этом модуле находится настройка подключения к БД:

- `DATABASE_URL`
- `engine`
- `SessionLocal`
- `Base`
- `init_db()`
- `get_db()`

По умолчанию используется:

```text
sqlite:///./data/app.db
```

Путь можно переопределить через переменную окружения `DATABASE_URL`.

## Почему SQLite

SQLite выбран как простой вариант для тестового:

- не требует отдельного сервера БД;
- хранит данные в одном файле;
- легко запускается локально и в Docker;
- подходит для демонстрации REST API, слоев приложения и работы SQLAlchemy.

В Docker база хранится в файле:

```text
/app/data/app.db
```

А в `docker-compose.yml` настроен volume:

```yaml
volumes:
  - ./data:/app/data
```

Поэтому файл базы сохраняется на компьютере в папке:

```text
./data/app.db
```

Данные не пропадут после остановки или пересоздания контейнера, пока не удалить папку `data`.

## Важное ограничение

Сейчас аналитика считается синхронно во время HTTP-запроса.

То есть эндпоинты:

```text
GET /devices/{device_id}/analytics
GET /users/{user_id}/analytics
```

сразу выполняют расчет и возвращают результат.

Если по требованиям нужна асинхронная аналитика через Celery, проект нужно дополнить:


## Запуск локально

Создать и активировать виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

Запустить сервер:

```powershell
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
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

## Запуск через Docker Compose

Собрать и запустить контейнер:

```powershell
docker compose up --build
```

После запуска API будет доступно:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Остановить контейнер:

```powershell
docker compose down
```

Остановить контейнер и удалить сохраненную SQLite-базу:

```powershell
docker compose down
Remove-Item -Recurse -Force .\data
```
