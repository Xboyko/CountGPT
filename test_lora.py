"""Mocked tests for LoRA draft routing (no GPU or Unsloth required)."""

from __future__ import annotations

import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import countgpt
import lora_infer


class _FakeBatch:
    def __init__(self, payload=None):
        self.payload = payload or {"input_ids": object()}

    def to(self, _device):
        return self

    def keys(self):
        return self.payload.keys()

    def __iter__(self):
        return iter(self.payload)

    def items(self):
        return self.payload.items()

    def __getitem__(self, key):
        return self.payload[key]


class LoraConfigTests(unittest.TestCase):
    def tearDown(self):
        lora_infer.reset_lora_state()
        os.environ.pop("COUNTGPT_LORA_PATH", None)
        os.environ.pop("COUNTGPT_FORCE_OLLAMA", None)

    def test_lora_path_defaults_next_to_app(self):
        os.environ.pop("COUNTGPT_LORA_PATH", None)
        expected = Path(lora_infer.__file__).resolve().parent / "countgpt_model"
        self.assertEqual(lora_infer.lora_path(), expected)

    def test_lora_path_env_override(self):
        with patch.dict(os.environ, {"COUNTGPT_LORA_PATH": "/tmp/custom-adapter"}):
            self.assertEqual(lora_infer.lora_path(), Path("/tmp/custom-adapter"))

    def test_force_ollama_env(self):
        with patch.dict(os.environ, {"COUNTGPT_FORCE_OLLAMA": "1"}):
            self.assertTrue(lora_infer.force_ollama())
        with patch.dict(os.environ, {"COUNTGPT_FORCE_OLLAMA": "true"}):
            self.assertTrue(lora_infer.force_ollama())
        os.environ.pop("COUNTGPT_FORCE_OLLAMA", None)
        self.assertFalse(lora_infer.force_ollama())

    def test_adapter_present_requires_marker_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            self.assertFalse(lora_infer.adapter_present(empty))
            adapter = Path(tmp) / "adapter"
            adapter.mkdir()
            (adapter / "adapter_config.json").write_text("{}", encoding="utf-8")
            self.assertTrue(lora_infer.adapter_present(adapter))

    def test_available_false_without_gpu_or_adapter(self):
        with patch.object(lora_infer, "adapter_present", return_value=False), patch.object(
            lora_infer, "cuda_available", return_value=True
        ):
            self.assertFalse(lora_infer.lora_available())
        with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=False
        ):
            self.assertFalse(lora_infer.lora_available())

    def test_available_false_when_force_ollama(self):
        with patch.dict(os.environ, {"COUNTGPT_FORCE_OLLAMA": "1"}), patch.object(
            lora_infer, "adapter_present", return_value=True
        ), patch.object(lora_infer, "cuda_available", return_value=True):
            self.assertFalse(lora_infer.lora_available())

    def test_available_true_when_adapter_and_cuda(self):
        with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=True
        ):
            self.assertTrue(lora_infer.lora_available())


