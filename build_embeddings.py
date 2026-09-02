"""Embed clean_rules.json with MiniLM and save rules_with_embeddings.pkl."""

import json
import os
import pickle
import sys

from sentence_transformers import SentenceTransformer

IN_PATH = "clean_rules.json"
OUT_PATH = "rules_with_embeddings.pkl"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


def build_embeddings(in_path=IN_PATH, out_path=OUT_PATH, model_name=EMBED_MODEL_NAME):
    if not os.path.exists(in_path):
        raise FileNotFoundError(
            f"{in_path} not found. Run extract_all_rules.py (or setup_data.py) first."
        )

    print(f"Loading {in_path}...")
    with open(in_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    usable = []
    skipped = 0
    for rule in rules:
        text = (rule.get("text") or "").strip()
        if not text:
            skipped += 1
            continue
        usable.append(rule)

    print(
        f"Loaded {len(rules)} rules; embedding {len(usable)}"
        + (f" (skipped {skipped} with empty text)" if skipped else "")
    )
    if not usable:
        raise ValueError(f"No embeddable rules found in {in_path}")

    print(f"Loading the embedding model ({model_name})...")
    model = SentenceTransformer(model_name)

    texts_to_embed = []
    for rule in usable:
        title = (rule.get("title") or "").strip()
        combined = (title + ". " if title else "") + rule["text"]
        texts_to_embed.append(combined)

    print("Turning all rules into fingerprints... this may take a minute or two")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)

    print(f"Saving {out_path}...")
    with open(out_path, "wb") as f:
        pickle.dump({"rules": usable, "embeddings": embeddings}, f)

    print(f"Done! Saved {out_path} ({len(usable)} rules)")
    return out_path


def main():
    try:
        build_embeddings()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
