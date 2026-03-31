# MCP Knowledge Server

Production-grade MCP-сервер для LLM-агентов, предоставляющий безопасные typed tools для поиска знаний, чтения документов, сборки проектного контекста и выполнения ограниченных действий внутри системы.

## О проекте

`MCP Knowledge Server` — это backend-компонент для agentic / LLM-систем, который выступает прослойкой между моделью и внутренними данными/действиями.  
Сервер предоставляет инструменты через MCP-подобный JSON-RPC transport, контролирует доступ по API key и scope-ам, ведет аудит операций и поддерживает наблюдаемость через метрики и request tracing.


---

## Цели проекта

Проект разрабатывался как **production-oriented MCP backend**, который должен демонстрировать навыки, ожидаемые от LLM Engineer / AI Backend Engineer:

- проектирование tool interfaces для LLM-агентов;
- реализация MCP-oriented transport layer;
- schema-first подход к tool contracts;
- safe tool execution;
- retrieval-aware backend design;
- контекстная агрегация для моделей;
- auth, scopes и auditability;
- observability и production readiness;
- тестирование tool contracts и integration flows.

---

## Ключевые возможности

### Knowledge / Retrieval
- поиск документов через PostgreSQL Full-Text Search;
- ранжирование результатов через `ts_rank`;
- фильтрация по проекту;
- получение документа по идентификатору;
- сборка структурированного project context.

### Actions
- создание задач;
- создание заметок;
- idempotency для `create_note`.

### Security
- аутентификация через `x-api-key`;
- tool-level authorization через scopes;
- request context с `request_id`, `client_id`, `client_name`.

### Observability
- Prometheus metrics;
- HTTP request metrics;
- MCP tool metrics;
- request logging;
- audit logs для mutation-операций.

### Quality
- Alembic migrations;
- unit / integration / contract tests;
- typed DTO и отдельный service layer.

---

## Архитектура

Проект реализован как **modular monolith** с четким разделением слоев.

### Слои системы

#### 1. Transport layer
Отвечает за входные протоколы и адаптацию запросов:
- HTTP routers;
- MCP endpoint;
- middleware;
- зависимости для auth / request context.

#### 2. MCP layer
Инкапсулирует tool execution pipeline:
- registry tools;
- dispatcher;
- input/output schemas;
- permission checks;
- result envelope.

#### 3. Application layer
Содержит use cases и бизнес-логику:
- document service;
- project service;
- task services;
- note service.

#### 4. Domain layer
Содержит сущности, enum-ы и модели предметной области:
- projects;
- documents;
- document_chunks;
- tasks;
- notes;
- api_clients;
- audit_logs.

#### 5. Infrastructure layer
Содержит технические адаптеры:
- SQLAlchemy repositories;
- DB session management;
- auth service;
- metrics;
- search implementation.

---

## Структура проекта

```text
app/
├── application/
│   ├── dto/
│   ├── interfaces/
│   └── services/
├── core/
│   ├── config.py
│   ├── exceptions.py
│   ├── logging.py
│   ├── request_context.py
│   └── telemetry.py
├── domain/
│   ├── enums/
│   └── models/
├── infrastructure/
│   ├── auth/
│   ├── db/
│   ├── observability/
│   └── repositories/
├── tests/
│   ├── contract/
│   ├── integration/
│   └── unit/
└── transport/
    ├── http/
    │   ├── middleware.py
    │   ├── dependencies.py
    │   └── routers/
    └── mcp/
        ├── auth.py
        ├── context.py
        ├── dispatcher.py
        ├── registry.py
        ├── result.py
        ├── schemas.py
        └── tools/
```

## Технологический стек
### Backend
- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic

### Data / Storage
- PostgreSQL
- Redis

### Search
- PostgreSQL Full-Text Search
- tsvector
- ts_rank
- GIN index

### Testing / Quality
- pytest
- pytest-asyncio
- httpx
- Ruff
- MyPy

### Observability
- prometheus-client

### Infra
- Docker Compose

---

## MCP tools

Сервер предоставляет следующие инструменты.

### `search_knowledge`

Ищет документы по текстовому запросу с использованием PostgreSQL FTS.

Scope: `knowledge:read`

### `get_document`

Возвращает полный документ по идентификатору.

Scope: `knowledge:read`

### `build_project_context`

Собирает структурированный контекст по проекту:

