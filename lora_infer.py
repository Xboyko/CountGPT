"""Optional Unsloth/PEFT LoRA adapter for CountGPT drafting (not lookup).

The adapter directory is produced by ``finetune.py`` (default ``countgpt_model/``).
Load is lazy and thread-safe. Missing adapter, no CUDA, Unsloth import errors,
or a failed load all leave drafting on Ollama.
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("countgpt.lora")

APP_DIR = Path(__file__).resolve().parent
DEFAULT_ADAPTER_NAME = "countgpt_model"
MAX_SEQ_LENGTH = 2048
MAX_NEW_TOKENS = 768
ADAPTER_MARKERS = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "adapter_model.bin",
    "pytorch_model.bin",
    "model.safetensors",
)

_lock = threading.Lock()
_model: Any = None
_tokenizer: Any = None
_loaded = False
_load_failed = False
_error: str | None = None
_skip_logged = False


class LoraError(RuntimeError):
    """Raised when a draft was routed to LoRA but generation cannot run."""


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def force_ollama() -> bool:
    """COUNTGPT_FORCE_OLLAMA disables the adapter even if it is on disk."""
    return _truthy_env("COUNTGPT_FORCE_OLLAMA")


def lora_path() -> Path:
    """Adapter directory: ``COUNTGPT_LORA_PATH`` or ``countgpt_model`` next to the app."""
    raw = (os.environ.get("COUNTGPT_LORA_PATH") or "").strip()
    if raw:
        return Path(raw).expanduser()
    return APP_DIR / DEFAULT_ADAPTER_NAME


def adapter_present(path: Path | None = None) -> bool:
    """True when the adapter directory looks like a saved Unsloth/PEFT model."""
    target = path if path is not None else lora_path()
    if not target.is_dir():
        return False
    return any((target / name).is_file() for name in ADAPTER_MARKERS)


def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001 — torch may be missing in the core env
        return False


def reset_lora_state() -> None:
    """Test helper: forget a previous load attempt (does not free GPU memory)."""
    global _model, _tokenizer, _loaded, _load_failed, _error, _skip_logged
    with _lock:
        _model = None
        _tokenizer = None
        _loaded = False
        _load_failed = False
        _error = None
        _skip_logged = False


def _log(message: str, *, level: int = logging.INFO) -> None:
    LOGGER.log(level, message)
    print(message)


def lora_available() -> bool:
    """True when the next draft should try the local adapter."""
    if force_ollama() or _load_failed:
        return False
    if _loaded:
        return True
    return adapter_present() and cuda_available()


def log_skip_reason() -> None:
    """Log once why an on-disk adapter is not being used for this process."""
    global _skip_logged, _error
    if _skip_logged or _loaded:
        return
    path = lora_path()
    if force_ollama():
        message = (
            "CountGPT LoRA: COUNTGPT_FORCE_OLLAMA is set. "
            f"Drafting will use Ollama llama3.1:8b (adapter at {path} ignored)."
        )
    elif _load_failed and _error:
        message = _error
    elif not cuda_available():
        message = (
            f"CountGPT LoRA: CUDA is not available; cannot load adapter at {path}. "
            "Drafting will use Ollama llama3.1:8b."
        )
        if _error is None:
            _error = message
    elif not adapter_present(path):
        return
    else:
        message = (
            f"CountGPT LoRA: adapter at {path} will not be used. "
            "Drafting will use Ollama llama3.1:8b."
        )
    _skip_logged = True
    _log(message, level=logging.WARNING)


def lora_loaded() -> bool:
    return _loaded


def lora_error() -> str | None:
    return _error


def lora_status() -> dict[str, Any]:
    """Health payload: whether LoRA is available and whether it is in memory."""
    path = lora_path()
    present = adapter_present(path)
    cuda = cuda_available()
    forced = force_ollama()
    available = lora_available()
    return {
        "path": str(path),
        "adapter_present": present,
        "cuda_available": cuda,
        "force_ollama": forced,
        "available": available,
        "loaded": _loaded,
        "error": _error,
    }


def _import_unsloth():
    from unsloth import FastLanguageModel

    return FastLanguageModel


def _try_load_locked() -> None:
    """Load the adapter. Caller must hold ``_lock``."""
    global _model, _tokenizer, _loaded, _load_failed, _error

    if _loaded or _load_failed:
        return
    if force_ollama():
        return

    path = lora_path()
    if not adapter_present(path):
        return
    if not cuda_available():
        _error = (
            f"CountGPT LoRA: CUDA is not available; cannot load adapter at {path}. "
            "Drafting will use Ollama llama3.1:8b."
        )
        _log(_error, level=logging.WARNING)
        return

    _log(f"CountGPT LoRA: loading adapter from {path} …")
    try:
        FastLanguageModel = _import_unsloth()
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(path),
            max_seq_length=MAX_SEQ_LENGTH,
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(model)
    except Exception as exc:  # noqa: BLE001 — any load failure falls back to Ollama
        _model = None
        _tokenizer = None
        _loaded = False
        _load_failed = True
        _error = (
            f"CountGPT LoRA: failed to load adapter from {path}: {exc}. "
            "Drafting will use Ollama llama3.1:8b."
        )
        _log(_error, level=logging.ERROR)
        return

    _model = model
    _tokenizer = tokenizer
    _loaded = True
    _load_failed = False
    _error = None
    _log(f"CountGPT LoRA: adapter loaded from {path}")


def get_lora_model():
    """Lazy-load once. Returns ``(model, tokenizer)`` or ``None``."""
    if force_ollama():
        return None
    if _loaded:
        return _model, _tokenizer
    if _load_failed:
        return None
    if not adapter_present() or not cuda_available():
        if adapter_present() and not cuda_available():
            # Record a clear reason for /api/health without retrying every call.
            if _error is None:
                with _lock:
                    if _error is None and not _loaded:
                        _try_load_locked()
        return None

    with _lock:
        if _loaded:
            return _model, _tokenizer
        if _load_failed:
            return None
        _try_load_locked()
        if _loaded:
            return _model, _tokenizer
    return None


def wrap_lora_prompt(prompt: str) -> str:
    """Wrap the shared RAG/drafting prompt in the SFT Instruction/Response format."""
    body = (prompt or "").strip()
    if body.endswith("Answer:"):
        body = body[: -len("Answer:")].rstrip()
    return f"### Instruction:\n{body}\n\n### Response:\n"


def extract_lora_response(decoded: str) -> str:
    """Return only the generated completion after ``### Response:``."""
    text = decoded or ""
    marker = "### Response:"
    if marker in text:
        text = text.split(marker, 1)[1]
    for stop in ("<|end_of_text|>", "<|eot_id|>"):
        text = text.replace(stop, "")
    return text.strip()


def generate_draft(prompt: str, *, max_new_tokens: int = MAX_NEW_TOKENS) -> str:
    """Run the loaded adapter. Raises ``LoraError`` if LoRA cannot generate."""
    pair = get_lora_model()
    if pair is None:
        raise LoraError(_error or "LoRA adapter is not loaded")
    model, tokenizer = pair
    wrapped = wrap_lora_prompt(prompt)
    try:
        inputs = tokenizer(wrapped, return_tensors="pt")
        if hasattr(inputs, "to"):
            inputs = inputs.to("cuda")
        if hasattr(inputs, "keys"):
            generate_kwargs = dict(inputs)
        else:
            generate_kwargs = inputs
        outputs = model.generate(
            **generate_kwargs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as exc:  # noqa: BLE001
        raise LoraError(f"LoRA generate failed: {exc}") from exc
    return extract_lora_response(decoded)
