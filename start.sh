#!/usr/bin/env bash
# CountGPT — one-command local start (WSL / Linux / macOS).
# Usage:
#   ./start.sh
#   START_RELOAD=1 ./start.sh    # uvicorn --reload while hacking
# No public domain or hosting. Open http://127.0.0.1:7860 on this machine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MODEL="${COUNTGPT_MODEL:-llama3.1:8b}"
APP_HOST="${COUNTGPT_HOST:-0.0.0.0}"
APP_PORT="${COUNTGPT_PORT:-7860}"
LOCAL_URL="http://127.0.0.1:${APP_PORT}"

banner() {
  echo
  echo "============================================================"
  echo "  $*"
  echo "============================================================"
}

warn() {
  echo "WARNING: $*" >&2
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

is_wsl() {
  [[ -r /proc/version ]] && grep -qi microsoft /proc/version
}

# GET $1/api/tags — 0 if Ollama answers.
probe_ollama() {
  local host="$1"
  python - "$host" <<'PY'
import sys
import urllib.error
import urllib.request

host = sys.argv[1].rstrip("/")
try:
    with urllib.request.urlopen(host + "/api/tags", timeout=3) as resp:
        sys.exit(0 if getattr(resp, "status", 200) == 200 else 1)
except (urllib.error.URLError, TimeoutError, OSError):
    sys.exit(1)
PY
}

# 0 if $MODEL is listed at $1.
ollama_has_model() {
  local host="$1"
  python - "$host" "$MODEL" <<'PY'
import json
import sys
import urllib.error
import urllib.request

host = sys.argv[1].rstrip("/")
wanted = sys.argv[2]
try:
    with urllib.request.urlopen(host + "/api/tags", timeout=5) as resp:
        data = json.load(resp)
except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
    sys.exit(1)

ok = False
for item in (data.get("models") or []):
    name = item.get("name") or item.get("model") or ""
    if name == wanted or name.startswith(wanted):
        ok = True
        break
sys.exit(0 if ok else 1)
PY
}

pick_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
  elif command -v python >/dev/null 2>&1; then
    echo python
  else
    die "Python 3.10–3.12 is required. Install python3 and re-run ./start.sh"
  fi
}

# --- venv -------------------------------------------------------------------
PY_SYS="$(pick_python)"

if [[ -d venv ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
  echo "Using existing venv ($(command -v python))"
else
  echo "Creating venv with ${PY_SYS}..."
  "$PY_SYS" -m venv venv
  # shellcheck disable=SC1091
  source venv/bin/activate
  echo "Installing requirements (first run can take a few minutes)..."
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not in venv — installing requirements.txt..."
  python -m pip install -r requirements.txt
fi

# --- RAG data ---------------------------------------------------------------
if [[ ! -f rules_with_embeddings.pkl ]]; then
  banner "Building local NIST data (rules_with_embeddings.pkl is missing)"
  echo "This downloads the public 800-53 catalog and embeds it with MiniLM."
  echo "Needs network once. Llama weights are NOT downloaded here."
  if ! python setup_data.py; then
    echo
    echo "Could not create rules_with_embeddings.pkl."
    echo "Fix the error above, then from the repo root run:"
    echo "  source venv/bin/activate"
    echo "  python setup_data.py"
    exit 1
  fi
fi

# --- Ollama host ------------------------------------------------------------
# Prefer an explicit OLLAMA_HOST, then localhost, then WSL → Windows host.
if [[ -n "${OLLAMA_HOST:-}" ]]; then
  echo "Using OLLAMA_HOST from the environment: ${OLLAMA_HOST}"
else
  if probe_ollama "http://127.0.0.1:11434"; then
    export OLLAMA_HOST="http://127.0.0.1:11434"
    echo "Ollama is reachable on localhost:11434"
  elif is_wsl; then
    WSL_DNS="$(grep nameserver /etc/resolv.conf | awk '{print $2; exit}')"
    if [[ -z "${WSL_DNS}" ]]; then
      warn "WSL detected but no nameserver in /etc/resolv.conf"
      export OLLAMA_HOST="http://127.0.0.1:11434"
    else
      export OLLAMA_HOST="http://${WSL_DNS}:11434"
      echo "WSL detected — probing Windows Ollama at ${OLLAMA_HOST}"
      if probe_ollama "${OLLAMA_HOST}"; then
        echo "Ollama is reachable via the WSL nameserver host"
      else
        warn "No Ollama at ${OLLAMA_HOST}. Start Ollama on Windows and keep this OLLAMA_HOST."
      fi
    fi
  else
    export OLLAMA_HOST="http://127.0.0.1:11434"
    warn "Ollama is not answering at ${OLLAMA_HOST}. Start it, then refresh /api/health."
  fi
fi

# --- Model ------------------------------------------------------------------
if probe_ollama "${OLLAMA_HOST}"; then
  if ollama_has_model "${OLLAMA_HOST}"; then
    echo "Ollama model ${MODEL} is present"
  else
    echo "Ollama is up but ${MODEL} is not installed yet."
    if command -v ollama >/dev/null 2>&1; then
      echo "Pulling ${MODEL} (several GB; needs disk + RAM)..."
      ollama pull "${MODEL}"
    else
      echo
      echo "install/start Ollama on Windows and pull llama3.1:8b"
      echo "  https://ollama.com"
      echo "  ollama pull llama3.1:8b"
      echo "The site will still start; Chat/Workbench need the model."
      echo
    fi
  fi
else
  if is_wsl; then
    echo
    echo "install/start Ollama on Windows and pull llama3.1:8b"
    echo "  https://ollama.com   then:  ollama pull llama3.1:8b"
    echo "WSL should use:  export OLLAMA_HOST=${OLLAMA_HOST}"
    echo
  else
    warn "Cannot reach Ollama at ${OLLAMA_HOST}."
    echo "Install Ollama (https://ollama.com), run it, then:  ollama pull llama3.1:8b"
  fi
fi

# --- Run --------------------------------------------------------------------
# Avoid empty-array + set -u (macOS ships Bash 3.2).
banner "CountGPT  →  ${LOCAL_URL}"
echo "  Guide:      ${LOCAL_URL}/guide"
echo "  Chat:       ${LOCAL_URL}/"
echo "  Workbench:  ${LOCAL_URL}/workbench"
echo "  Health:     ${LOCAL_URL}/api/health"
echo
echo "Local only — no public domain. Stop with Ctrl+C."
echo "============================================================"
echo

if [[ "${START_RELOAD:-}" == "1" ]]; then
  echo "START_RELOAD=1 — uvicorn will reload on file changes"
  exec uvicorn app:app --host "${APP_HOST}" --port "${APP_PORT}" --reload
fi
exec uvicorn app:app --host "${APP_HOST}" --port "${APP_PORT}"
