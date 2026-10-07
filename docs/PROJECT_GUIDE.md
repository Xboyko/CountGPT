# CountGPT project guide

This guide explains what is in the repository, what each file does, and how the pieces work together.

## The overall structure

CountGPT is a Python web app with three browser pages. It uses an existing language model, Llama 3.1 8B, plus search over a local NIST catalog. The optional training code adapts that existing model for drafting; it does not build a language model from scratch.

A normal chat request follows this path:

```text
Browser: static/index.html + static/app.js
    |
    | sends the question to /api/chat
    v
app.py                    Receives and checks the request
    |
    v
countgpt.py               Chooses the kind of answer and builds the prompt
    |
    +--> retrieve.py      Finds relevant NIST controls
    |
    +--> Ollama           Runs Llama for lookups, explanations, and fallback drafts
    |    or
    +--> lora_infer.py    Runs the optional local adapter for drafting
    |
    v
app.py returns the answer and source information to the browser
```

The Guide is mostly written educational content. Its chapters do not require the language model to generate them. The Workbench uses forms to collect information before sending a drafting request to the backend.

There are two different uses of AI here:

- **Search:** MiniLM turns text into lists of numbers called embeddings. Similar meanings tend to produce similar numbers, which lets the app find relevant controls even when the wording differs.
- **Writing:** Llama uses the question, instructions, and retrieved text to generate an answer.

The search data and the fine-tuning examples serve different purposes. The NIST catalog supplies reference material at question time. The training examples teach a style of response during optional training.

## Main application files

| File | What it does |
| --- | --- |
| `app.py` | The web server entry point. FastAPI serves the pages and handles requests for chat, drafting, finding imports, exports, help content, and health status. It checks incoming fields and passes the work to the other Python modules. |
| `countgpt.py` | The main application logic. It distinguishes explanations, control lookups, and drafting requests; prepares prompts; calls search and the model; attaches source details; and formats Markdown/CSV exports. |
| `retrieve.py` | Searches the local NIST index. It combines exact control-ID matching with meaning-based search, ranks matches, and filters weak results. It also has a small self-check you can run directly. |
| `lora_infer.py` | Loads the optional trained adapter when needed and generates drafts with it. Checks the adapter, CUDA, and loading errors so the main app can fall back to Ollama. |
| `parse_findings.py` | Converts pasted finding text or CSV content into fields the Workbench can use, such as severity, host, plugin ID, and finding description. It uses parsing rules, not a language model. |
| `setup_data.py` | Runs the download, extraction, and embedding steps in order. Reuses existing files by default; `--force` rebuilds them and `--check` checks existing artifacts. |
| `finetune.py` | Runs the optional training job. Loads a quantized Llama model, attaches LoRA adapters, trains on the example dataset, and saves the adapter/tokenizer. |
| `training_data.jsonl` | The 300 examples read by the training job. Each line is a separate JSON object containing an instruction and an example response. |

## Browser files: static/

HTML defines a page's structure and content. CSS defines its appearance. JavaScript makes it interactive and calls the Python API. JSON stores structured content that the pages can load.

| File | What it does |
| --- | --- |
| `static/index.html` | The Chat page structure: messages, input, saved-chat sidebar, and source/export controls. |
| `static/app.js` | Makes Chat work: sends questions, displays answers, checks health, and connects history, sources, and export actions. |
| `static/history.js` | Saves and restores conversations using the browser's local storage. There is no server-side chat-history database. |
| `static/sources.js` | Shared source display code for the UI. Builds source cards, citation links, and retrieval-status information. |
| `static/guide.html` | The written learning guide, including the MissionTracker walkthrough. Most chapter text lives here. |
| `static/guide.js` | Adds glossary search, navigation highlighting, health status, and practice-scenario links to the Guide. |
| `static/guide-meta.json` | Guide metadata: chapter IDs, titles, and suggested questions to try in Chat. It is separate from the chapter text. |
| `static/glossary.json` | Definitions of the terms used throughout the learning material. |
| `static/workbench.html` | The Workbench page structure, including the POA&M and SSP forms. |
| `static/workbench.js` | Handles form input, finding imports, practice scenarios, draft requests, displayed results, and exports. |
| `static/field-help.json` | Explanations and help links for individual Workbench fields. |
| `static/scenarios.json` | Fictional practice situations that fill in the Workbench forms. |
| `static/styles.css` | Shared appearance for all three pages: layout, colors, typography, buttons, and responsive behavior. |

Saving chat history in the browser does not mean a question never leaves the browser. Questions and a recent history window are sent to the Python backend to generate an answer.

## Data and training helpers: scripts/

