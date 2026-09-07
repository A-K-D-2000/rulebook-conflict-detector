import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
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
    return FileResponse("templates/index.html")

@app.get("/rulebook-content")
async def get_rulebook_content():
    """Serves the full text of rulebook.md to the frontend reader."""
    if not os.path.exists("rulebook.md"):
        return JSONResponse({"content": "rulebook.md not found."}, status_code=404)
    with open("rulebook.md", "r", encoding="utf-8", errors="ignore") as f:
        return {"content": f.read()}

@app.post("/ask")
async def ask_endpoint(payload: QueryRequest):
    try:
        result = query_rulebook(payload.query)
        return result
    except Exception as e:
        return {
            "query": payload.query,
            "status": "not_covered",
            "answer": f"Error processing query: {str(e)}",
            "citations": [],
            "conflict_details": None,
            "passages": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)