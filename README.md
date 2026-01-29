
# 🔥 Phoenix AI Services is MCP server

Unified agentic framework to run dynamic RAG APIs and utility tools like calculator, date, and   python evaluator.

# phoenix_ai_services

[![PyPI - Version](https://img.shields.io/pypi/v/phoenix-ai-services.svg)](https://pypi.org/project/phoenix-ai-services/)
[![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python Version](https://img.shields.io/pypi/pyversions/phoenix-ai-services.svg)](https://pypi.org/project/phoenix-ai-services/)
[![License](https://img.shields.io/pypi/l/phoenix-ai-services)](https://github.com/Praveengovianalytics/phoenix_ai_services/LICENSE)

---

> `phoenix_ai_services` is a modular Python package for managing RAG endpoints, tool-based APIs, and plug-and-play AI utilities using FastAPI & Poetry. It supports RESTful control for registering, updating, and deleting endpoints for RAG, tools, and more.


## 🔧 Setup

```bash
poetry install
poetry run python phoenix_ai_services/main.py
```

## 🧩 MCP Server (Latest Standard)

Phoenix AI Services now exposes an MCP-compatible SSE server mounted at `/mcp` by default.

- **SSE endpoint:** `GET /mcp/sse`
- **Message endpoint:** `POST /mcp/messages/`

You can change the mount path via `PHOENIX_MCP_MOUNT_PATH`.

### Example: Run with Uvicorn (Production)

```bash
PHOENIX_HOST=0.0.0.0 PHOENIX_PORT=8003 uvicorn phoenix_ai_services.main:app
```

## 🚀 API Endpoints

### RAG
- `POST /rag/endpoints/{name}` – Register RAG
- `PUT /rag/endpoints/{name}` – Update RAG
- `DELETE /rag/endpoints/{name}` – Remove RAG
- `GET /rag/query/{name}` – Ask RAG agent

### Tools
- `GET /tool/calculator?input_data=2+3*4`
- `GET /tool/system_time`
- `GET /tool/python?input_data=round(3.14159, 2)`

### Admin
- `GET /rag/endpoints` – View all registered endpoints

### Health
- `GET /healthz` – Liveness check
- `GET /elk/query?q=message:error` – Query ELK with a query string

## ⚙️ Production Configuration

Environment variables:

- `PHOENIX_HOST` (default: `0.0.0.0`)
- `PHOENIX_PORT` (default: `8003`)
- `PHOENIX_LOG_LEVEL` (default: `info`)
- `PHOENIX_MCP_MOUNT_PATH` (default: `/mcp`)
- `PHOENIX_ELK_BASE_URL` (example: `https://your-elasticsearch:9200`)
- `PHOENIX_ELK_INDEX` (example: `logs-*`)
- `PHOENIX_ELK_API_KEY` (optional, API key for Elasticsearch)

## 🔍 ELK MCP Integration Examples

### Configure ELK connection

```bash
export PHOENIX_ELK_BASE_URL="https://your-elasticsearch:9200"
export PHOENIX_ELK_INDEX="logs-*"
export PHOENIX_ELK_API_KEY="your_api_key"
```

### REST query example

```bash
curl "http://localhost:8003/elk/query?q=service:api%20AND%20level:error&size=5"
```

### MCP tool example (client-side)

Use your MCP client to call the `mcp_query_elk` tool:

```
tool: mcp_query_elk
args:
  query: "service:api AND level:error"
  size: 5
```

## 🧠 Powered by Phoenix Agentic AI Framework