| File | What it does |
| --- | --- |
| `scripts/__init__.py` | Marks this folder as a Python package so its modules can be imported. |
| `scripts/download_catalog.py` | Downloads the official NIST SP 800-53 Rev. 5 OSCAL catalog and saves `nist_data.json`. OSCAL is a structured format for security-control information. |
| `scripts/extract_all_rules.py` | Reads that catalog, extracts control statements, removes withdrawn or empty entries, and writes `clean_rules.json`. |
| `scripts/build_embeddings.py` | Uses MiniLM to encode the cleaned controls and saves the text plus embeddings in `rules_with_embeddings.pkl`. |
| `scripts/build_training_data.py` | Combines selected examples from the five category modules below and writes `training_data.jsonl`. Running it replaces that dataset file. |
| `scripts/sft_poam.py` | Source examples for POA&M drafting and related finding/remediation work. |
| `scripts/sft_ssp.py` | Source examples for SSP control implementation statements. |
| `scripts/sft_rmf.py` | Source examples about the Risk Management Framework and authorization process. |
| `scripts/sft_soc.py` | Source examples for security operations and alert triage. |
| `scripts/sft_stig.py` | Source examples about STIG configuration checks and vulnerability-scan findings. |
| `scripts/validate_training_data.py` | Checks the dataset's format, required fields, size, category coverage, repeated instructions, and certain concrete IDs that should be placeholders. It does not verify every answer's factual accuracy. |

SFT means supervised fine-tuning: training on example instructions paired with desired responses.

## Tests and evaluations

Tests check expected program behavior. The retrieval evaluation asks a narrower question: did search return an acceptable control for each example query?

| File | What it does |
| --- | --- |
| `tests/__init__.py` | Makes the tests importable as a package. |
| `tests/test_app.py` | Checks API responses, page/assets delivery, exports, and related UI integration. |
| `tests/test_countgpt.py` | Checks prompt routing, history handling, citations, exports, finding parsing, Workbench prompts, and retrieval-evaluation behavior. |
| `tests/test_launch.py` | Checks launcher and Docker configuration files, including shell syntax. Checks Compose when Docker is available. |
| `tests/test_lora.py` | Checks adapter configuration, prompt handling, loading, drafting routing, and fallback behavior using controlled substitutes for model operations. |
| `tests/test_training_data.py` | Checks the actual example dataset and the validator's handling of valid and invalid inputs. |
| `evals/__init__.py` | Marks the evaluation folder as a Python package. |
| `evals/retrieval_cases.json` | Example search questions, acceptable control IDs, and the evaluation's pass threshold. |
| `evals/run_retrieval_eval.py` | Runs the search evaluation and reports hit rate and precision. Can validate the cases, use a small fixed test index, or evaluate the real local index. |

A passing test suite is useful evidence that the application behaves as expected. It does not establish that generated compliance advice is correct.

## Startup, dependencies, and repository settings

| File | What it does |
| --- | --- |
| `start.sh` | Starts the app on WSL/Linux/macOS. Creates or activates the virtual environment, installs dependencies when needed, builds missing search data, checks Ollama, and launches Uvicorn. |
| `start.ps1` | Windows PowerShell launcher. Prefers WSL and otherwise uses a native Windows Python environment. |
| `requirements.txt` | Python dependencies for the app and search: HTTP requests, numerical operations, embedding models, Ollama's client, FastAPI, and Uvicorn. |
| `requirements-finetune.txt` | Adds optional training/adapter libraries, including Unsloth, Transformers, TRL, Datasets, PEFT, and Accelerate. |
| `Dockerfile` | Instructions for building the app's container image, including Python dependencies and the startup command. |
| `docker-compose.yml` | Runs two containers together: CountGPT and Ollama. Defines ports, a health check, and persistent storage for models and search data. |
| `docker/entrypoint.sh` | Container startup helper. Waits for Ollama, restores or builds search data, attempts to pull the language model if needed, then starts the server. |
| `.dockerignore` | Keeps local environments, model outputs, tests, demo assets, and other unnecessary files out of the Docker build context. |
| `.gitignore` | Keeps generated data, local model outputs, environment files, caches, and virtual environments out of Git. |
| `.gitattributes` | Keeps shell scripts on Unix-style line endings so they work in Bash. |
| `.github/workflows/launch-check.yml` | GitHub Actions workflow that checks Windows PowerShell 5.1 parsing, Bash syntax, Compose configuration, and launch tests on pushes and pull requests. It does not run the full application test suite. |
| `README.md` | The public introduction, features, and basic setup instructions. |
| `docs/PROJECT_GUIDE.md` | This file-by-file explanation. |