class LoraPromptTests(unittest.TestCase):
    def test_wrap_includes_nist_placeholders_and_caveat(self):
        matches = [
            {
                "id": "AC-2",
                "title": "Account Management",
                "text": "Manage information system accounts.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        prompt = countgpt.build_prompt("Draft a POA&M for AC-2", [], matches)
        wrapped = lora_infer.wrap_lora_prompt(prompt)
        self.assertTrue(wrapped.startswith("### Instruction:"))
        self.assertIn("### Response:", wrapped)
        self.assertFalse(wrapped.strip().endswith("Answer:"))
        self.assertIn("AC-2", wrapped)
        self.assertIn("Manage information system accounts.", wrapped)
        self.assertIn("[System Name]", wrapped)
        self.assertIn("[ISSO Name]", wrapped)
        self.assertIn("not assessor-validated", wrapped)

    def test_extract_response_strips_instruction(self):
        decoded = (
            "### Instruction:\nDraft a POA&M\n\n### Response:\n"
            "Weakness: demo\n\nThis is a draft, not assessor-validated."
            "<|end_of_text|>"
        )
        text = lora_infer.extract_lora_response(decoded)
        self.assertEqual(
            text,
            "Weakness: demo\n\nThis is a draft, not assessor-validated.",
        )


class LoraLoadTests(unittest.TestCase):
    def tearDown(self):
        lora_infer.reset_lora_state()
        os.environ.pop("COUNTGPT_FORCE_OLLAMA", None)
        os.environ.pop("COUNTGPT_LORA_PATH", None)

    def test_get_model_none_without_cuda(self):
        with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=False
        ):
            self.assertIsNone(lora_infer.get_lora_model())
            self.assertFalse(lora_infer.lora_loaded())
            self.assertIn("CUDA", lora_infer.lora_error() or "")

    def test_load_failure_is_cached_and_logged(self):
        fake_flm = MagicMock()
        fake_flm.from_pretrained.side_effect = RuntimeError("no GPU memory")
        with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=True
        ), patch.object(lora_infer, "_import_unsloth", return_value=fake_flm):
            self.assertIsNone(lora_infer.get_lora_model())
            self.assertIsNone(lora_infer.get_lora_model())
        self.assertEqual(fake_flm.from_pretrained.call_count, 1)
        self.assertFalse(lora_infer.lora_available())
        self.assertIn("no GPU memory", lora_infer.lora_error() or "")

    def test_lazy_load_once_thread_safe(self):
        fake_model = object()
        fake_tok = object()
        started = threading.Event()
        release = threading.Event()
        calls = []

        def from_pretrained(**_kwargs):
            calls.append(1)
            started.set()
            release.wait(timeout=2)
            return fake_model, fake_tok

        fake_flm = MagicMock()
        fake_flm.from_pretrained.side_effect = from_pretrained
        fake_flm.for_inference.return_value = None

        def worker():
            with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
                lora_infer, "cuda_available", return_value=True
            ), patch.object(lora_infer, "_import_unsloth", return_value=fake_flm):
                pair = lora_infer.get_lora_model()
                self.assertIs(pair[0], fake_model)
                self.assertIs(pair[1], fake_tok)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        self.assertTrue(started.wait(timeout=2))
        release.set()
        for thread in threads:
            thread.join(timeout=2)
        self.assertEqual(len(calls), 1)
        self.assertTrue(lora_infer.lora_loaded())

    def test_status_reports_loaded_and_available(self):
        with patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=True
        ):
            info = lora_infer.lora_status()
        self.assertTrue(info["available"])
        self.assertFalse(info["loaded"])
        self.assertFalse(info["force_ollama"])
        self.assertIn("countgpt_model", info["path"])


