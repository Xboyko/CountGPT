#!/usr/bin/env python3
"""Write training_data.jsonl from the category example modules.

Usage (from repo root):
    python scripts/build_training_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sft_poam import examples as poam_examples
from sft_rmf import examples as rmf_examples
from sft_soc import examples as soc_examples
from sft_ssp import examples as ssp_examples
from sft_stig import examples as stig_examples


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


# Cap exported SFT rows in the requested 250–300 band while keeping
# category balance. Extra examples remain in the sft_*.py modules.
CATEGORY_EXPORT_CAPS = {
    "poam": 72,
    "ssp": 84,
    "rmf": 56,
    "soc": 42,
    "stig": 46,
}


def _normalize(rec: dict) -> dict:
    return {
        "instruction": rec["instruction"].strip(),
        "output": rec["output"].strip(),
    }


def take_spread(items: list[dict], n: int) -> list[dict]:
    """Keep the first items (seeded originals) and spread the rest."""
    if n >= len(items):
        return items
    if n <= 1:
        return items[:n]
    head = 1
    kept = list(items[:head])
    rest = items[head:]
    need = n - head
    if need >= len(rest):
        return items[:n]
    step = len(rest) / need
    for i in range(need):
        kept.append(rest[int(i * step)])
    return kept


def all_examples() -> list[dict]:
    blocks = {
        "poam": poam_examples(),
        "ssp": ssp_examples(),
        "rmf": rmf_examples(),
        "soc": soc_examples(),
        "stig": stig_examples(),
    }
    records: list[dict] = []
    for name, block in blocks.items():
        selected = take_spread(block, CATEGORY_EXPORT_CAPS[name])
        records.extend(_normalize(rec) for rec in selected)
    return records


def main() -> int:
    out = repo_root() / "training_data.jsonl"
    records = all_examples()
    lines = [json.dumps(r, ensure_ascii=False) + "\n" for r in records]
    out.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {len(records)} records to {out}")
    print(
        "source library sizes: "
        f"poam={len(poam_examples())} ssp={len(ssp_examples())} "
        f"rmf={len(rmf_examples())} soc={len(soc_examples())} "
        f"stig={len(stig_examples())}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
