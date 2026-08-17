#!/usr/bin/env python3
"""Eval harness for the CloudCart support agent — complete solution."""

import json
import sys
import time

sys.path.insert(0, "..")
from solution.agent import run_agent


def load_cases(path: str = "eval_cases.json") -> list:
    with open(path) as f:
        return json.load(f)


def grade(response: str, assertions: dict) -> dict:
    """Grade a response against deterministic assertions."""
    response_lower = response.lower()
    failures = []

    for term in assertions.get("must_contain", []):
        if term.lower() not in response_lower:
            failures.append(f"MISSING: '{term}'")

    for term in assertions.get("must_not_contain", []):
        if term.lower() in response_lower:
            failures.append(f"UNEXPECTED: '{term}'")

    if "must_contain_any" in assertions:
        if not any(t.lower() in response_lower
                   for t in assertions["must_contain_any"]):
            failures.append(
                f"MISSING_ANY: none of {assertions['must_contain_any']}"
            )

    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }


def run_eval(cases_path: str = "eval_cases.json", runs: int = 1):
    """Run the eval suite."""
    cases = load_cases(cases_path)
    all_results = []

    for run_idx in range(runs):
        print(f"\n{'='*50}")
        print(f"Run {run_idx + 1}/{runs}")
        print(f"{'='*50}")

        for case in cases:
            print(f"\n  {case['id']}: {case['name']}...", end=" ", flush=True)

            t0 = time.monotonic()
            try:
                response = run_agent(case["input"])
            except Exception as e:
                response = f"ERROR: {e}"
            latency = time.monotonic() - t0

            result = grade(response, case["assertions"])
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} ({latency:.1f}s)")

            if not result["passed"]:
                for f in result["failures"]:
                    print(f"    {f}")

            all_results.append({
                "run": run_idx,
                "case_id": case["id"],
                "name": case["name"],
                "passed": result["passed"],
                "failures": result["failures"],
                "response_excerpt": response[:200],
                "latency_s": round(latency, 2),
            })

    # Summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")

    if runs > 1:
        print(f"\nPer-case pass rate ({runs} runs):")
        for case in cases:
            case_results = [r for r in all_results if r["case_id"] == case["id"]]
            case_passed = sum(1 for r in case_results if r["passed"])
            print(f"  {case['id']} {case['name']}: {case_passed}/{runs}")

    with open("eval_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results: eval_results.json")


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_eval(runs=runs)
