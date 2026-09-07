import json
import os
import time
from datetime import datetime, timezone
from rag_engine import query_rulebook

BENCHMARK_FILE = "test_questions.json"
RESULTS_FILE = "benchmark_results.json"

if not os.path.exists(BENCHMARK_FILE):
    raise FileNotFoundError(f"Missing {BENCHMARK_FILE}! Ensure it is in the root directory.")

with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
    benchmark_data = json.load(f)

unanswerable_cases = benchmark_data.get("unanswerable_questions", [])
conflict_cases = benchmark_data.get("conflict_queries", [])

print("=" * 65)
print("  RULEBOOK RAG BENCHMARK & EVALUATION PIPELINE")
print(f"  Unanswerable Test Cases: {len(unanswerable_cases)}")
print(f"  Conflict Test Cases:     {len(conflict_cases)}")
print("=" * 65)

eval_results = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "unanswerable_eval": [],
    "conflict_eval": [],
    "summary_metrics": {}
}

# 1. EVALUATE UNANSWERABLE QUESTIONS (Hallucination Suppression)
print("\n>>> Running Hallucination Suppression Benchmark (Unanswerable Cases)...")
unanswerable_correct = 0

for i, item in enumerate(unanswerable_cases, 1):
    q_id = item.get("id", f"UNANS-{i:02d}")
    query = item.get("question", "")

    print(f"[{i}/{len(unanswerable_cases)}] Testing: {query[:60]}...")

    res = query_rulebook(query)
    is_success = (res.get("status") == "not_covered")
    if is_success:
        unanswerable_correct += 1

    eval_results["unanswerable_eval"].append({
        "id": q_id,
        "query": query,
        "expected_status": "not_covered",
        "predicted_status": res.get("status"),
        "success": is_success,
        "answer_snippet": res.get("answer", "")[:120]
    })

    time.sleep(4.2)

# 2. EVALUATE CONFLICT QUERIES (Contradiction Detection)
print("\n>>> Running Contradiction Detection Benchmark (Conflict Cases)...")
conflict_correct = 0

for i, item in enumerate(conflict_cases, 1):
    q_id = item.get("id", f"CONFLICT-{i:02d}")
    query = item.get("query", "")
    expected_sections = set(item.get("conflicting_sections", []))

    print(f"[{i}/{len(conflict_cases)}] Testing: {query[:60]}...")

    res = query_rulebook(query)
    is_conflict = (res.get("status") == "conflict")

    cited_sections = set(res.get("citations", []))
    if res.get("conflict_details"):
        cited_sections.update(res["conflict_details"].get("conflicting_sections", []))

    overlap = expected_sections.intersection(cited_sections)
    is_success = is_conflict and len(overlap) > 0

    if is_success:
        conflict_correct += 1

    eval_results["conflict_eval"].append({
        "id": q_id,
        "query": query,
        "expected_status": "conflict",
        "predicted_status": res.get("status"),
        "expected_sections": list(expected_sections),
        "detected_sections": list(cited_sections),
        "success": is_success,
        "nature_of_conflict": (res.get("conflict_details") or {}).get("nature_of_conflict", "")
    })

    time.sleep(4.2)

# 3. COMPUTE SUMMARY METRICS
total_unans = len(unanswerable_cases)
total_conf = len(conflict_cases)

refusal_rate = (unanswerable_correct / total_unans * 100) if total_unans > 0 else 0
conflict_rate = (conflict_correct / total_conf * 100) if total_conf > 0 else 0

eval_results["summary_metrics"] = {
    "total_unanswerable_tested": total_unans,
    "unanswerable_refusal_accuracy": f"{refusal_rate:.1f}%",
    "total_conflicts_tested": total_conf,
    "conflict_detection_accuracy": f"{conflict_rate:.1f}%"
}

with open(RESULTS_FILE, "w", encoding="utf-8") as out:
    json.dump(eval_results, out, indent=2)

print("\n" + "=" * 65)
print("                     BENCHMARK SUMMARY")
print("=" * 65)
print(f"  Unanswerable Questions Refusal Accuracy: {unanswerable_correct}/{total_unans} ({refusal_rate:.1f}%)")
print(f"  Contradiction Detection Accuracy:        {conflict_correct}/{total_conf} ({conflict_rate:.1f}%)")
print("=" * 65)
print(f"Report successfully saved to: {RESULTS_FILE}\n")