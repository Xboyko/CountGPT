#!/usr/bin/env python3
"""Validate CountGPT SFT data in training_data.jsonl.

Checks JSONL parse, minimum count, required keys, empty fields, rough
category balance, and near-duplicate instructions.

Usage (from repo root):
    python scripts/validate_training_data.py
    python scripts/validate_training_data.py --path training_data.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REQUIRED_KEYS = ("instruction", "output")
MIN_RECORDS = 200
PREFERRED_RECORDS = 250
NEAR_DUP_JACCARD = 0.82

# Soft floors so one category cannot dominate an otherwise large file.
MIN_CATEGORY = {
    "poam": 40,
    "ssp": 40,
    "rmf": 25,
    "soc": 20,
    "stig_scan": 15,
}

# Plugin-style IDs and CVE-like strings that are not placeholders.
CVE_FACT_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
PLUGIN_FACT_RE = re.compile(
    r"\b(?:plugin(?:\s+id)?|pluginid)\s*[#:]?\s*\d{4,7}\b",
    re.IGNORECASE,
)
PLACEHOLDER_HINT = re.compile(
    r"\[(?:plugin(?:\s+id)?|plugin number|cve|vulnerability/cve)[^\]]*\]",
    re.IGNORECASE,
)

WORD_RE = re.compile(r"[a-z0-9]+")

CATEGORY_RULES = (
    (
        "poam",
        (
            "poa&m",
            "poam",
            "p.o.a.m",
            "false positive",
            "risk adjustment",
            "vendor dependency",
            "past-due",
            "overdue",
            "emass",
            "weakness:",
            "required action:",
        ),
    ),
    (
        "ssp",
        (
            "implementation statement",
            "control implementation",
            "customer responsibility",
            "events logged",
            "baseline enforcement",
        ),
    ),
    (
        "soc",
        (
            "soc analyst",
            "triage",
            "splunk alert",
            "failed login",
            "outbound traffic",
            "service account",
            "escalate",
            "walk through the triage",
        ),
    ),
    (
        "stig_scan",
        (
            "stig",
            "credentialed",
            "uncredentialed",
            "scap",
            "acas",
            "nessus",
            "ckl",
            "cat i",
            "cat ii",
            "cat iii",
        ),
    ),
    (
        "rmf",
        (
            "authorizing official",
            "isso",
            "issm",
            "continuous monitoring",
            "security assessment report",
            "authorization to operate",
            "authority to operate",
            "rmf",
            "srtm",
            "3pao",
            "fedramp",
            "common control",
            "tailor",
            "categorization",
        ),
    ),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_dataset_path() -> Path:
    return repo_root() / "training_data.jsonl"


def load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    records: list[dict] = []
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return [], [f"{path}: file is empty"]
    for i, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            errors.append(f"line {i}: blank line")
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {i}: JSON parse error: {exc}")
            continue
        if not isinstance(obj, dict):
            errors.append(f"line {i}: record is {type(obj).__name__}, expected object")
            continue
        records.append(obj)
        missing = [k for k in REQUIRED_KEYS if k not in obj]
        if missing:
            errors.append(f"line {i}: missing key(s): {', '.join(missing)}")
            continue
        extra = sorted(set(obj) - set(REQUIRED_KEYS))
        if extra:
            errors.append(f"line {i}: unexpected key(s): {', '.join(extra)}")
        for key in REQUIRED_KEYS:
            value = obj.get(key)
            if not isinstance(value, str):
                errors.append(f"line {i}: {key} must be a string")
            elif not value.strip():
                errors.append(f"line {i}: {key} is empty")
    return records, errors


def classify(record: dict) -> str:
    inst = record.get("instruction", "").lower()
    blob = f"{inst}\n{record.get('output', '')}".lower()
    scores: dict[str, int] = {}
    for name, needles in CATEGORY_RULES:
        scores[name] = sum(1 for n in needles if n in blob)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "other"

    drafting = any(
        w in inst
        for w in ("draft", "write a ", "write an ", "create a ", "fill out")
    )
    explainer = any(
        w in inst
        for w in (
            "explain",
            "what is",
            "what are",
            "what does",
            "difference",
            "how does",
            "how do ",
            "how should",
            "why ",
            "who is",
            "walk through the nist rmf",
        )
    )

    if "implementation statement" in inst or "control implementation" in inst:
        return "ssp"
    if "triage" in inst or "soc analyst" in inst:
        return "soc"
    if drafting and any(
        w in inst for w in ("poa&m", "poam", "false positive", "risk adjustment")
    ):
        return "poam"
    if explainer and not drafting:
        if any(
            w in inst
            for w in (
                "stig",
                "credentialed",
                "uncredentialed",
                "acas",
                "scap",
                "ckl",
                "nessus",
            )
        ):
            return "stig_scan"
        if scores.get("rmf", 0) or any(
            w in inst
            for w in (
                "rmf",
                "ato",
                "isso",
                "issm",
                "authorizing",
                "sar",
                "ssp",
                "fedramp",
                "continuous monitoring",
            )
        ):
            return "rmf"
    return best


def tokenize(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def near_duplicates(records: list[dict]) -> list[str]:
    issues: list[str] = []
    tokens = [tokenize(r.get("instruction", "")) for r in records]
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            score = jaccard(tokens[i], tokens[j])
            if score >= NEAR_DUP_JACCARD:
                issues.append(
                    f"near-duplicate instructions (jaccard={score:.2f}) "
                    f"lines {i + 1} and {j + 1}"
                )
    return issues


def invented_ids(records: list[dict]) -> list[str]:
    issues: list[str] = []
    for i, rec in enumerate(records, start=1):
        blob = f"{rec.get('instruction', '')}\n{rec.get('output', '')}"
        if CVE_FACT_RE.search(blob) and not PLACEHOLDER_HINT.search(blob):
            issues.append(
                f"line {i}: CVE-looking identifier presented as a fact; "
                "use a placeholder such as [CVE]"
            )
        if PLUGIN_FACT_RE.search(blob) and not PLACEHOLDER_HINT.search(blob):
            issues.append(
                f"line {i}: numeric plugin id presented as a fact; "
                "use a placeholder such as [plugin id]"
            )
    return issues


def category_counts(records: list[dict]) -> dict[str, int]:
    return dict(Counter(classify(r) for r in records))


def validate(path: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    if not path.is_file():
        return [f"dataset not found: {path}"], {}

    records, parse_errors = load_jsonl(path)
    errors.extend(parse_errors)

    counts = category_counts(records) if records else {}
    info = {
        "path": str(path),
        "n": len(records),
        "categories": counts,
    }

    if len(records) < MIN_RECORDS:
        errors.append(
            f"only {len(records)} records; need at least {MIN_RECORDS} "
            f"(prefer {PREFERRED_RECORDS}–300)"
        )

    errors.extend(near_duplicates(records))
    errors.extend(invented_ids(records))

    for name, floor in MIN_CATEGORY.items():
        n = counts.get(name, 0)
        if n < floor:
            errors.append(
                f"category {name!r} has {n} records; expected at least {floor}"
            )

    return errors, info


def format_report(info: dict, errors: list[str]) -> str:
    cats = info.get("categories") or {}
    lines = [
        f"dataset: {info.get('path', '')}",
        f"records: {info.get('n', 0)}",
        "category counts:",
    ]
    for name in ("poam", "ssp", "rmf", "soc", "stig_scan", "other"):
        if name in cats:
            lines.append(f"  {name}: {cats[name]}")
    extra = sorted(set(cats) - {"poam", "ssp", "rmf", "soc", "stig_scan", "other"})
    for name in extra:
        lines.append(f"  {name}: {cats[name]}")
    if errors:
        lines.append("status: FAIL")
        lines.extend(f"  - {e}" for e in errors)
    else:
        lines.append("status: PASS")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=default_dataset_path(),
        help="JSONL path (default: repo-root training_data.jsonl)",
    )
    args = parser.parse_args(argv)
    errors, info = validate(args.path)
    print(format_report(info, errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
