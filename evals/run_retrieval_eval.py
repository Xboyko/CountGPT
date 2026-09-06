"""Retrieval eval for CountGPT.

Scores the hybrid ID + MiniLM index only — not LLM prose.

Usage:
  python evals/run_retrieval_eval.py
  python -m evals.run_retrieval_eval
  python evals/run_retrieval_eval.py --dry-run
  python evals/run_retrieval_eval.py --fixture

If rules_with_embeddings.pkl is missing, the real-store run prints a skip
message and exits 0. A completed run exits 1 when hit-rate falls below
``min_hit_rate`` in the cases file (default 0.70).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import retrieve  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "retrieval_cases.json"
DEFAULT_MIN_HIT_RATE = 0.70

FIXTURE_RULES = [
    {"id": "AC-2", "title": "Account Management", "text": "Manage information system accounts."},
    {"id": "AC-2(1)", "title": "Automated Account Management", "text": "Automate account management."},
    {"id": "AC-11", "title": "Device Lock", "text": "Lock the session after inactivity."},
    {"id": "AC-20", "title": "Use of External Systems", "text": "Authorize use of external systems."},
    {"id": "AU-2", "title": "Event Logging", "text": "Identify the types of events to log."},
    {"id": "AU-6", "title": "Audit Record Review", "text": "Review and analyze audit records."},
    {"id": "CM-7", "title": "Least Functionality", "text": "Disable unused ports and services."},
    {"id": "IA-2", "title": "Identification and Authentication", "text": "Unique identification; multi-factor."},
    {"id": "IR-4", "title": "Incident Handling", "text": "Implement an incident handling process."},
    {"id": "RA-5", "title": "Vulnerability Monitoring and Scanning", "text": "Scan for vulnerabilities."},
    {"id": "SC-7", "title": "Boundary Protection", "text": "Monitor and control communications at the boundary."},
    {"id": "SC-8", "title": "Transmission Confidentiality and Integrity", "text": "Protect transmitted information."},
    {"id": "SI-2", "title": "Flaw Remediation", "text": "Install security-relevant software updates."},
]


class DummyModel:
    """Zero embeddings so fixture mode needs no GPU / MiniLM download."""

    def encode(self, _q):
        return np.zeros(8, dtype=np.float32)


def load_cases(path: Path | None = None) -> dict:
    cases_path = path or CASES_PATH
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("retrieval_cases.json must be an object with a cases list")
    return data


def validate_cases(data: dict) -> list[str]:
    errors = []
    cases = data.get("cases") or []
    if len(cases) < 20:
        errors.append(f"need at least 20 cases, found {len(cases)}")
    seen = set()
    for i, case in enumerate(cases):
        prefix = f"cases[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue
        cid = case.get("id")
        if not cid or cid in seen:
            errors.append(f"{prefix}.id missing or duplicate")
        seen.add(cid)
        if not (case.get("query") or "").strip():
            errors.append(f"{prefix}.query is required")
        expected = case.get("expected_ids")
        if not isinstance(expected, list):
            errors.append(f"{prefix}.expected_ids must be a list")
        kind = case.get("kind")
        if kind not in {"exact_id", "topical", "hard", "negative"}:
            errors.append(f"{prefix}.kind must be exact_id|topical|hard|negative")
        if kind == "negative" and expected:
            errors.append(f"{prefix} negative cases must have empty expected_ids")
        if kind != "negative" and not expected:
            errors.append(f"{prefix} positive cases need at least one expected id")
    return errors


def fixture_store() -> dict:
    rules = FIXTURE_RULES
    return {
        "rules": rules,
        "embeddings": np.zeros((len(rules), 8), dtype=np.float32),
        "index_by_id": {
            retrieve.canonicalize_control_id(r["id"]): i for i, r in enumerate(rules)
        },
    }


def ids_hit(retrieved: list[dict], expected: list[str]) -> bool:
    if not expected:
        return len(retrieved) == 0
    got = {retrieve.canonicalize_control_id(m.get("id", "")) for m in retrieved}
    want = {retrieve.canonicalize_control_id(x) for x in expected}
    return bool(got & want)


def precision_at_k(retrieved: list[dict], expected: list[str]) -> float:
    if not retrieved:
        return 1.0 if not expected else 0.0
    if not expected:
        return 0.0
    want = {retrieve.canonicalize_control_id(x) for x in expected}
    hits = sum(
        1
        for m in retrieved
        if retrieve.canonicalize_control_id(m.get("id", "")) in want
    )
    return hits / len(retrieved)


def evaluate_cases(
    cases: list[dict],
    *,
    store=None,
    model=None,
    k: int = 4,
    min_score: float = 0.35,
) -> dict:
    rows = []
    for case in cases:
        hits = retrieve.retrieve(
            case["query"],
            k=k,
            min_score=min_score,
            store=store,
            model=model,
        )
        expected = case.get("expected_ids") or []
        row = {
            "id": case.get("id"),
            "kind": case.get("kind"),
            "query": case["query"],
            "expected_ids": expected,
            "retrieved_ids": [m.get("id", "") for m in hits],
            "hit": ids_hit(hits, expected),
            "precision_at_k": precision_at_k(hits, expected),
        }
        rows.append(row)

    hit_rate = sum(1 for r in rows if r["hit"]) / len(rows) if rows else 0.0
    p_at_k = (
        sum(r["precision_at_k"] for r in rows) / len(rows) if rows else 0.0
    )
    return {
        "n": len(rows),
        "hit_rate": hit_rate,
        "precision_at_k": p_at_k,
        "rows": rows,
    }


def print_report(summary: dict, *, min_hit_rate: float, skipped: str | None = None) -> None:
    if skipped:
        print(skipped)
        return
    print("CountGPT retrieval eval (index only — not LLM prose)")
    print(f"cases: {summary['n']}")
    print(f"hit-rate: {summary['hit_rate']:.3f}  (threshold {min_hit_rate:.2f})")
    print(f"precision-at-k: {summary['precision_at_k']:.3f}")
    misses = [r for r in summary["rows"] if not r["hit"]]
    if misses:
        print("misses:")
        for row in misses:
            print(
                f"  - {row['id']}: expected {row['expected_ids'] or '[]'} "
                f"got {row['retrieved_ids']}"
            )


def try_real_store():
    try:
        store = retrieve.load_store()
    except FileNotFoundError:
        return None, (
            "SKIP: rules_with_embeddings.pkl not found. "
            "From the project root run: python setup_data.py"
        )
    try:
        model = retrieve.get_model()
    except Exception as exc:  # noqa: BLE001
        return None, f"SKIP: embedding model failed to load ({exc})"
    return (store, model), None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        default=str(CASES_PATH),
        help="Path to retrieval_cases.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the cases file only; do not load the pickle or MiniLM.",
    )
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Score exact-ID and negative cases on a tiny in-memory store (no GPU).",
    )
    args = parser.parse_args(argv)

    data = load_cases(Path(args.cases))
    errors = validate_cases(data)
    if errors:
        print("Invalid retrieval cases:")
        for err in errors:
            print(f"  - {err}")
        return 2

    min_hit_rate = float(data.get("min_hit_rate") or DEFAULT_MIN_HIT_RATE)
    k = int(data.get("k") or 4)
    min_score = float(data.get("min_score") or retrieve.DEFAULT_MIN_SCORE)

    if args.dry_run:
        print(f"OK: {len(data['cases'])} retrieval cases are well-formed.")
        print("This suite scores retrieval, not LLM prose.")
        return 0

    if args.fixture:
        cases = [
            c
            for c in data["cases"]
            if c.get("kind") in {"exact_id", "negative"}
        ]
        summary = evaluate_cases(
            cases,
            store=fixture_store(),
            model=DummyModel(),
            k=k,
            min_score=0.99,
        )
        print_report(summary, min_hit_rate=1.0)
        if summary["hit_rate"] < 1.0:
            print("FAIL: fixture exact-ID / negative cases should all hit.")
            return 1
        return 0

    loaded, skip = try_real_store()
    if skip:
        print(skip)
        return 0
    store, model = loaded
    summary = evaluate_cases(
        data["cases"],
        store=store,
        model=model,
        k=k,
        min_score=min_score,
    )
    print_report(summary, min_hit_rate=min_hit_rate)
    if summary["hit_rate"] < min_hit_rate:
        print(
            f"FAIL: hit-rate {summary['hit_rate']:.3f} is below "
            f"regression threshold {min_hit_rate:.2f}."
        )
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
