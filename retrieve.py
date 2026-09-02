"""Shared NIST 800-53 retrieval: exact control-ID lookup + MiniLM cosine search."""

import os
import pickle
import re

import numpy as np

PKL_PATH = "rules_with_embeddings.pkl"
DEFAULT_K = 4
DEFAULT_MIN_SCORE = 0.35
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

NIST_FAMILIES = {
    "ac", "at", "au", "ca", "cm", "cp", "ia", "ir", "ma", "mp",
    "pe", "pl", "pm", "ps", "pt", "ra", "sa", "sc", "si", "sr",
}
# AC-2, ac-2, AC-2.1, AC-2(1)
CONTROL_ID_RE = re.compile(
    r"\b([A-Za-z]{2,3})-(\d+)(?:\((\d+)\)|\.(\d+))?"
)

_store = None
_model = None


def canonicalize_control_id(cid):
    """Normalize AC-2, ac-02, AC-2(1), ac-2.1 -> ac-2 / ac-2.1."""
    if not cid:
        return ""
    s = str(cid).strip().lower().replace(" ", "")
    s = re.sub(r"\((\d+)\)", r".\1", s)
    m = re.match(r"^([a-z]{2,3})-0*(\d+)(?:\.0*(\d+))?$", s)
    if not m:
        return s
    if m.group(3):
        return f"{m.group(1)}-{int(m.group(2))}.{int(m.group(3))}"
    return f"{m.group(1)}-{int(m.group(2))}"


def extract_control_ids(query):
    """Return unique canonical IDs mentioned in the query, in order."""
    found = []
    seen = set()
    for match in CONTROL_ID_RE.finditer(query or ""):
        family, number = match.group(1), match.group(2)
        if family.lower() not in NIST_FAMILIES:
            continue
        enh = match.group(3) or match.group(4)
        raw = f"{family}-{number}" + (f".{enh}" if enh else "")
        canon = canonicalize_control_id(raw)
        if canon and canon not in seen:
            seen.add(canon)
            found.append(canon)
    return found


def relation_to_query_id(rule_canon, query_canon):
    """exact | parent | enhancement | None. Avoids AC-20 matching AC-2."""
    if not rule_canon or not query_canon:
        return None
    if rule_canon == query_canon:
        return "exact"
    if rule_canon.startswith(query_canon + "."):
        return "enhancement"
    if "." in query_canon:
        parent = query_canon.rsplit(".", 1)[0]
        if rule_canon == parent:
            return "parent"
    return None


def embeddings_to_numpy(embeddings):
    """Accept torch tensors or numpy arrays from pickle."""
    if embeddings is None:
        return np.zeros((0, 1), dtype=np.float32)
    if hasattr(embeddings, "detach"):
        embeddings = embeddings.detach().cpu().numpy()
    elif hasattr(embeddings, "numpy") and not isinstance(embeddings, np.ndarray):
        try:
            embeddings = embeddings.numpy()
        except Exception:
            pass
    arr = np.asarray(embeddings)
    if arr.dtype != np.float32:
        arr = arr.astype(np.float32, copy=False)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return arr


def cosine_scores(query_vec, embeddings):
    q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
    E = embeddings_to_numpy(embeddings)
    if E.size == 0:
        return np.array([], dtype=np.float32)
    qn = float(np.linalg.norm(q)) + 1e-12
    En = np.linalg.norm(E, axis=1) + 1e-12
    return (E @ q) / (En * qn)


def load_store(path=PKL_PATH):
    global _store
    if _store is not None and path == PKL_PATH:
        return _store
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "rb") as f:
        data = pickle.load(f)
    rules = data.get("rules") or []
    embeddings = embeddings_to_numpy(data.get("embeddings"))
    index_by_id = {}
    for i, rule in enumerate(rules):
        canon = canonicalize_control_id(rule.get("id", ""))
        if canon and canon not in index_by_id:
            index_by_id[canon] = i
    store = {
        "rules": rules,
        "embeddings": embeddings,
        "index_by_id": index_by_id,
        "path": path,
    }
    if path == PKL_PATH:
        _store = store
    return store


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def _match_dict(rule, score, source):
    return {
        "id": rule.get("id", ""),
        "title": rule.get("title", ""),
        "text": rule.get("text", ""),
        "score": float(score),
        "source": source,
    }


