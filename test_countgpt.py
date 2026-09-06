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
        self.assertFalse(countgpt.is_drafting_task("What is a POA&M?"))
        self.assertFalse(countgpt.is_drafting_task("SSP vs POA&M?"))

    def test_explain_hints(self):
        self.assertTrue(countgpt.is_explain_task("What is an SSP?"))
        self.assertTrue(countgpt.is_explain_task("SSP vs POA&M?"))
        self.assertTrue(countgpt.is_explain_task("What is a POA&M?"))
        self.assertTrue(countgpt.is_explain_task("What does an ISSO do?"))
        self.assertFalse(countgpt.is_explain_task("What does AC-2 require?"))
        self.assertFalse(countgpt.is_explain_task("What is AC-2?"))
        self.assertFalse(countgpt.is_explain_task("Draft a POA&M for AC-2"))


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

    def test_build_prompt_explain_is_pedagogical(self):
        prompt = countgpt.build_prompt("What is an SSP?", [], [])
        self.assertIn("plain English", prompt)
        self.assertIn("not official policy", prompt)
        self.assertNotIn("Drafting instructions", prompt)
        self.assertNotIn("Answer ONLY from the retrieved NIST SP 800-53 rules", prompt)


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


class WorkbenchPromptTests(unittest.TestCase):
    def test_poam_question_includes_fields_and_placeholders(self):
        question = countgpt.build_poam_question(
            {
                "finding": "Weak TLS cipher on web server",
                "severity": "High",
                "system_name": "WebPortal",
                "poc": "",
                "detector_source": "ACAS/Nessus",
                "plugin_id": "",
                "discovery_date": "2026-09-01",
                "control_id": "SC-8",
                "vendor_dependency": "no",
                "status": "Open",
                "guidance": "Use the High 30-day window.",
            }
        )
        self.assertIn("Draft a POA&M", question)
        self.assertIn("Weak TLS cipher on web server", question)
        self.assertIn("High", question)
        self.assertIn("30", question)
        self.assertIn("WebPortal", question)
        self.assertIn("[ISSO Name]", question)
        self.assertIn("ACAS/Nessus", question)
        self.assertIn("2026-09-01", question)
        self.assertIn("SC-8", question)
        self.assertIn("[plugin ID if known]", question)
        self.assertIn("Use the High 30-day window.", question)
        self.assertIn("Do not invent plugin IDs", question)

    def test_poam_question_requires_finding(self):
        with self.assertRaises(countgpt.WorkbenchError):
            countgpt.build_poam_question({"severity": "Low"})

    def test_ssp_question_uses_placeholders_and_control_id(self):
        question = countgpt.build_ssp_question(
            {
                "control_id": "AU-2",
                "system_name": "",
                "system_context": "DoD web application; SIEM not named.",
            }
        )
        self.assertIn("AU-2", question)
        self.assertIn("[System Name]", question)
        self.assertIn("DoD web application", question)
        self.assertIn("implementation statement", question.lower())
        self.assertIn("Do not invent tools", question)

    def test_ssp_question_requires_control_id(self):
        with self.assertRaises(countgpt.WorkbenchError):
            countgpt.build_ssp_question({"system_name": "WebPortal"})

    def test_retrieval_query_prefers_control_and_finding(self):
        poam_q = countgpt.workbench_retrieval_query(
            "poam",
            {"control_id": "AC-2", "finding": "stale local accounts"},
        )
        self.assertEqual(poam_q, "AC-2 stale local accounts")
        ssp_q = countgpt.workbench_retrieval_query(
            "ssp",
            {"control_id": "IA-2", "system_context": "CAC MFA"},
        )
        self.assertEqual(ssp_q, "IA-2 CAC MFA")

    def test_severity_timeline_normalization(self):
        self.assertEqual(countgpt.severity_timeline_days("high"), 30)
        self.assertEqual(countgpt.severity_timeline_days("medium"), 90)
        self.assertEqual(countgpt.severity_timeline_days("Low"), 180)
        self.assertEqual(countgpt.normalize_severity("mod"), "Moderate")

    def test_workbench_turn_reuses_generate_answer(self):
        matches = [
            {
                "id": "SC-8",
                "title": "Transmission Confidentiality",
                "text": "Protect transmitted information.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        captured = {}

        def fake_generate(question, history, *, retrieve_query=None):
            captured["question"] = question
            captured["history"] = history
            captured["retrieve_query"] = retrieve_query
            return "Weakness: Weak TLS on WebPortal.", matches

        with patch.object(countgpt, "generate_answer", side_effect=fake_generate):
            result = countgpt.workbench_turn(
                "poam",
                {
                    "finding": "Weak TLS cipher",
                    "severity": "High",
                    "system_name": "WebPortal",
                    "control_id": "SC-8",
                },
            )
        self.assertIn("Weak TLS", result["draft"])
        self.assertEqual(result["meta"]["mode"], "poam")
        self.assertEqual(result["meta"]["severity_timeline_days"], 30)
        self.assertEqual(captured["retrieve_query"], "SC-8 Weak TLS cipher")
        self.assertIn("Draft a POA&M", captured["question"])
        self.assertEqual(result["matches"][0]["id"], "SC-8")

    def test_export_markdown_includes_workbench_fields(self):
        md = countgpt.build_export_markdown(
            {
                "question": "Draft a POA&M",
                "answer": "Weakness: demo",
                "drafting": True,
                "mode": "poam",
                "generated_at": "2026-01-01T00:00:00+00:00",
                "fields": {"finding": "Weak TLS", "severity": "High"},
                "matches": [],
            }
        )
        self.assertIn("Workbench fields", md)
        self.assertIn("finding: Weak TLS", md)
        self.assertIn("poam", md)

    def test_export_basename_ssp(self):
        name = countgpt.export_basename(
            {"mode": "ssp", "drafting": True},
            when=__import__("datetime").datetime(2026, 1, 2, 3, 4, 5, tzinfo=__import__("datetime").timezone.utc),
        )
        self.assertTrue(name.startswith("countgpt-ssp-draft-"))


if __name__ == "__main__":
    unittest.main()