FastAPI handles the web API. Uvicorn is the process that runs that API and listens for browser requests. Ollama is a separate service that runs the language model.

## Demo files: docs/demo/

These files show the app without requiring someone to install it. The application itself does not load them.

| File | What it shows |
| --- | --- |
| `docs/demo/01-chat.png` | Chat page. |
| `docs/demo/02-chat-sources.png` | Chat with the source panel. |
| `docs/demo/03-guide.png` | Learning Guide. |
| `docs/demo/04-guide-missiontracker.png` | MissionTracker section of the Guide. |
| `docs/demo/05-workbench.png` | Workbench page. |
| `docs/demo/06-workbench-scenario.png` | A practice scenario in the Workbench. |
| `docs/demo/07-chat-answer.png` | An example chat answer. |
| `docs/demo/countgpt-demo.mp4` | A slideshow walkthrough of the demo pages. |

## Local files and folders that are not on GitHub

These are generated or installed locally. They are excluded from Git, but some are needed to run the app after setup.

| File or folder | What it contains |
| --- | --- |
| `nist_data.json` | The downloaded NIST catalog in its original structured form. |
| `clean_rules.json` | The extracted control IDs, titles, and statement text. |
| `rules_with_embeddings.pkl` | The search index: control text and numeric embeddings, saved in Python's pickle format. |
| `countgpt_model/` | The saved adapter and tokenizer files from optional training. Its presence alone does not mean the running app successfully loaded it. |
| `training_output/` | Training checkpoints and other outputs written by the trainer. |
| `unsloth_compiled_cache/` | Generated helper code/cache used by Unsloth. |
| `venv/` | The project's installed Python environment and packages. |
| `__pycache__/` | Python's compiled-code cache. These folders can also appear inside other folders. |
| `.git/` | Git's local history and repository metadata. |

The main Ollama Llama model is stored outside this repository in Ollama's model storage, or in the Docker volume when using Compose.

## Running the pieces yourself

Run commands from the repo root. For manual setup in WSL/Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup_data.py
ollama pull llama3.1:8b
python app.py
```

For native Windows PowerShell, activate with `venv\Scripts\Activate.ps1` instead. Use a separate environment for Windows and WSL. Ollama must be running for generation.

Useful commands with that environment active:

```bash
python setup_data.py --check                 # check saved data
python setup_data.py --force                 # download and rebuild search data
python -m unittest discover -s tests         # application tests
python evals/run_retrieval_eval.py --dry-run  # validate evaluation cases
python evals/run_retrieval_eval.py --fixture  # test using a small fixed index
python evals/run_retrieval_eval.py            # evaluate the real search index
python scripts/validate_training_data.py     # check the training examples
python scripts/build_training_data.py        # regenerate examples from source modules
```

### Settings

Set these as environment variables before starting the app. The application does not automatically load a `.env` file.

| Setting | Purpose |
| --- | --- |
| `OLLAMA_HOST` | Address of the Ollama server; normally `http://127.0.0.1:11434`. If using WSL with Ollama on Windows, `start.sh` probes localhost and Windows-host candidates. A manual launch may need the reachable Windows-host address. |
| `COUNTGPT_DRY_RUN=1` | Returns a canned answer instead of running model generation; useful for checking the UI. |
| `COUNTGPT_FORCE_OLLAMA=1` | Uses Ollama for drafting even when a local adapter is present. |
| `COUNTGPT_LORA_PATH` | Points to an adapter directory other than the default `countgpt_model/`. |
| `COUNTGPT_PKL_PATH` | Points retrieval to a different saved search index. The setup script still creates its default files in the repo root. |
| `COUNTGPT_HOST`, `COUNTGPT_PORT` | Bind address and port used by `python app.py` and `start.sh`. Defaults are `0.0.0.0` and `7860`; the default bind can accept connections from other machines if networking permits. |
| `START_RELOAD=1` | Enables automatic server reload through the launch scripts while editing code. |
| `COUNTGPT_DATA_DIR` | Storage location used by the Docker entrypoint for persistent search data. |
| `COUNTGPT_SKIP_OLLAMA_PULL=1` | Stops the Docker entrypoint from automatically pulling the Llama model. |

### Where to begin reading the code

Start with `app.py` to see the available routes. Follow `/api/chat` into `countgpt.chat_turn()`, then `generate_answer()`, then `retrieve.retrieve()`. That covers the main question-to-answer flow.

For the browser side, open `static/index.html` and `static/app.js`. For setup, start with `setup_data.py`. Leave the fine-tuning scripts for later unless you specifically want to work on training.
