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
    return FileResponse("templates/index.html")

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