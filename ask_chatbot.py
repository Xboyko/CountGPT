import ollama
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
context_text = retrieve.format_matches(matches)

if not matches:
    prompt = f"""You are a cybersecurity assistant. Retrieval found no NIST 800-53
controls that match this question closely enough (no control ID hit and no
embedding above the similarity floor). Do NOT invent a control number or quote
a control that was not provided. Tell the user you could not find a confident
match and suggest they name a control ID (for example AC-2) or rephrase.

Question: {question}

Answer:"""
else:
    prompt = f"""You are a helpful cybersecurity assistant. Answer the question using ONLY the NIST rules provided below. Mention which rule ID(s) you used.

NIST rules:
{context_text}

Question: {question}

Answer:"""

print("\nAsking the AI model... (this may take a moment)\n")

response = ollama.chat(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": prompt}],
)

print("=== ANSWER ===\n")
print(response["message"]["content"])