def retrieve(query, k=DEFAULT_K, min_score=DEFAULT_MIN_SCORE, store=None, model=None):
    """Return up to k matches: ID hits first (plus nearby enhancements), then semantic.

    Exact ID matches ignore the similarity floor. Semantic hits must meet min_score.
    """
    if store is None:
        store = load_store()
    rules = store["rules"]
    embeddings = store["embeddings"]
    index_by_id = store.get("index_by_id") or {}
    k = max(int(k), 0)
    if k == 0 or not rules:
        return []

    mentioned = extract_control_ids(query)
    chosen = []
    used = set()
    rank = {"exact": 0, "parent": 1, "enhancement": 2}

    id_candidates = []
    if mentioned:
        for i, rule in enumerate(rules):
            canon = canonicalize_control_id(rule.get("id", ""))
            best_rel = None
            for qid in mentioned:
                rel = relation_to_query_id(canon, qid)
                if rel and (best_rel is None or rank[rel] < rank[best_rel]):
                    best_rel = rel
            if best_rel:
                id_candidates.append((rank[best_rel], canon, i, best_rel))
        id_candidates.sort(key=lambda x: (x[0], x[1]))
        for _rk, _canon, idx, rel in id_candidates:
            if len(chosen) >= k:
                break
            if idx in used:
                continue
            used.add(idx)
            chosen.append(_match_dict(rules[idx], 1.0, f"id:{rel}"))

    remaining = k - len(chosen)
    if remaining <= 0:
        return chosen[:k]

    if model is None:
        model = get_model()
    query_vec = model.encode(query or "")
    scores = cosine_scores(query_vec, embeddings)

    # If mentioned IDs exist in the catalog but were missed (label vs id), try index
    for qid in mentioned:
        idx = index_by_id.get(qid)
        if idx is not None and idx not in used and len(chosen) < k:
            used.add(idx)
            chosen.append(_match_dict(rules[idx], 1.0, "id:exact"))

    remaining = k - len(chosen)
    if remaining <= 0:
        return chosen[:k]

    order = np.argsort(-scores)
    for idx in order:
        if remaining <= 0:
            break
        idx = int(idx)
        if idx in used:
            continue
        score = float(scores[idx])
        if score < min_score:
            break
        used.add(idx)
        chosen.append(_match_dict(rules[idx], score, "semantic"))
        remaining -= 1

    return chosen


def format_matches(matches):
    if not matches:
        return ""
    parts = []
    for m in matches:
        parts.append(
            f"{m['id']} - {m['title']}: {m['text']}"
        )
    return "\n\n".join(parts)


def pkl_missing_message(path=PKL_PATH):
    return (
        f"ERROR: {path} not found. From the project root run: "
        f"python setup_data.py"
    )


if __name__ == "__main__":
    # Tiny in-memory ID-matching check (no MiniLM / pkl required).
    fake_rules = [
        {"id": "AC-2", "title": "Account Management", "text": "Manage accounts."},
        {"id": "AC-2(1)", "title": "Automated Account Management", "text": "Automate."},
        {"id": "AC-20", "title": "Use of External Systems", "text": "External."},
        {"id": "ia-2", "title": "Identification and Authentication", "text": "MFA."},
    ]
    fake_store = {
        "rules": fake_rules,
        "embeddings": np.zeros((len(fake_rules), 8), dtype=np.float32),
        "index_by_id": {
            canonicalize_control_id(r["id"]): i for i, r in enumerate(fake_rules)
        },
    }

    class DummyModel:
        def encode(self, _q):
            return np.zeros(8, dtype=np.float32)

    hits = retrieve("What does AC-2 require?", k=4, min_score=0.99, store=fake_store, model=DummyModel())
    ids = [h["id"] for h in hits]
    assert "AC-2" in ids, ids
    assert "AC-2(1)" in ids, ids
    assert "AC-20" not in ids, ids
    hits2 = retrieve("explain ac-2.1", k=4, min_score=0.99, store=fake_store, model=DummyModel())
    ids2 = [h["id"] for h in hits2]
    assert "AC-2(1)" in ids2 and "AC-2" in ids2, ids2
    print("retrieve.py ID-matching self-check passed:", ids, ids2)
