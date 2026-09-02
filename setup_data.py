"""
Build CountGPT's local RAG data from scratch:

  NIST OSCAL download → clean_rules.json → rules_with_embeddings.pkl

Usage:
  python setup_data.py              # skip steps when outputs already exist
  python setup_data.py --force      # rebuild everything
  python setup_data.py --check      # verify artifacts only (no download/embed)
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys

NIST_DATA = "nist_data.json"
CLEAN_RULES = "clean_rules.json"
EMBEDDINGS_PKL = "rules_with_embeddings.pkl"
EXPECTED_MIN_RULES = 1000


def _run_module(script: str) -> None:
    """Run a sibling script with the same interpreter (works in venv)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, path], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def check_artifacts(verbose: bool = True) -> bool:
    ok = True
    for path in (NIST_DATA, CLEAN_RULES, EMBEDDINGS_PKL):
        if os.path.exists(path):
            size = os.path.getsize(path)
            if verbose:
                print(f"  OK  {path} ({size:,} bytes)")
        else:
            ok = False
            if verbose:
                print(f"  MISSING  {path}")

    if os.path.exists(CLEAN_RULES):
        with open(CLEAN_RULES, "r", encoding="utf-8") as f:
            rules = json.load(f)
        n = len(rules) if isinstance(rules, list) else 0
        if n < EXPECTED_MIN_RULES:
            ok = False
            if verbose:
                print(
                    f"  WARN  {CLEAN_RULES} has only {n} rules "
                    f"(expected ~{EXPECTED_MIN_RULES}+ from NIST 800-53 Rev 5)"
                )
        elif verbose:
            print(f"  OK  {CLEAN_RULES} contains {n} rules")

    if os.path.exists(EMBEDDINGS_PKL):
        with open(EMBEDDINGS_PKL, "rb") as f:
            data = pickle.load(f)
        rules = data.get("rules") or []
        embeddings = data.get("embeddings")
        n_rules = len(rules)
        n_emb = len(embeddings) if embeddings is not None else 0
        if n_rules == 0 or n_rules != n_emb:
            ok = False
            if verbose:
                print(
                    f"  WARN  {EMBEDDINGS_PKL} rules={n_rules} embeddings={n_emb} (mismatch or empty)"
                )
        elif verbose:
            print(f"  OK  {EMBEDDINGS_PKL} aligned ({n_rules} rules + embeddings)")

    ollama = shutil.which("ollama")
    if ollama:
        if verbose:
            print(f"  OK  ollama found ({ollama})")
    elif verbose:
        print(
            "  WARN  ollama not on PATH — install from https://ollama.com "
            "and run: ollama pull llama3.1:8b"
        )

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download NIST 800-53, extract controls, and build embeddings."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild all artifacts even if they already exist.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only verify existing artifacts (and Ollama on PATH).",
    )
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if args.check:
        print("Checking CountGPT data artifacts...")
        ok = check_artifacts(verbose=True)
        if not ok:
            print("\nSetup incomplete. Run: python setup_data.py")
            raise SystemExit(1)
        print("\nAll required data artifacts look ready.")
        print("Launch UI:  python chat_website.py")
        print("Or CLI:     python ask_chatbot.py")
        return

    print("CountGPT data setup")
    print(f"Working directory: {os.getcwd()}")

    if args.force or not os.path.exists(NIST_DATA):
        _run_module("test_download.py")
    else:
        print(f"\n=== Skipping download ({NIST_DATA} exists; use --force to refresh) ===")

    if args.force or not os.path.exists(CLEAN_RULES):
        _run_module("extract_all_rules.py")
    else:
        print(f"\n=== Skipping extract ({CLEAN_RULES} exists; use --force to refresh) ===")

    if args.force or not os.path.exists(EMBEDDINGS_PKL):
        _run_module("build_embeddings.py")
    else:
        print(
            f"\n=== Skipping embeddings ({EMBEDDINGS_PKL} exists; use --force to refresh) ==="
        )

    print("\n=== Verifying ===")
    ok = check_artifacts(verbose=True)
    if not ok:
        print("\nSetup finished with warnings. Fix issues above before chatting.")
        raise SystemExit(1)

    print("\nSetup complete.")
    print("Next:")
    print("  1. ollama pull llama3.1:8b   # once, if you have not already")
    print("  2. python chat_website.py    # Gradio UI")
    print("     python ask_chatbot.py     # one-shot CLI")


if __name__ == "__main__":
    main()
