import logging
import os
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from phoenix_ai_services.elk_controller import query_elk
from phoenix_ai_services.rag_controller import summarize_with_config
from phoenix_ai_services.registry import EndpointRegistry
from phoenix_ai_services.tool_controller import run_tool

logger = logging.getLogger(__name__)

APP_TITLE = os.getenv("PHOENIX_APP_TITLE", "Phoenix AI Services - RAG Framework")
MCP_MOUNT_PATH = os.getenv("PHOENIX_MCP_MOUNT_PATH", "/mcp")
SERVER_HOST = os.getenv("PHOENIX_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PHOENIX_PORT", "8003"))
LOG_LEVEL = os.getenv("PHOENIX_LOG_LEVEL", "info")
ELK_BASE_URL = os.getenv("PHOENIX_ELK_BASE_URL", "")
ELK_INDEX = os.getenv("PHOENIX_ELK_INDEX", "")
ELK_API_KEY = os.getenv("PHOENIX_ELK_API_KEY")


# === Pydantic Schemas ===
class RAGConfig(BaseModel):
    api_key: str
    embedding_model: str
    chat_model: str
    index_path: str


def create_app() -> FastAPI:
    app = FastAPI(title=APP_TITLE)
    registry = EndpointRegistry()

    # === Dynamic Endpoint Manager APIs ===
    @app.post("/rag/endpoints/{name}")
    def add_rag_endpoint(name: str, config: RAGConfig):
        registry.add(name, config.model_dump())
        return {"message": f"✅ Endpoint '{name}' registered."}

    @app.put("/rag/endpoints/{name}")
    def update_rag_endpoint(name: str, config: RAGConfig):
        registry.update(name, config.model_dump())
        return {"message": f"🔁 Endpoint '{name}' updated."}

    @app.delete("/rag/endpoints/{name}")
    def delete_rag_endpoint(name: str):
        registry.delete(name)
        return {"message": f"❌ Endpoint '{name}' deleted."}

    @app.get("/rag/endpoints")
    def list_rag_endpoints() -> Dict[str, Dict]:
        return registry.list_all()

    @app.get("/registry")
    def registry_alias() -> Dict[str, Dict]:
        return registry.list_all()

    # === Universal RAG Query Handler ===
    @app.get("/rag/query/{name}")
    def query_rag_endpoint(
        name: str,
        question: str = Query(...),
        mode: str = Query("standard"),
        top_k: int = Query(5),
    ):
        config = registry.get(name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Endpoint '{name}' not found.")
        return summarize_with_config(config, question, mode, top_k)

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}

    @app.get("/elk/query")
    def elk_query(
        q: str = Query(..., description="ELK query string"),
        size: int = Query(10, ge=1, le=1000),
    ):
        if not ELK_BASE_URL or not ELK_INDEX:
            raise HTTPException(status_code=500, detail="ELK configuration is not set.")
        try:
            return query_elk(
                base_url=ELK_BASE_URL,
                index=ELK_INDEX,
                query=q,
                size=size,
                api_key=ELK_API_KEY,
            )
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/test/run")
    def test_run():
        results = {}

        # Test RAG if "default_rag" is registered
        try:
            config = registry.get("default_rag")
            if config and config.get("type") == "rag":
                rag_response = summarize_with_config(
                    config=config,
                    question="What is the leave policy?",
                    mode="standard",
                    top_k=3,
                )
                results["RAG_Test"] = rag_response
            else:
                results["RAG_Test"] = "⚠️ 'default_rag' not registered"
        except Exception as e:
            results["RAG_Test"] = f"❌ Failed: {str(e)}"

        # Test tools
        try:
            results["Tool_Calculator"] = run_tool("calculator", "2 + 3 * 4")
            results["Tool_SystemTime"] = run_tool("system_time", "")
            results["Tool_Python"] = run_tool("python", "round(3.14159, 2)")
        except Exception as e:
            results["Tools"] = f"❌ Tool test failed: {str(e)}"

        return results

    # === MCP Server ===
    mcp = FastMCP(
        name="Phoenix AI Services",
        instructions="Dynamic RAG inference and utility tools via MCP.",
    )

    @mcp.tool(description="List registered RAG endpoints.")
    def mcp_list_rag_endpoints() -> Dict[str, Dict]:
        return registry.list_all()

    @mcp.tool(description="Run a RAG query against a registered endpoint.")
    def mcp_query_rag(name: str, question: str, mode: str = "standard", top_k: int = 5):
        config = registry.get(name)
        if not config:
            raise ValueError(f"Endpoint '{name}' not found.")
        return summarize_with_config(config, question, mode, top_k)

    @mcp.tool(description="Run a tool by name (calculator, system_time, python).")
    def mcp_run_tool(tool_name: str, input_data: str = ""):
        try:
            return run_tool(tool_name, input_data)
        except HTTPException as exc:
            raise ValueError(exc.detail) from exc

    @mcp.tool(description="Query ELK via the configured Elasticsearch API.")
    def mcp_query_elk(query: str, size: int = 10):
        if not ELK_BASE_URL or not ELK_INDEX:
            raise ValueError("ELK configuration is not set.")
        return query_elk(
            base_url=ELK_BASE_URL,
            index=ELK_INDEX,
            query=query,
            size=size,
            api_key=ELK_API_KEY,
        )

    app.mount(MCP_MOUNT_PATH, mcp.sse_app(MCP_MOUNT_PATH))

    return app


app = create_app()


if __name__ == "__main__":
    logger.info(
        "🚀 Starting Phoenix AI Services at http://%s:%s", SERVER_HOST, SERVER_PORT
    )
    uvicorn.run(
        "phoenix_ai_services.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=LOG_LEVEL,
    )
