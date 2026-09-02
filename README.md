# CountGPT

A locally-run cybersecurity compliance assistant, built to learn the RMF/ATO process (POA\&Ms, SSPs, control implementation) from the ground up by actually building a tool around it, not just reading about it.

This is a work in progress. It's not polished, and it's not trying to be a finished product — it's a learning project focused on the ISSO/compliance side of cybersecurity, combining two AI techniques: retrieval-augmented generation (RAG) for factual grounding, and QLoRA fine-tuning for domain-specific writing style.

**Note on how this was built:** I used AI coding assistants heavily for implementation. My focus was on the compliance domain design (what the RAG dataset should contain, what the fine-tuning examples needed to teach, how to structure POA\&M/SSP-style outputs), debugging the pipeline when it broke, and evaluating whether the results actually made sense against real RMF/FedRAMP/DoD guidance. I'm not claiming to have hand-written every line — I'm claiming to understand what the project does and why it's built the way it is.

## Why I built this

I wanted to get hands-on with the kind of work an ISSO or compliance-focused cybersecurity role actually involves — reading and applying NIST 800-53 controls, drafting POA\&Ms, writing SSP control implementation statements — rather than just reading about RMF in the abstract. Building a tool that has to actually retrieve and reason over real control text forced me to understand the material well enough to know when the output was right or wrong.

## Tech stack

* Python 3.12
* sentence-transformers (`all-MiniLM-L6-v2` embeddings)
* Custom-built vector search (ChromaDB-style)
* Ollama running Llama 3.1 8B locally
* Unsloth (QLoRA fine-tuning)
* PyTorch (CUDA)
* Gradio (chat interface)
* WSL2 (Ubuntu on Windows)

## What's built and working

### 1\. RAG pipeline

* Downloads the real, official NIST 800-53 Rev 5 control catalog (public NIST/OSCAL source) — \~1,196 controls and enhancements
* Custom recursive parser extracts clean control text from deeply nested source data
* Generates 384-dimension semantic embeddings for every control
* Similarity-based retrieval: converts a plain-English question into an embedding, compares against stored control embeddings, returns the top-K most relevant matches
* Passes retrieved control text as grounded context to a locally-running Llama 3.1 8B model, which generates a cited, fact-grounded answer
* Wrapped in a working Gradio chat interface (local web app)

### 2\. Fine-tuning pipeline (QLoRA on Llama 3.1 8B)

* Built a 25-example instruction-tuning dataset, grounded in real, sourced public reference material:

  * FedRAMP's official POA\&M guidance (remediation timelines by severity, vendor dependency handling, false positive/risk adjustment documentation)
  * DoD RMF process specifics: eMASS as the system of record, ISSO/ISSM role distinctions, ATO authorization rules
  * ACAS/Nessus as the DoD-mandated scanning tool; STIG vs. vulnerability-scan distinction
* Dataset spans three categories: POA\&M drafting, SSP control implementation statements (AC-2, AU-2, IA-2, SC-7, CM-6, IR-6, RA-5, CP-9), and SOC-style alert triage reasoning
* Ran a full QLoRA fine-tuning job on local consumer hardware (RTX 3060 Ti, 8GB VRAM) using Unsloth
* Loaded and tested the fine-tuned model; confirmed the full pipeline runs end-to-end

## Debugging notes worth mentioning

* **Parsing bug:** the initial control parser only captured 324 of 1,196 controls. Root cause was missed nesting levels — sub-groups and control enhancements were structured deeper than expected in the source data. Fixed by making the parser recurse through all nesting levels.
* **GPU/environment failure:** hit a multi-layered Windows/GPU compatibility issue — a CPU-only PyTorch install, a PyTorch/torchao version mismatch, and a hard Triton/Windows incompatibility causing silent crashes. Diagnosed via Windows exit codes, resolved by migrating the fine-tuning environment to WSL2 (including recovering from a lost sudo password along the way).

## Honest current limitations

* 25 training examples isn't enough to reliably shift model behavior. Test output showed reasonable POA\&M structure but didn't consistently reflect trained-in specifics (exact timelines, eMASS terminology). This is expected, not a failure — a meaningful fine-tuning effect likely needs 300+ examples.
* The fine-tuned model isn't yet wired into the Gradio front-end — it currently runs on base Llama 3.1 via RAG only.
* Data source scope is limited to public NIST 800-53 controls. STIGs and live CVE feeds are planned but not built yet.

## What's next

* Expand the fine-tuning dataset toward 300+ examples
* Wire the fine-tuned model into the Gradio front-end
* Add STIG references and live CVE feed integration

