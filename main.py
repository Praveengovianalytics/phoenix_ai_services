
import nest_asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from threading import Thread
import uvicorn

from phoenix_ai_services.registry import EndpointRegistry
from phoenix_ai_services.rag_controller import summarize_with_config
from phoenix_ai_services.tool_controller import run_tool

nest_asyncio.apply()
app = FastAPI(title="Phoenix AI Services")

registry = EndpointRegistry()

class RAGConfig(BaseModel):
    api_key: str
    embedding_model: str
    chat_model: str
    index_path: str

@app.post("/rag/endpoints/{name}")
def add_rag_endpoint(name: str, config: RAGConfig):
    registry.add(name, {"type": "rag", **config.dict()})
    return {"message": f"✅ RAG endpoint '{name}' registered."}

@app.put("/rag/endpoints/{name}")
def update_rag_endpoint(name: str, config: RAGConfig):
    registry.update(name, {"type": "rag", **config.dict()})
    return {"message": f"🔁 RAG endpoint '{name}' updated."}

@app.delete("/rag/endpoints/{name}")
def delete_rag_endpoint(name: str):
    registry.delete(name)
    return {"message": f"❌ RAG endpoint '{name}' deleted."}

@app.get("/rag/query/{name}")
def query_rag_endpoint(name: str, question: str = Query(...), mode: str = Query("standard"), top_k: int = Query(5)):
    config = registry.get(name)
    if not config or config.get("type") != "rag":
        raise HTTPException(status_code=404, detail=f"RAG endpoint '{name}' not found.")
    return summarize_with_config(config, question, mode, top_k)

@app.get("/tool/{tool_name}")
def tool_runner(tool_name: str, input_data: str = Query("")):
    return run_tool(tool_name, input_data)

@app.get("/registry")
def list_registry():
    return registry.list_all()

mcp = FastApiMCP(app, name="Phoenix AI Services", description="Unified RAG and Tool Service")
mcp.mount()

def run_server():
    print("🚀 Starting Phoenix AI Services at http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)

Thread(target=run_server).start()
