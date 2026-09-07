# The Rulebook That Argues With Itself

A specialized Retrieval-Augmented Generation (RAG) system built with FastAPI and Google Gemini that indexes institutional university regulations, retrieves relevant clauses with visible similarity scores, detects internal policy contradictions across chapters, and refuses to hallucinate when the corpus is silent.

---

## Problem Overview

University regulations are notoriously prone to internal friction:
- One clause mandates a 75% attendance threshold to sit for exams.
- Another clause allows medical exemptions down to 50%.
- A separate appeals committee claims exclusive power to condone attendance down to 60%.

Standard AI chatbots give misleading, overconfident answers by latching onto whichever passage they find first. This system is designed to read all relevant clauses simultaneously, providing:
1. **Clause-Level Citations**: Explicit references (e.g., Section 3.1) and quotes.
2. **Side-by-Side Scoring**: Direct, visible cosine similarity scores (never hidden behind clicks).
3. **Strict 3-State Classification**:
   - `ANSWERED`: Unambiguous answers supported by cited text.
   - `NOT COVERED`: Explicit refusal to hallucinate when the corpus is silent.
   - `CONFLICT`: Automatic detection and breakdown of internal policy contradictions.

---

## Corpus & Planted Contradictions

The source policy manual (`rulebook.md`) contains over 6,000 words across 12 chapters, structured into 71 discrete sections. Exactly three policy contradictions were planted for evaluation:

| # | Conflict Area | Conflicting Sections | Nature of Contradiction |
|---|---|---|---|
| 1 | Exam Attendance Threshold | Section 3.1 vs Section 5.4 vs Section 12.2 | Sec 3.1 mandates a strict 75% threshold with no waivers; Sec 5.4 lowers it to 50% for medical leave; Sec 12.2 gives the Academic Committee sole authority to waive attendance down to 60% and bans waivers below 60%. |
| 2 | Merit Scholarship Retention | Section 7.2 vs Section 9.1 | Sec 7.2 requires an 8.50 CGPA with zero exceptions across all cohorts; Sec 9.1 permits varsity student-athletes to retain merit scholarships at an 8.00 CGPA. |
| 3 | Grade Review Deadlines | Section 4.3 vs Section 11.1 | Sec 4.3 enforces a strict deadline of 7 calendar days to apply for grade re-evaluation; Sec 11.1 allows up to 14 working days to submit re-checking petitions. |

---

## Benchmark & Evaluation Results

The system was evaluated against `test_questions.json` using an automated testing pipeline (`evaluate.py`):
- **25 Hard Unanswerable Edge Cases**: Plausible student scenarios completely absent from the text (e.g., missing exams for a sibling's wedding, charging e-scooters in dorms, pet fish, reality TV leaves).
- **3 Planted Contradiction Queries**: Multi-clause policy questions designed to trigger conflicting sections.

### Summary Metrics

- **Unanswerable Questions Refusal Accuracy**: 21/25 (84.0%)
- **Contradiction Detection Accuracy**: 3/3 (100.0%)

### Key Takeaways
- **Conflict Detection (100%)**: Successfully flagged all internal contradictions, identified conflicting section numbers, and detailed the conflict.
- **Hallucination Suppression (84%)**: Correctly identified silence on 21 of 25 deceptive edge cases without fabricating university policies.

---

## System Architecture

- **Ingestion & Parser (`ingest.py`)**: Slices raw markdown into 71 structured section objects with metadata (chapter, section ID, title, body).
- **Vector Retrieval (`rag_engine.py`)**: Generates vector representations using `gemini-embedding-001` and performs in-memory pure-Python cosine similarity matching.
- **Reasoning Engine (`rag_engine.py`)**: Uses `gemini-3.5-flash-lite` with structured JSON schema output and automated retry logic for API resilience.
- **Web Service (`main.py`)**: FastAPI backend with `POST /ask` and a side-by-side verification interface (`templates/index.html`).

---

## Quickstart & Setup

### 1. Clone & Install Dependencies
```powershell
git clone <your-repo-url>
cd rulebook-conflict-detector
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```ini
GEMINI_API_KEY=your_free_google_gemini_api_key
```

### 3. Ingest & Index Corpus
```powershell
python ingest.py
```

### 4. Run the Web Application
```powershell
python main.py
```
Open `http://127.0.0.1:8000` in your browser to interact with the side-by-side UI.

### 5. Run the Evaluation Suite
```powershell
python evaluate.py
```
Outputs benchmark progress and exports full evaluation logs to `benchmark_results.json`.

---

## Project Structure

```text
rulebook-conflict-detector/
├── ingest.py
├── rag_engine.py
├── main.py
├── evaluate.py
├── rulebook.md
├── test_questions.json
├── requirements.txt
├── benchmark_results.json
├── templates/
│   └── index.html
└── README.md
```
