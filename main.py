from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rag_engine import query_rulebook

app = FastAPI(
    title="The Rulebook That Argues With Itself",
    description="RAG service for institutional rulebooks with conflict and silence detection."
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def serve_home():
    """Serves the side-by-side verification interface directly."""
    return FileResponse("templates/index.html")

@app.post("/ask")
async def ask_endpoint(payload: QueryRequest):
    """
    Main RAG API endpoint.
    Accepts: { "query": "string" }
    Returns: status, answer, citations, conflict_details, passages with similarity scores.
    """
    result = query_ruleboo