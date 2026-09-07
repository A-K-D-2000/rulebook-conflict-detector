The Rulebook That Argues With Itself
====================================

A specialized Retrieval-Augmented Generation (RAG) system built with FastAPI and Google Gemini that indexes institutional university regulations, retrieves relevant clauses with visible similarity scores, detects internal policy contradictions across chapters, and refuses to hallucinate when the corpus is silent.

Problem Overview
----------------

University regulations are notoriously prone to internal friction:

*   One clause mandates a 75% attendance threshold to sit for exams.
    
*   Another clause allows medical exemptions down to 50%.
    
*   A separate appeals committee claims exclusive power to condone attendance down to 60%.
    

Standard AI chatbots give misleading, overconfident answers by latching onto whichever passage they find first. This system is designed to read all relevant clauses simultaneously, providing:

1.  **Clause-Level Citations:** Explicit references (e.g., Section 3.1) and quotes.
    
2.  **Side-by-Side Scoring:** Direct, visible cosine similarity scores (never hidden behind clicks).
    
3.  **Strict 3-State Classification:**
    
    *   **ANSWERED:** Unambiguous answers supported by cited text.
        
    *   **NOT COVERED:** Explicit refusal to hallucinate when the corpus is silent.
        
    *   **CONFLICT:** Automatic detection and breakdown of internal policy contradictions.
        

Corpus & Planted Contradictions
-------------------------------

The source policy manual (rulebook.md) contains over 6,000 words across 12 chapters, structured into 71 discrete sections. Exactly three policy contradictions were planted for evaluation:

#Conflict AreaConflicting SectionsNature of Contradiction1Exam Attendance ThresholdSection 3.1 vs Section 5.4 vs Section 12.2Sec 3.1 mandates a strict 75% threshold with no waivers; Sec 5.4 lowers it to 50% for medical leave; Sec 12.2 gives the Academic Committee sole authority to waive attendance down to 60% and bans waivers below 60%.2Merit Scholarship RetentionSection 7.2 vs Section 9.1Sec 7.2 requires an 8.50 CGPA with zero exceptions across all cohorts; Sec 9.1 permits varsity student-athletes to retain merit scholarships at an 8.00 CGPA.3Grade Review DeadlinesSection 4.3 vs Section 11.1Sec 4.3 enforces a strict deadline of 7 calendar days to apply for grade re-evaluation; Sec 11.1 allows up to 14 working days to submit re-checking petitions.

Benchmark & Evaluation Results
------------------------------

The system was evaluated against test\_questions.json using an automated testing pipeline (evaluate.py):

*   **25 Hard Unanswerable Edge Cases:** Plausible student scenarios completely absent from the text (e.g., missing exams for a sibling's wedding, charging e-scooters in dorms, pet fish, reality TV leaves).
    
*   **3 Planted Contradiction Queries:** Multi-clause policy questions designed to trigger conflicting sections.
    

### Summary Metrics

*   **Unanswerable Questions Refusal Accuracy:** 21/25 (84.0%)
    
*   **Contradiction Detection Accuracy:** 3/3 (100.0%)
    

### Key Takeaways

*   **Conflict Detection (100%):** Successfully flagged all internal contradictions, identified conflicting section numbers, and detailed the conflict.
    
*   **Hallucination Suppression (84%):** Correctly identified silence on 21 of 25 deceptive edge cases without fabricating university policies.
    

System Architecture
-------------------

*   **Ingestion & Parser (ingest.py):** Slices raw markdown into 71 structured section objects with metadata (chapter, section ID, title, body).
    
*   **Vector Retrieval (rag\_engine.py):** Generates vector representations using gemini-embedding-001 and performs in-memory pure-Python cosine similarity matching.
    
*   **Reasoning Engine (rag\_engine.py):** Uses gemini-3.5-flash-lite with structured JSON schema output and automated retry logic for API resilience.
    
*   **Web Service (main.py):** FastAPI backend with POST /ask and a side-by-side verification interface (templates/index.html).
    

Quickstart & Setup
------------------

### 1\. Clone & Install Dependencies

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone   cd rulebook-conflict-detector  python -m venv venv  .\venv\Scripts\activate  pip install -r requirements.txt   `

### 2\. Configure Environment

Create a .env file in the root directory:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   GEMINI_API_KEY=your_free_google_gemini_api_key   `

### 3\. Ingest & Index Corpus

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python ingest.py   `

### 4\. Run the Web Application

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python main.py   `

Open http://127.0.0.1:8000 in your browser to interact with the side-by-side UI.

### 5\. Run the Evaluation Suite

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python evaluate.py   `

Outputs benchmark progress and exports full evaluation logs to benchmark\_results.json.

Project Structure
-----------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   rulebook-conflict-detector/  ├── ingest.py  ├── rag_engine.py  ├── main.py  ├── evaluate.py  ├── rulebook.md  ├── test_questions.json  ├── requirements.txt  ├── benchmark_results.json  ├── templates/  │   └── index.html  └── README.md   `

GitHub Desktop
--------------

After pasting the corrected content into README.md:

1.  Save README.md (Ctrl + S).
    
2.  Go to **GitHub Desktop**.
    
3.  Use the commit summary:docs: complete readme setup instructions
    
4.  Click **Commit to main**.
    
5.  Click **Push origin**.