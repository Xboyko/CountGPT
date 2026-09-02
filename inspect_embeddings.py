import pickle

with open("rules_with_embeddings.pkl", "rb") as f:
    data = pickle.load(f)

rules = data["rules"]
embeddings = data["embeddings"]

print("Number of rules stored:", len(rules))
print("Number of fingerprints stored:", len(embeddings))
print()
print("First rule's info:")
print("ID:", rules[0]["id"])
print("Title:", rules[0]["title"])
print()
print("First rule's fingerprint (first 5 numbers):")
print(embeddings[0][:5])