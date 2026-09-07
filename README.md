# Rulebook Conflict Detector & RAG Engine

A high-accuracy Question-Answering service over university academic regulations. Designed to cite exact passages, admit when regulations are silent, and explicitly flag contradictory rules.

---

## 📌 Project Overview

University rulebooks often contain conflicting clauses, hidden waivers, and ambiguous thresholds scattered across hundreds of pages. Standard LLMs hallucinate plausible answers rather than pointing out rule contradictions.

This service reads academic regulations, computes vector similarity over structured document chunks, and evaluates questions using **Gemini 3.7/3.8 Flash**. It strictly categorizes every response into one of three distinct statuses:
1. **`answered`**: Returns the precise answer along with cited section references and similarity scores.
2. **`not_covered`**: Flags when the rulebook corpus is silent on the asked question.
3. **`conflict`**: Detects and highlights mutually exclusive or contradictory clauses within the rulebook.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, FastAPI, Uvicorn
* **LLM & Embeddings:** Gemini API (`gemini-3.7-flash` / `gemini-3.8-flash`)
* **Vector Store:** In-memory NumPy Cosine Similarity engine (No external database required)
* **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS

---

## 📂 Repository Structure

```text
.
├── main.py              # FastAPI server, RAG pipeline, and Gemini integration
├── requirements.txt     # Python dependencies
├── rulebook.md          # 6,000+ word synthetic academic regulations corpus
├── test_questions.json  # Evaluation dataset (25 unanswerable + 3 planted conflicts)
├── static/
│   └── index.html       # Single-page interface displaying answers + passage citations
└── README.md            # Setup and execution documentation