"""API tests for the FastAPI HTML chat server."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app as countgpt_app
import countgpt


class AppApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(countgpt_app.app)

    def test_index_serves_html_ui(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("CountGPT", res.text)
        self.assertIn("Draft / not assessor-validated", res.text)
        self.assertIn("/static/app.js", res.text)

    def test_static_js_and_css(self):
        js = self.client.get("/static/app.js")
        css = self.client.get("/static/styles.css")
        self.assertEqual(js.status_code, 200)
        self.assertEqual(css.status_code, 200)
        self.assertIn("/api/chat", js.text)

    def test_health_shape(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ok", data)
        self.assertIn("store_loaded", data)
        self.assertIn("ollama", data)
        self.assertIn("dry_run", data)
        self.assertEqual(data["model"], "llama3.1:8b")
        self.assertIn("host", data["ollama"])

    def test_chat_requires_message(self):
        res = self.client.post("/api/chat", json={"message": "  ", "history": []})
        self.assertEqual(res.status_code, 400)

    def test_chat_without_store_returns_setup_message(self):
        with patch.object(countgpt, "STORE_OK", False), patch.object(
            countgpt, "STORE_ERROR", "ERROR: rules_with_embeddings.pkl not found."
        ):
            res = self.client.post(
                "/api/chat",
                json={"message": "What does AC-2 require?", "history": []},
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("not found", data["answer"].lower())
        self.assertEqual(data["matches"], [])
        self.assertFalse(data["drafting"])

    def test_chat_uses_retrieve_and_returns_matches(self):
        matches = [
            {
                "id": "AC-2",
                "title": "Account Management",
                "text": "Manage accounts.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]

        def fake_generate(question, history):
            self.assertEqual(question, "What does AC-2 require?")
            self.assertEqual(history, [{"role": "user", "content": "hi"}])
            return "AC-2 covers account management.", matches

        with patch.object(countgpt, "STORE_OK", True), patch.object(
            countgpt, "generate_answer", side_effect=fake_generate
        ):
            res = self.client.post(
                "/api/chat",
                json={
                    "message": "What does AC-2 require?",
                    "history": [{"role": "user", "content": "hi"}],
                },
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("account management", data["answer"].lower())
        self.assertEqual(data["matches"][0]["id"], "AC-2")
        self.assertFalse(data["drafting"])

    def test_chat_marks_drafting(self):
        with patch.object(countgpt, "STORE_OK", True), patch.object(
            countgpt,
            "generate_answer",
            return_value=("Here is a draft.", []),
        ):
            res = self.client.post(
                "/api/chat",
                json={"message": "Draft a POA&M for AC-2", "history": []},
            )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["drafting"])

    def test_chat_ollama_error_is_502(self):
        with patch.object(countgpt, "STORE_OK", True), patch.object(
            countgpt,
            "generate_answer",
            side_effect=countgpt.OllamaError("Ollama at http://127.0.0.1:11434 failed"),
        ):
            res = self.client.post(
                "/api/chat",
                json={"message": "What does AC-2 require?", "history": []},
            )
        self.assertEqual(res.status_code, 502)

    def test_export_markdown(self):
        res = self.client.post(
            "/api/export",
            json={
                "question": "What does AC-2 require?",
                "answer": "Account management.",
                "drafting": False,
                "matches": [
                    {
                        "id": "AC-2",
                        "title": "Account Management",
                        "text": "Manage accounts.",
                        "score": 1.0,
                        "source": "id:exact",
                    }
                ],
                "format": "md",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/markdown", res.headers.get("content-type", ""))
        self.assertIn("Draft / not assessor-validated", res.text)
        self.assertIn("AC-2", res.text)
        self.assertIn("attachment", res.headers.get("content-disposition", ""))

    def test_export_csv(self):
        res = self.client.post(
            "/api/export",
            json={
                "question": "Draft a POA&M",
                "answer": "Draft text",
                "drafting": True,
                "matches": [],
                "format": "csv",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers.get("content-type", ""))
        self.assertIn("row_type", res.text)


if __name__ == "__main__":
    unittest.main()
