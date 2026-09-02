import retrieve

print("Loading saved rules and fingerprints...")
try:
    retrieve.load_store()
except FileNotFoundError:
    print(retrieve.pkl_missing_message())
    raise SystemExit(1)

print("Loading the embedding model...")
retrieve.get_model()

question = input("\nAsk a question about NIST rules: ")

matches = retrieve.retrieve(question, k=4)

print("\nTop matching rules:\n")
if not matches:
    print("No rules met the similarity floor (and no control ID was found in the question).")
else:
    for rank, rule in enumerate(matches, start=1):
        print(
            f"{rank}. {rule['id']} - {rule['title']}  "
            f"(score: {rule['score']:.4f}, {rule['source']})"
        )
