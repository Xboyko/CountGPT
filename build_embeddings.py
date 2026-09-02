import json
from sentence_transformers import SentenceTransformer
import pickle

print("Loading clean_rules.json...")
with open("clean_rules.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

usable = []
skipped = 0
for rule in rules:
    text = (rule.get("text") or "").strip()
    if not text:
        skipped += 1
        continue
    usable.append(rule)

print(f"Loaded {len(rules)} rules; embedding {len(usable)}"
      + (f" (skipped {skipped} with empty text)" if skipped else ""))

print("Loading the embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

texts_to_embed = []
for rule in usable:
    title = (rule.get("title") or "").strip()
    combined = (title + ". " if title else "") + rule["text"]
    texts_to_embed.append(combined)

print("Turning all rules into fingerprints... this may take a minute or two")
embeddings = model.encode(texts_to_embed, show_progress_bar=True)

print("Saving everything to disk...")
with open("rules_with_embeddings.pkl", "wb") as f:
    pickle.dump({"rules": usable, "embeddings": embeddings}, f)

print("Done! Saved rules_with_embeddings.pkl")
