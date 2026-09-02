# CountGPT

A locally run cybersecurity compliance assistant I'm building to learn the RMF/ATO process (POA\&Ms, SSPs, control implementation). This is still a work in progress and is not polished or finished. It's a learning project focused on the ISSO/compliance side of cybersecurity. It uses two different AI techniques: retrieval augmented generation (RAG) for factual grounding, and QLoRA fine tuning for domain specific writing style.

**Note on how this was built:** I used AI to help me program and implement this project. My focus was on the compliance domain design (what the RAG dataset should contain, what the fine tuning examples needed to teach, how to structure POA\&M/SSP style outputs), debugging the pipeline when it broke, and checking whether the results actually made sense against real RMF/FedRAMP/DoD guidance. This project is mainly here to strengthen my knowledge in different areas of cybersecurity.

## Why I built this

I wanted to get hands on with the kind of work an ISSO or compliance focused cybersecurity role actually involves, like reading and applying NIST 800-53 controls, drafting POA\&Ms, and writing SSP control implementation statements, instead of just reading about RMF in the abstract. Building a tool that has to retrieve and reason over real control text forced me to actually understand the material well enough to know when the output was right or wrong.

## Tech stack

Python 3.12, sentence-transformers (`all-MiniLM-L6-v2` embeddings), a custom built vector search (ChromaDB style), Ollama running Llama 3.1 8B locally, Unsloth for QLoRA fine tuning, PyTorch (CUDA), Gradio for the chat interface, and WSL2 (Ubuntu on Windows).

## What's Built

### 1\. RAG pipeline

I download the real, official NIST 800-53 Rev 5 control catalog (public NIST/OSCAL source), which is about 1,196 controls and enhancements. Then a custom recursive parser can extract clean control text from the deeply nested source data. Then I generate 384 dimension semantic embeddings for every control. For retrieval, it converts a plain English question into an embedding, compares it against all the stored control embeddings, and returns the top matches. Those retrieved controls get passed as grounded context to a locally running Llama 3.1 8B model, which generates a cited, fact grounded answer. This is all wrapped in a working Gradio chat interface so it runs as a local web.

### 2\. Fine tuning pipeline (QLoRA on Llama 3.1 8B)

I built a 25 example instruction tuning dataset, grounded in real, sourced public reference material, including:

* FedRAMP's official POA\&M guidance (remediation timelines by severity, vendor dependency handling, false positive/risk adjustment documentation)
* DoD RMF process specifics like eMASS as the system of record, ISSO/ISSM role distinctions, and ATO authorization rules
* ACAS/Nessus as the DoD mandated scanning tool, and the difference between STIGs and vulnerability scans

The dataset covers three categories: POA\&M drafting, SSP control implementation statements (AC-2, AU-2, IA-2, SC-7, CM-6, IR-6, RA-5, CP-9), and SOC style alert triage reasoning. I ran a full QLoRA fine tuning job on my own hardware (RTX 3060 Ti, 8GB VRAM) using Unsloth, then loaded and tested the fine tuned model to confirm the pipeline runs end to end.

## Debugging Notes

While building the parser, I ran into an issue where it only captured 324 of the 1,196 controls. It seemed that the source data had nesting levels I wasn't accounting for (sub groups and control enhancements go deeper than I expected), so I made it so the parser can recurse through all the nesting levels to actually capture everything.

## Current Limitations

25 training examples isn't really enough to reliably shift the model's behavior. My test output showed a reasonable POA\&M structure but it didn't consistently pick up the trained in specifics, like exact timelines or eMASS terminology. I think this is expected and not really a failure, it probably needs 300+ examples to have a meaningful effect and be a strong candidate.

The fine tuned model also isn't wired into the Gradio front end yet, so right now it's only running on the base Llama 3.1 model through RAG. And the data source is still limited to the public NIST 800-53 controls.

## The Vision

I want to expand the fine tuning dataset toward 300+ examples to get better answers, get the fine tuned model actually wired into the Gradio front end, and possibly move this to a publicly hosted site down the line.