class LoraRoutingTests(unittest.TestCase):
    def setUp(self):
        countgpt.STORE_OK = True
        countgpt.STORE_ERROR = None
        lora_infer.reset_lora_state()

    def tearDown(self):
        countgpt.reset_store_state()
        lora_infer.reset_lora_state()
        os.environ.pop("COUNTGPT_FORCE_OLLAMA", None)
        os.environ.pop("COUNTGPT_DRY_RUN", None)

    def _matches(self):
        return [
            {
                "id": "AC-2",
                "title": "Account Management",
                "text": "Manage information system accounts.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]

    def test_lookup_stays_on_ollama(self):
        ollama_client = MagicMock()
        ollama_client.chat.return_value = {
            "message": {"content": "AC-2 is account management."}
        }
        with patch.object(countgpt.retrieve, "retrieve", return_value=self._matches()), patch.object(
            countgpt, "get_ollama_client", return_value=ollama_client
        ), patch.object(lora_infer, "generate_draft") as draft:
            answer, matches = countgpt.generate_answer("What does AC-2 require?", [])
        self.assertIn("account management", answer.lower())
        self.assertEqual(matches[0]["id"], "AC-2")
        draft.assert_not_called()
        ollama_client.chat.assert_called_once()
        self.assertEqual(countgpt.last_generation_info()["backend"], "ollama")

    def test_explain_stays_on_ollama(self):
        ollama_client = MagicMock()
        ollama_client.chat.return_value = {
            "message": {"content": "An SSP is the system security plan."}
        }
        with patch.object(countgpt.retrieve, "retrieve", return_value=[]), patch.object(
            countgpt, "get_ollama_client", return_value=ollama_client
        ), patch.object(lora_infer, "lora_available", return_value=True), patch.object(
            lora_infer, "generate_draft"
        ) as draft:
            answer, _ = countgpt.generate_answer("What is an SSP?", [])
        self.assertIn("system security plan", answer.lower())
        draft.assert_not_called()
        ollama_client.chat.assert_called_once()

    def test_drafting_uses_lora_when_available(self):
        lora_prompt = {}

        def fake_draft(prompt, **_kwargs):
            lora_prompt["text"] = prompt
            return "Weakness: [System Name]\nThis is a draft, not assessor-validated."

        with patch.object(countgpt.retrieve, "retrieve", return_value=self._matches()), patch.object(
            lora_infer, "lora_available", return_value=True
        ), patch.object(lora_infer, "generate_draft", side_effect=fake_draft), patch.object(
            countgpt, "get_ollama_client"
        ) as ollama_factory:
            answer, matches = countgpt.generate_answer("Draft a POA&M for AC-2", [])
        self.assertIn("Weakness", answer)
        self.assertEqual(matches[0]["id"], "AC-2")
        self.assertIn("AC-2", lora_prompt["text"])
        self.assertIn("not assessor-validated", lora_prompt["text"])
        self.assertIn("[System Name]", lora_prompt["text"])
        ollama_factory.assert_not_called()
        self.assertEqual(countgpt.last_generation_info()["backend"], "lora")

    def test_drafting_falls_back_when_lora_fails(self):
        ollama_client = MagicMock()
        ollama_client.chat.return_value = {"message": {"content": "Ollama draft"}}
        with patch.object(countgpt.retrieve, "retrieve", return_value=self._matches()), patch.object(
            lora_infer, "lora_available", return_value=True
        ), patch.object(
            lora_infer, "generate_draft", side_effect=lora_infer.LoraError("boom")
        ), patch.object(countgpt, "get_ollama_client", return_value=ollama_client):
            answer, _ = countgpt.generate_answer("Draft a POA&M for AC-2", [])
        self.assertEqual(answer, "Ollama draft")
        ollama_client.chat.assert_called_once()
        self.assertEqual(countgpt.last_generation_info()["backend"], "ollama")

    def test_force_ollama_skips_lora_for_drafts(self):
        ollama_client = MagicMock()
        ollama_client.chat.return_value = {"message": {"content": "Forced Ollama"}}
        with patch.dict(os.environ, {"COUNTGPT_FORCE_OLLAMA": "1"}), patch.object(
            countgpt.retrieve, "retrieve", return_value=self._matches()
        ), patch.object(lora_infer, "adapter_present", return_value=True), patch.object(
            lora_infer, "cuda_available", return_value=True
        ), patch.object(lora_infer, "generate_draft") as draft, patch.object(
            countgpt, "get_ollama_client", return_value=ollama_client
        ):
            answer, _ = countgpt.generate_answer("Draft a POA&M for AC-2", [])
        self.assertEqual(answer, "Forced Ollama")
        draft.assert_not_called()
        ollama_client.chat.assert_called_once()

    def test_workbench_poam_uses_lora(self):
        with patch.object(countgpt.retrieve, "retrieve", return_value=self._matches()), patch.object(
            lora_infer, "lora_available", return_value=True
        ), patch.object(
            lora_infer,
            "generate_draft",
            return_value="Weakness: Weak TLS.\nThis is a draft, not assessor-validated.",
        ), patch.object(countgpt, "get_ollama_client") as ollama_factory:
            result = countgpt.workbench_turn(
                "poam",
                {"finding": "Weak TLS", "severity": "High", "control_id": "AC-2"},
            )
        self.assertIn("Weak TLS", result["draft"])
        self.assertTrue(result["meta"]["drafting"])
        self.assertEqual(result["meta"]["backend"], "lora")
        self.assertTrue(result["meta"]["model"].startswith("lora:"))
        ollama_factory.assert_not_called()

    def test_workbench_ssp_uses_lora(self):
        with patch.object(countgpt.retrieve, "retrieve", return_value=self._matches()), patch.object(
            lora_infer, "lora_available", return_value=True
        ), patch.object(
            lora_infer, "generate_draft", return_value="Implementation summary for AU-2."
        ):
            result = countgpt.workbench_turn("ssp", {"control_id": "AU-2"})
        self.assertEqual(result["meta"]["backend"], "lora")
        self.assertIn("AU-2", result["meta"]["question"])

    def test_health_includes_lora_fields(self):
        with patch.object(countgpt, "check_ollama", return_value={"reachable": True}), patch.object(
            lora_infer, "lora_status", return_value={
                "path": "/tmp/countgpt_model",
                "adapter_present": True,
                "cuda_available": False,
                "force_ollama": False,
                "available": False,
                "loaded": False,
                "error": "CUDA is not available",
            }
        ):
            health = countgpt.health_status()
        self.assertIn("lora", health)
        self.assertFalse(health["lora"]["loaded"])
        self.assertFalse(health["lora"]["available"])
        self.assertEqual(health["lora"]["path"], "/tmp/countgpt_model")

    def test_generate_draft_decodes_mock_model(self):
        tokenizer = MagicMock()
        tokenizer.return_value = _FakeBatch()
        tokenizer.decode.return_value = (
            "### Instruction:\nDraft\n\n### Response:\nMilestones: demo"
        )
        model = MagicMock()
        model.generate.return_value = [[1, 2, 3]]
        with patch.object(lora_infer, "get_lora_model", return_value=(model, tokenizer)):
            text = lora_infer.generate_draft("Draft a POA&M")
        self.assertEqual(text, "Milestones: demo")
        model.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
