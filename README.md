# CountGPT

A locally run cybersecurity compliance assistant I'm building to learn the RMF/ATO process (POA\&Ms, SSPs, control implementation). This is still a work in progress and is not polished or finished. It's a learning project focused on the ISSO/compliance side of cybersecurity. It uses two different AI techniques: retrieval augmented generation (RAG) for factual grounding, and QLoRA fine tuning for domain specific writing style.

**Note on how this was built:** I used AI to help me program and implement this project. My focus was on the compliance domain design (what the RAG dataset should contain, what the fine tuning examples needed to teach, how to structure POA\&M/SSP style outputs), debugging the pipeline when it broke, and checking whether the results actually made sense against real RMF/FedRAMP/DoD guidance. This project is mainly here to strengthen my knowledge in different areas of cybersecurity.

## Quick start (reproducible setup)

**Requirements:** Python 3.10–3.12, [Ollama](https://ollama.com), and enough disk for the MiniLM model + Llama 3.1 8B.

```bash
# 1. Clone and enter the repo
cd CountGPT

# 2. Create and activate a virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / WSL / macOS:
source venv/bin/activate

# 3. Install Python deps
pip install -r requirements.txt

# 4. Build local NIST 800-53 data (download → extract → embed)
python setup_data.py

# 5. Pull the chat model (once)
ollama pull llama3.1:8b

# 6. Run the HTML chat UI
uvicorn app:app --reload --host 0.0.0.0 --port 7860
# or: python app.py
# or: python chat_website.py

# Optional: legacy Gradio UI
# python chat_gradio.py

# Optional: one-shot CLI
# python ask_chatbot.py
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860). The site is a ChatGPT-style page: chat transcript, retrieved NIST control sources (desktop sidebar, collapsible on mobile), a persistent **draft / not assessor-validated** banner, and Markdown/CSV export of the last answer plus sources. Chat starter chips include beginner questions (`What is an SSP?`, `SSP vs POA&M?`). A `/?q=...` query prefills the composer — the Guide uses this for “Try in Chat” links.

The **Guide** at [http://127.0.0.1:7860/guide](http://127.0.0.1:7860/guide) is a plain-English learning page (Chat | Workbench | Guide in the header). It explains what CountGPT is, NIST SP 800-53, RMF/ATO at a high level, how an SSP / POA\&M / SAR connect, ISSO/ISSM/AO roles, common High/Moderate/Low fix windows, and ACAS vs STIG. A searchable glossary defines the same terms. This is a study aid, not official ATO authority.

The **Workbench** at [http://127.0.0.1:7860/workbench](http://127.0.0.1:7860/workbench) is a structured POA\&M / SSP form. Example POA\&M fields: finding text, High/Moderate/Low (30/90/180-day timelines), system name, POC/ISSO, detector source (e.g. ACAS/Nessus), discovery date, optional control ID (`AC-2`), vendor dependency, and status. Templates prefill High/Moderate/Low or a False Positive / Risk Adjustment starter. SSP mode takes a control ID plus system context and drafts an implementation statement with placeholders. Generate uses the same NIST retrieval + drafting prompts as chat; export downloads the current draft, sources, and disclaimer as Markdown or CSV. The model is instructed not to invent plugin IDs, dates, or tools you did not provide.

### Ollama host (WSL / remote)

The app talks to Ollama at `OLLAMA_HOST` (default `http://127.0.0.1:11434`). If you run CountGPT in WSL and Ollama on Windows, point it at the Windows host IP:

```bash
# In WSL, the Windows host is often in /etc/resolv.conf
export OLLAMA_HOST=http://$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}'):11434
uvicorn app:app --reload --host 0.0.0.0 --port 7860
```

On the Windows side, Ollama must listen beyond localhost (for example set `OLLAMA_HOST=0.0.0.0` in the Windows environment, then restart Ollama). `GET /api/health` reports whether the store loaded and whether Ollama is reachable.

`COUNTGPT_DRY_RUN=1` skips the model call and returns a short answer from retrieved controls — useful for UI checks when Llama is not pulled yet.

### Future domain / reverse proxy

The HTML UI is static files plus `/api/*`. Putting `uvicorn` (or gunicorn + uvicorn workers) behind Caddy/nginx on a domain is enough; no separate frontend build. Auth is not included yet.

Useful checks:

```bash
python setup_data.py --check    # verify artifacts + Ollama on PATH
python setup_data.py --force    # rebuild download/extract/embeddings
python retrieve.py              # ID-matching self-check (no GPU needed)
python -m unittest test_countgpt.py test_app.py
```

Regenerable files (`nist_data.json`, `clean_rules.json`, `rules_with_embeddings.pkl`) are gitignored and created by `setup_data.py`.

### Optional: QLoRA fine-tuning

Needs a CUDA GPU. This path is separate from the chat UI today.

```bash
pip install -r requirements-finetune.txt
python finetune.py              # reads training_data.jsonl → countgpt_model/
python test_finetuned.py        # smoke-test the adapter
```

## Why I built this

I wanted to get hands on with the kind of work an ISSO or compliance focused cybersecurity role actually involves, like reading and applying NIST 800-53 controls, drafting POA\&Ms, and writing SSP control implementation statements, instead of just reading about RMF in the abstract. Building a tool that has to retrieve and reason over real control text forced me to actually understand the material well enough to know when the output was right or wrong.

## Tech stack

Python 3.12, sentence-transformers (`all-MiniLM-L6-v2` embeddings), custom NumPy cosine retrieval over a pickled index (hybrid exact control-ID + semantic search), Ollama running Llama 3.1 8B locally, FastAPI + a vanilla HTML/CSS/JS chat UI (Gradio kept as an optional legacy UI), Unsloth for QLoRA fine tuning, PyTorch (CUDA), and WSL2 (Ubuntu on Windows).

## What's Built

### 1. RAG pipeline

I download the real, official NIST 800-53 Rev 5 control catalog (public NIST/OSCAL source), which is about 1,196 controls and enhancements. Then a custom recursive parser can extract clean control text from the deeply nested source data. Then I generate 384 dimension semantic embeddings for every control. For retrieval, it converts a plain English question into an embedding, compares it against all the stored control embeddings, and returns the top matches (plus exact ID hits when the user names a control). Those retrieved controls get passed as grounded context to a locally running Llama 3.1 8B model, which generates a cited, fact grounded answer. The HTML UI shows a persistent draft disclaimer, a sources side panel (control IDs, similarity scores, titles/text), Markdown/CSV export of the last answer plus retrieved controls, a `/guide` learning page with a searchable glossary (`GET /api/glossary`, `GET /api/guide`), and a `/workbench` page for structured POA\&M and SSP drafts (`POST /api/poam`, `POST /api/ssp`). Teacher-style chat questions (what is an SSP, SSP vs POA\&M) use an explain prompt so answers stay pedagogical and do not invent policy.

### 2. Fine tuning pipeline (QLoRA on Llama 3.1 8B)

I built a 25 example instruction tuning dataset (`training_data.jsonl`), grounded in real, sourced public reference material, including:

* FedRAMP's official POA\&M guidance (remediation timelines by severity, vendor dependency handling, false positive/risk adjustment documentation)
* DoD RMF process specifics like eMASS as the system of record, ISSO/ISSM role distinctions, and ATO authorization rules
* ACAS/Nessus as the DoD mandated scanning tool, and the difference between STIGs and vulnerability scans

The dataset covers three categories: POA\&M drafting, SSP control implementation statements (AC-2, AU-2, IA-2, SC-7, CM-6, IR-6, RA-5, CP-9), and SOC style alert triage reasoning. I ran a full QLoRA fine tuning job on my own hardware (RTX 3060 Ti, 8GB VRAM) using Unsloth, then loaded and tested the fine tuned model to confirm the pipeline runs end to end.

## Debugging Notes

While building the parser, I ran into an issue where it only captured 324 of the 1,196 controls. It seemed that the source data had nesting levels I wasn't accounting for (sub groups and control enhancements go deeper than I expected), so I made it so the parser can recurse through all the nesting levels to actually capture everything.

## Current Limitations

25 training examples isn't really enough to reliably shift the model's behavior. My test output showed a reasonable POA\&M structure but it didn't consistently pick up the trained in specifics, like exact timelines or eMASS terminology. I think this is expected and not really a failure, it probably needs 300+ examples to have a meaningful effect and be a strong candidate.

The fine tuned model also isn't wired into the chat UI yet, so right now it's only running on the base Llama 3.1 model through RAG. And the data source is still limited to the public NIST 800-53 controls.

## The Vision

I want to expand the fine tuning dataset toward 300+ examples to get better answers, get the fine tuned model actually wired into the chat UI, and possibly move this to a publicly hosted site down the line (static UI + `/api` behind a reverse proxy).
