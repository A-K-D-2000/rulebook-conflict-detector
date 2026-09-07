import os
import json
import math
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

INDEX_FILE = "sections_index.json"
if not os.path.exists(INDEX_FILE):
    raise FileNotFoundError(f"{INDEX_FILE} not found. Run ingest.py first!")

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    SECTIONS_DATABASE = json.load(f)

def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def retrieve_top_sections(query, top_k=5):
    # Retry embedding call if needed
    for attempt in range(4):
        try:
            res = client.models.embed_content(
                model="gemini-embedding-001",
                contents=query
            )
            query_vector = res.embeddings[0].values
            break
        except (ServerError, APIError) as e:
            if attempt < 3:
                time.sleep(3 * (attempt + 1))
            else:
                raise e

    scored_sections = []
    for sec in SECTIONS_DATABASE:
        score = cosine_similarity(query_vector, sec["embedding"])
        scored_sections.append({
            "id": sec["id"],
            "title": sec["title"],
            "chapter": sec["chapter"],
            "text": sec["text"],
            "score": round(score, 4)
        })

    scored_sections.sort(key=lambda x: x["score"], reverse=True)
    return scored_sections[:top_k]

SYSTEM_PROMPT = """
You are the official Academic Registrar QA Engine. Your duty is to analyze institutional rulebook passages and answer questions with absolute precision, strict citation, and uncompromising honesty.

You must categorize your response into exactly one of three statuses:
1. "answered": The retrieved passages explicitly and unambiguously address the query.
   - You must cite the exact Section ID(s) (e.g., Section 3.1) and quote key supporting phrases.
2. "not_covered": The retrieved passages DO NOT explicitly answer the user's specific scenario or question.
   - State clearly that the university rulebook is silent or does not specify rules for this scenario.
   - Do NOT invent rules, assume unstated policies, or hallucinate.
3. "conflict": The retrieved passages contain contradictory rules across different sections.
   - Identify the conflicting sections.
   - Explicitly state what each section claims and describe the exact nature of the contradiction.

Return your response strictly in the following JSON format:
{
  "status": "answered" | "not_covered" | "conflict",
  "answer": "Your comprehensive answer, explanation of silence, or detailed conflict breakdown.",
  "citations": ["Section X.Y", "Section A.B"],
  "conflict_details": {
      "conflicting_sections": ["Section X.Y", "Section A.B"],
      "nature_of_conflict": "Summary of contradiction"
  }
}
"""

def query_rulebook(query: str):
    top_passages = retrieve_top_sections(query, top_k=5)

    context_blocks = []
    for p in top_passages:
        context_blocks.append(f"[{p['id']} - {p['title']} (Score: {p['score']})]\n{p['text']}")
    context_text = "\n\n---\n\n".join(context_blocks)

    user_message = f"""USER QUERY:
{query}

RETRIEVED RULEBOOK PASSAGES:
{context_text}
"""

    response = None
    # Retry on temporary Google server overload (503/429)
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            break
        except (ServerError, APIError) as e:
            if attempt < 3:
                print(f"    (Google server busy, retrying in {(attempt + 1) * 3}s...)")
                time.sleep((attempt + 1) * 3)
            else:
                raise e

    try:
        parsed_result = json.loads(response.text)
    except Exception:
        parsed_result = {
            "status": "answered",
            "answer": response.text if response else "Error parsing response.",
            "citations": [],
            "conflict_details": None
        }

    return {
        "query": query,
        "status": parsed_result.get("status", "answered"),
        "answer": parsed_result.get("answer", ""),
        "citations": parsed_result.get("citations", []),
        "conflict_details": parsed_result.get("conflict_details", None),
        "passages": [
            {
                "id": p["id"],
                "title": p["title"],
                "score": p["score"],
                "text": p["text"]
            }
            for p in top_passages
        ]
    }

if __name__ == "__main__":
    test_q = "What attendance percentage is needed for exams?"
    print(f"Testing with query: '{test_q}'\n")
    result = query_rulebook(test_q)
    print(f"Status: {result['status']}")
    print(f"Answer: {result['answer']}")
    print(f"Passages Retrieved: {len(result['passages'])}")