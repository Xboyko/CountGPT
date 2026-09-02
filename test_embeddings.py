from sentence_transformers import SentenceTransformer

print("Loading the model (this happens once, may take a minute the first time)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

sentence1 = "How do I manage user accounts securely?"
sentence2 = "Define and document the types of accounts allowed within the system."
sentence3 = "What is the weather like today?"

embedding1 = model.encode(sentence1)
embedding2 = model.encode(sentence2)
embedding3 = model.encode(sentence3)

print("\nLength of one fingerprint (how many numbers):", len(embedding1))
print("\nFirst 5 numbers of sentence 1's fingerprint:")
print(embedding1[:5])

similarity_1_2 = model.similarity(embedding1, embedding2)
similarity_1_3 = model.similarity(embedding1, embedding3)

print("\nSimilarity between sentence 1 and 2 (related meaning):", similarity_1_2)
print("Similarity between sentence 1 and 3 (unrelated meaning):", similarity_1_3)