- метаданные проекта;
- последние документы;
- открытые задачи.

Scope: `projects:read`

### `search_tasks`

Ищет задачи по тексту, проекту и/или исполнителю.

Scope: `tasks:read`

### `create_task`

Создает задачу внутри проекта.

Scope: `tasks:write`

### `create_note`

Создает заметку внутри проекта.

Scope: `notes:write`

---

## Модель безопасности
### Аутентификация

Для доступа к MCP endpoint используется заголовок:

`x-api-key`

Ключ сопоставляется с сущностью `api_client` в базе данных.

### Авторизация

Каждому клиенту назначается набор scope-ов, например:

- `knowledge:read`
- `projects:read`
- `tasks:read`
- `tasks:write`
- `notes:write`

Каждый `tool` требует конкретный scope, и вызов без нужного разрешения будет отклонен.

### Request Context

Для каждого запроса формируется `request context`:

- `request_id`
- `client_id`
- `client_name`
- `scopes`

Этот контекст используется при:

- проверке прав;
- логировании;
- аудите mutation-операций.

---

## Аудит и наблюдаемость
### Audit

Для `write-tools` создаются записи в `audit_logs`, содержащие:

- client id;
- request id;
- tool name;
- action type;
- входной payload;
- outcome.
### Метрики

Экспортируются:

- http_requests_total
- http_request_duration_seconds
- mcp_tool_calls_total
- mcp_tool_duration_seconds
### Логи

На уровне приложения логируются:

- HTTP requests;
- tool execution;
- ошибки валидации и выполнения.

---

## Схема работы


- Пользователь отправляет запрос в host-приложение.
- Host передает агенту список доступных tools.
- Модель принимает решение вызвать нужный tool.
- Host отправляет JSON-RPC запрос на MCP server.

- MCP server:
  - аутентифицирует клиента;
  - проверяет scope;
  - валидирует input schema;
  - вызывает service layer;
  - получает результат;
  - возвращает typed output.
- Host передает результат обратно модели.
- Модель строит итоговый ответ пользователю.

---

## Локальный запуск
1. Создать .env

Скопируйте пример:

```
cp .env.example .env
```

2. Поднять инфраструктуру
```
docker compose up -d
```
3. Установить зависимости
```
pip install -e ".[dev]"
```
4. Применить миграции
```
alembic upgrade head
```
5. Заполнить базу тестовыми данными
```
python -m app.infrastructure.db.seed
```
6. Запустить сервер
```
uvicorn app.main:app --reload
```

---

## Полезные endpoint-ы
#### Health
```
GET /api/v1/health/live
GET /api/v1/health/ready
```
#### Metrics 
```
GET /api/v1/metrics
```
#### MCP
```
POST /api/v1/mcp
```

---

## Пример заголовков для MCP-запроса
```
Content-Type: application/json
x-api-key: dev-secret-key
x-request-id: test-request-001
```

---

## Примеры MCP-запросов
### Получить список tools
```
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```
### Поиск знаний
```
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_knowledge",
    "arguments": {
      "query": "retrieval architecture"
    }
  }
}
```
### Сборка project context
```
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "build_project_context",
    "arguments": {
      "slug": "aurora"
    }
  }
}
```
### Создание задачи
```
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "create_task",
    "arguments": {
      "project_id": "PROJECT_UUID",
      "title": "Add request logging",
      "description": "Persist request metadata for MCP tool calls",
      "priority": "high",
      "assignee": "zach",
      "created_by": "platform-team"
    }
  }
}
```

---

## Тестирование
### Запустить все тесты
```
pytest
```
### По слоям
```
pytest app/tests/unit
pytest app/tests/integration
pytest app/tests/contract
```

## Что покрыто тестами
### Unit
- API key auth;
- scope checks.
### Integration
- health endpoints;
- MCP read-tools;
- MCP write-tools;
- idempotency для create_note.
### Contract
- shape ответа tools/list;
- структура MCP payload.

---


## Ограничения текущей версии

На данный момент проект намеренно не включает:

- OAuth 2.1 / OIDC;
- полноценный remote MCP authorization flow;
- pgvector и semantic search;
- chunk-level retrieval в tool response;
- reranking;
- OpenTelemetry tracing;
- rate limiting;
- JSONB audit payload;
- background indexing pipeline.

---

## Всем спасибо!