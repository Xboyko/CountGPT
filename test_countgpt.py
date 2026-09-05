"""Unit tests for draft/lookup routing, prompts, export, and Ollama host."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import countgpt


class DraftRoutingTests(unittest.TestCase):
    def test_drafting_hints(self):
        self.assertTrue(countgpt.is_drafting_task("Draft a POA&M for AC-2"))
        self.assertTrue(countgpt.is_drafting_task("Write a POAM for weak TLS"))
        self.assertTrue(
            countgpt.is_drafting_task(
                "Write an SSP implementation statement for AU-2 Event Logging."
            )
        )
        self.assertTrue(countgpt.is_drafting_task("generate a control implementation"))
        self.assertTrue(countgpt.is_drafting_task("SOC triage for a failed login spike"))

    def test_lookup_hints(self):
        self.assertFalse(countgpt.is_drafting_task("What does AC-2 require?"))
        self.assertFalse(countgpt.is_drafting_task("Explain IA-2 identification"))
        self.assertFalse(countgpt.is_drafting_task("Summarize requirements for AU-2"))
        self.assertFalse(countgpt.is_drafting_task("Tell me about AC-20"))


class HistoryAndPromptTests(unittest.TestCase):
    def test_history_to_text_messages(self):
        history = [
            {"role": "user", "content": "What is AC-2?"},
            {"role": "assistant", "content": "Account management."},
            {"role": "user", "content": "And AC-3?"},
            {"role": "assistant", "content": "Access enforcement."},
        ]
        text = countgpt.history_to_text(history)
        self.assertIn("User: What is AC-2?", text)
        self.assertIn("Assistant: Account management.", text)
        self.assertIn("User: And AC-3?", text)

    def test_build_prompt_lookup_uses_retrieved_rules(self):
        matches = [
            {
                "id": "AC-2",
                "title": "Account Management",
                "text": "Manage information system accounts.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        prompt = countgpt.build_prompt("What does AC-2 require?", [], matches)
        self.assertIn("Answer ONLY from the retrieved NIST SP 800-53 rules", prompt)
        self.assertIn("AC-2", prompt)
        self.assertNotIn("Drafting instructions", prompt)

    def test_build_prompt_drafting_includes_instructions(self):
        matches = [
            {
                "id": "AU-2",
                "title": "Event Logging",
                "text": "Log events.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        prompt = countgpt.build_prompt(
            "Write an SSP implementation statement for AU-2",
            [],
            matches,
        )
        self.assertIn("Drafting instructions", prompt)
        self.assertIn("not assessor-validated", prompt)
        self.assertIn("AU-2", prompt)

    def test_build_prompt_no_matches(self):
        prompt = countgpt.build_prompt("What is a banana control?", [], [])
        self.assertIn("could not find a confident NIST match", prompt)
        self.assertIn("Do NOT invent control IDs", prompt)


class ExportAndHostTests(unittest.TestCase):
    def test_export_markdown_includes_disclaimer_and_sources(self):
        state = {
            "question": "What does AC-2 require?",
            "answer": "AC-2 requires account management.",
            "drafting": False,
            "generated_at": "2026-01-01T00:00:00+00:00",
            "matches": [
                {
                    "id": "AC-2",
                    "title": "Account Management",
                    "text": "Manage accounts.",
                    "score": 1.0,
                    "source": "id:exact",
                }
            ],
        }
        md = countgpt.build_export_markdown(state)
        self.assertIn(countgpt.DISCLAIMER_TITLE, md)
        self.assertIn("What does AC-2 require?", md)
        self.assertIn("AC-2 requires account management.", md)
        self.assertIn("AC-2", md)
        self.assertIn("lookup", md)

    def test_export_csv_has_draft_and_control_rows(self):
        state = {
            "question": "Draft a POA&M for AC-2",
            "answer": "Here is a draft.",
            "drafting": True,
            "generated_at": "2026-01-01T00:00:00+00:00",
            "matches": [
                {
                    "id": "AC-2",
                    "title": "Account Management",
                    "text": "Manage accounts.",
                    "score": 1.0,
                    "source": "id:exact",
                }
            ],
        }
        csv_text = countgpt.build_export_csv(state)
        self.assertIn("row_type", csv_text)
        self.assertIn("draft", csv_text)
        self.assertIn("retrieved_control", csv_text)
        self.assertIn("AC-2", csv_text)

    def test_ollama_host_default_and_override(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OLLAMA_HOST", None)
            self.assertEqual(countgpt.ollama_host(), "http://127.0.0.1:11434")
        with patch.dict(os.environ, {"OLLAMA_HOST": "192.168.1.20:11434"}):
            self.assertEqual(countgpt.ollama_host(), "http://192.168.1.20:11434")
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://10.0.0.8:11434/"}):
            self.assertEqual(countgpt.ollama_host(), "http://10.0.0.8:11434")

    def test_dry_run_answer_cites_matches(self):
        matches = [
            {
                "id": "AC-2",
                "title": "Account Management",
                "text": "Manage information system accounts.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        text = countgpt.dry_run_answer("What does AC-2 require?", matches)
        self.assertIn("AC-2", text)
        self.assertIn("Account Management", text)


if __name__ == "__main__":
    unittest.main()
