import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from triage import triage_email

EVALS_DIR = Path(__file__).parent
TEST_CASES_PATH = EVALS_DIR / "test_cases.json"
PASS_THRESHOLD = 0.70


def load_test_cases():
    return json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))


def score_result(expected, actual):
    scores = {}
    scores["intent_match"] = 1 if actual.intent == expected["expected_intent"] else 0
    scores["urgency_match"] = 1 if actual.urgency == expected["expected_urgency"] else 0
    scores["escalate_match"] = 1 if actual.escalate == expected["expected_escalate"] else 0
    return scores


def run_evals():
    test_cases = load_test_cases()
    results = []
    total_scores = {"intent_match": 0, "urgency_match": 0, "escalate_match": 0}
    total_cases = len(test_cases)

    print(f"\n{'='*70}")
    print(f"  Mumzworld CS Triage -- Eval Suite ({total_cases} cases)")
    print(f"{'='*70}\n")

    for i, tc in enumerate(test_cases, 1):
        tc_id = tc["id"]
        email = tc["email"]
        print(f"[{i}/{total_cases}] Running {tc_id}...", end=" ", flush=True)

        start = time.time()
        try:
            output = triage_email(email)
            elapsed = round(time.time() - start, 1)
            scores = score_result(tc, output)

            for key in total_scores:
                total_scores[key] += scores[key]

            case_total = sum(scores.values())
            status = "PASS" if case_total == 3 else f"PARTIAL ({case_total}/3)"

            result = {
                "id": tc_id,
                "status": status,
                "elapsed_s": elapsed,
                "expected_intent": tc["expected_intent"],
                "actual_intent": output.intent,
                "expected_urgency": tc["expected_urgency"],
                "actual_urgency": output.urgency,
                "expected_escalate": tc["expected_escalate"],
                "actual_escalate": output.escalate,
                "confidence": output.confidence,
                "scores": scores,
                "reasoning": output.reasoning,
                "notes": tc.get("notes", ""),
            }
            results.append(result)

            print(f"{status} ({elapsed}s) -- intent:{output.intent} urg:{output.urgency} esc:{output.escalate} conf:{output.confidence}")

            if case_total < 3:
                misses = [k for k, v in scores.items() if v == 0]
                print(f"         > missed: {', '.join(misses)}")

        except Exception as e:
            elapsed = round(time.time() - start, 1)
            print(f"ERROR ({elapsed}s) -- {e}")
            results.append({
                "id": tc_id,
                "status": "ERROR",
                "elapsed_s": elapsed,
                "error": str(e),
            })

        if i < total_cases:
            time.sleep(1)

    max_score = total_cases * 3
    actual_score = sum(total_scores.values())
    overall_pct = round(actual_score / max_score * 100, 1) if max_score > 0 else 0

    print(f"\n{'='*70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  Intent accuracy:   {total_scores['intent_match']}/{total_cases} ({round(total_scores['intent_match']/total_cases*100,1)}%)")
    print(f"  Urgency accuracy:  {total_scores['urgency_match']}/{total_cases} ({round(total_scores['urgency_match']/total_cases*100,1)}%)")
    print(f"  Escalate accuracy: {total_scores['escalate_match']}/{total_cases} ({round(total_scores['escalate_match']/total_cases*100,1)}%)")
    print(f"  Overall score:     {actual_score}/{max_score} ({overall_pct}%)")
    print(f"  Pass threshold:    {PASS_THRESHOLD*100}%")
    print(f"  Result:            {'PASS' if overall_pct >= PASS_THRESHOLD*100 else 'FAIL'}")
    print(f"{'='*70}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EVALS_DIR / f"results_{timestamp}.json"
    output_data = {
        "timestamp": timestamp,
        "total_cases": total_cases,
        "scores": total_scores,
        "overall_pct": overall_pct,
        "passed": overall_pct >= PASS_THRESHOLD * 100,
        "cases": results,
    }
    output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to {output_path}")

    sys.exit(0 if overall_pct >= PASS_THRESHOLD * 100 else 1)


if __name__ == "__main__":
    run_evals()
