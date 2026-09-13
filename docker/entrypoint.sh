#!/usr/bin/env bash
# Container entrypoint: wait for Ollama, build/restore RAG data, optional model pull.
set -euo pipefail

cd /app

DATA_DIR="${COUNTGPT_DATA_DIR:-/data}"
MODEL="${COUNTGPT_MODEL:-llama3.1:8b}"
OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
export OLLAMA_HOST
mkdir -p "${DATA_DIR}"

echo "CountGPT container starting (OLLAMA_HOST=${OLLAMA_HOST})"

wait_for_ollama() {
  local i
  echo "Waiting for Ollama at ${OLLAMA_HOST} ..."
  for i in $(seq 1 90); do
    if curl -fsS --max-time 2 "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
      echo "Ollama is up"
      return 0
    fi
    sleep 2
  done
  echo "WARNING: Ollama did not become ready. The UI will start; Chat needs Ollama." >&2
  return 1
}

restore_or_build_data() {
  local f
  for f in nist_data.json clean_rules.json rules_with_embeddings.pkl; do
    if [[ ! -e "/app/${f}" && -f "${DATA_DIR}/${f}" ]]; then
      ln -s "${DATA_DIR}/${f}" "/app/${f}"
      echo "Reusing persisted ${f} from ${DATA_DIR}"
    fi
  done

  if [[ ! -f /app/rules_with_embeddings.pkl ]]; then
    echo "rules_with_embeddings.pkl missing — running setup_data.py (first run, network + CPU)"
    python setup_data.py
  fi

  for f in nist_data.json clean_rules.json rules_with_embeddings.pkl; do
    if [[ -f "/app/${f}" && ! -f "${DATA_DIR}/${f}" ]]; then
      cp -L "/app/${f}" "${DATA_DIR}/${f}"
      echo "Persisted ${f} to ${DATA_DIR}"
    fi
  done
}

ensure_model() {
  if [[ "${COUNTGPT_SKIP_OLLAMA_PULL:-}" == "1" ]]; then
    echo "COUNTGPT_SKIP_OLLAMA_PULL=1 — not pulling ${MODEL}"
    return 0
  fi
  if ! curl -fsS --max-time 3 "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
    echo "Ollama not reachable — skip model pull. Later: docker compose exec ollama ollama pull ${MODEL}"
    return 0
  fi
  if python - "$OLLAMA_HOST" "$MODEL" <<'PY'
import json, sys, urllib.request
host, wanted = sys.argv[1].rstrip("/"), sys.argv[2]
with urllib.request.urlopen(host + "/api/tags", timeout=5) as resp:
    data = json.load(resp)
for item in data.get("models") or []:
    name = item.get("name") or item.get("model") or ""
    if name == wanted or name.startswith(wanted):
        sys.exit(0)
sys.exit(1)
PY
  then
    echo "Ollama model ${MODEL} is present"
    return 0
  fi

  echo "Pulling ${MODEL} into the ollama service (several GB). You can also run:"
  echo "  docker compose exec ollama ollama pull ${MODEL}"
  if ! curl -fsS --max-time 3600 -X POST "${OLLAMA_HOST}/api/pull" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"${MODEL}\",\"stream\":false}"; then
    echo "WARNING: automatic pull failed. Run: docker compose exec ollama ollama pull ${MODEL}" >&2
  fi
  echo
}

wait_for_ollama || true
restore_or_build_data
ensure_model

echo
echo "============================================================"
echo "  CountGPT  →  http://127.0.0.1:7860"
echo "============================================================"
echo

exec "$@"
