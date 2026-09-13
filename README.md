# CountGPT

A **local learning tool** for the ISSO / compliance side of cybersecurity: NIST SP 800-53, RMF/ATO paperwork, POA&Ms, and SSP control implementation statements.

I built this to *learn* the domain — not to ship an official authorization product. Outputs are drafts for study and practice. They are **not** assessor-validated and must never be treated as an ATO decision.

**How it was built:** I used AI to help implement the code. My job was the compliance design (what to retrieve, how POA&M/SSP drafts should look, what beginners need explained), debugging the pipeline, and checking answers against public RMF/FedRAMP/DoD-style guidance.

## One-command start

This is a **local** site. You do not need a public domain, reverse proxy, or hosting. After start, open [http://127.0.0.1:7860](http://127.0.0.1:7860) on the same machine.

**What is in this repo:** the FastAPI UI, NIST retrieval code, and (after first setup) MiniLM embeddings of the public 800-53 catalog.

**What is not embedded:** Llama 3.1 8B weights (~4.9 GB). Those stay in [Ollama](https://ollama.com) as a service — either a host install that `./start.sh` talks to, or the `ollama` service in Compose. This is not a single fat binary.

### Option A — `./start.sh` (WSL / Linux / macOS)

```bash
./start.sh
```

Creates/activates `venv`, runs `setup_data.py` if `rules_with_embeddings.pkl` is missing, finds Ollama (including WSL → Windows via `/etc/resolv.conf`), pulls `llama3.1:8b` when the `ollama` CLI is available, then serves the UI.

Windows PowerShell (this project’s venv is usually WSL):

```powershell
.\start.ps1
```

`start.ps1` prefers `wsl -e bash start.sh`. Reload while editing: `START_RELOAD=1 ./start.sh`.

### Option B — Docker Compose

Needs roughly **8–16 GB RAM** and **~10+ GB disk** (8B model + embeddings + image).

```bash
docker compose up --build
```

First run waits for Ollama, builds the pickle if needed, and pulls `llama3.1:8b`. Manual equivalent:

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

Then open [http://127.0.0.1:7860](http://127.0.0.1:7860).

## What you get

Three pages in one local app:

| Page | URL | Purpose |
| --- | --- | --- |
| **Guide** | `/guide` | Plain-English chapters + searchable glossary (SSP vs POA&M, roles, ACAS vs STIG, …) |
| **Chat** | `/` | Ask NIST / process questions; grounded answers cite retrieved controls. Chat history is saved in this browser only (`localStorage`) — not on the server. |
| **Workbench** | `/workbench` | Structured POA&M and SSP drafts, field help, fictional practice scenarios |

Learning loop: read the Guide → ask Chat → load a practice scenario in Workbench → compare to “what good looks like.”

### What’s new / sophistication

- **Redesigned UI + chat history on this device.** Slimmer Chat / Workbench / Guide shell, conversation-first Chat, and Sources in a drawer instead of a permanent side panel. Previous chats stay in the browser (`localStorage`) so you can reopen them after a reload. They are labeled **Saved on this device** and are not uploaded or stored on the server (the `/api/chat` call still sends only the usual short history window for the model).
- **Citations you can check.** Chat and Workbench list the retrieved NIST controls with ID, title, score/source, and a short quote of the rule text. Inline chips such as `[AC-2]` jump to that card. If retrieval is empty or only weakly similar, the UI says so — no fake citations.
- **MissionTracker walkthrough.** A fictional contractor DoD web app story in the Guide: roles, Monday ACAS High finding, what gets written, later SAR / AO / Continuous Monitoring, and a table of “real-life artifact → where it lives in CountGPT.”
- **ACAS / CSV → POA&M rows.** On the Workbench POA&M form, paste scan lines or upload a simple CSV. The parser is a best-effort learning aid: it maps plugin, severity, host, and synopsis when they are present, never invents IDs or dates, and still waits for you to press Generate.
- **Retrieval evals.** `evals/retrieval_cases.json` plus `python evals/run_retrieval_eval.py` score the index (hit-rate / precision-at-k), not the model’s prose.

## Manual start (same pieces, by hand)

**Requirements:** Python 3.10–3.12, [Ollama](https://ollama.com), disk for MiniLM + `llama3.1:8b`. Prefer `./start.sh` unless you want each step explicit.

```bash
cd CountGPT
python -m venv venv
# Windows:  venv\Scripts\activate
# WSL/macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python setup_data.py          # download NIST catalog → extract → embed
ollama pull llama3.1:8b

uvicorn app:app --reload --host 0.0.0.0 --port 7860
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860), then try `/guide` and `/workbench`.

Optional: `python chat_gradio.py` (legacy Gradio), `python ask_chatbot.py` (CLI).

### WSL + Ollama on Windows

`./start.sh` sets this automatically. If you start uvicorn yourself and the app runs in WSL with Ollama on Windows, point at the Windows host first:

```bash
export OLLAMA_HOST=http://$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}'):11434
uvicorn app:app --reload --host 0.0.0.0 --port 7860
```

`GET /api/health` shows whether the NIST store loaded and whether Ollama is reachable.  
`COUNTGPT_DRY_RUN=1` skips the model call (UI checks without Llama).

### Checks

```bash
bash -n start.sh
python -m unittest test_launch.py
python setup_data.py --check
python retrieve.py
python -m unittest test_countgpt.py test_app.py
python evals/run_retrieval_eval.py --dry-run
python evals/run_retrieval_eval.py --fixture
python evals/run_retrieval_eval.py          # real pickle; skips if missing
python scripts/validate_training_data.py    # SFT JSONL parse + category floors
python -m unittest test_training_data.py
```

The eval suite loads `evals/retrieval_cases.json` (≥20 queries with acceptable control IDs). It scores **retrieval only** — whether the right NIST IDs come back — not the LLM write-up. If `rules_with_embeddings.pkl` is absent it prints a skip message and exits 0. A completed run fails (exit 1) when hit-rate falls below the `min_hit_rate` in that file (default **0.70**).

Regenerable data (`nist_data.json`, `clean_rules.json`, `rules_with_embeddings.pkl`) is gitignored and created by `setup_data.py`.

## What's under the hood

1. **RAG over NIST SP 800-53 Rev 5** — official OSCAL catalog → cleaned controls → MiniLM embeddings → hybrid exact-ID + semantic retrieve → Llama 3.1 8B via Ollama, with draft disclaimers and source export.
2. **Learning UI** — Guide glossary, teacher-style chat routing, Workbench tips (`static/field-help.json`), fictional scenarios (`static/scenarios.json`).
3. **Optional QLoRA** — `training_data.jsonl` has **300** instruction/output pairs (POA&M, SSP statements, RMF Q&A, SOC triage, STIG vs scan). Fine-tune with Unsloth is still optional and **not wired into the HTML UI** (Chat/Workbench keep using Ollama `llama3.1:8b` + RAG). Needs an NVIDIA GPU + CUDA:

```bash
pip install -r requirements-finetune.txt
python scripts/validate_training_data.py   # confirm JSONL before spending GPU time
python finetune.py                         # writes countgpt_model/ (gitignored)
python test_finetuned.py
```

`finetune.py` loads Llama 3.1 8B 4-bit, attaches LoRA (`r=16`), and runs 3 epochs at batch size 1 with gradient accumulation 4. A few hundred short examples is still a small job on a single modern GPU (often tens of minutes, not a multi-day run), but it will not start on CPU-only. Do not commit `countgpt_model/` or `training_output/`.

To rebuild the JSONL from the example modules (after editing `scripts/sft_*.py`):

```bash
python scripts/build_training_data.py
python scripts/validate_training_data.py
```

**Stack:** Python 3.12, sentence-transformers, NumPy retrieval, Ollama, FastAPI + vanilla HTML/CSS/JS, optional Gradio, WSL2 on Windows.

## Honest limitations

- Practice scenarios and drafts are for learning; not eMASS submissions.
- The SFT file is now hundreds of public FedRAMP/DoD/NIST-style examples with placeholders — still small versus a production corpus, and LoRA is not auto-loaded by the HTML UI.
- Fine-tuned weights are not in the chat path yet (base Llama + RAG).
- No auth / multi-user hosting yet (static UI + `/api` can sit behind a reverse proxy later).

## Why I built this

I wanted hands-on ISSO-style work — reading real 800-53 text, drafting POA&Ms and SSP statements — instead of only reading about RMF. A tool that must retrieve real control language forces you to notice when an answer is wrong.
