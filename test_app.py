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
        self.assertIn("/workbench", res.text)
        self.assertIn("/guide", res.text)
        self.assertIn("Chat", res.text)
        self.assertIn("Guide", res.text)

    def test_static_js_and_css(self):
        js = self.client.get("/static/app.js")
        css = self.client.get("/static/styles.css")
        self.assertEqual(js.status_code, 200)
        self.assertEqual(css.status_code, 200)
        self.assertIn("/api/chat", js.text)
        self.assertIn("What is an SSP?", js.text)
        self.assertIn('params.get("q")', js.text)

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
        self.assertFalse(res.json()["explain"])

    def test_chat_marks_explain_for_glossary_question(self):
        with patch.object(countgpt, "STORE_OK", True), patch.object(
            countgpt,
            "generate_answer",
            return_value=("An SSP is the written story of how a system is protected.", []),
        ):
            res = self.client.post(
                "/api/chat",
                json={"message": "What is an SSP?", "history": []},
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["explain"])
        self.assertFalse(data["drafting"])
        self.assertIn("system is protected", data["answer"].lower())

    def test_learning_poam_question_is_not_a_draft(self):
        with patch.object(countgpt, "STORE_OK", True), patch.object(
            countgpt,
            "generate_answer",
            return_value=("A POA&M is a living fix list.", []),
        ):
            res = self.client.post(
                "/api/chat",
                json={"message": "What is a POA&M?", "history": []},
            )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["drafting"])
        self.assertTrue(res.json()["explain"])

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

    def test_workbench_page_serves_html(self):
        res = self.client.get("/workbench")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("POA&amp;M", res.text)
        self.assertIn("/static/workbench.js", res.text)
        self.assertIn("Draft / not assessor-validated", res.text)
        self.assertIn("/guide", res.text)
        self.assertIn("Guide", res.text)

    def test_workbench_js_calls_poam_and_ssp(self):
        js = self.client.get("/static/workbench.js")
        self.assertEqual(js.status_code, 200)
        self.assertIn("/api/poam", js.text)
        self.assertIn("/api/ssp", js.text)

    def test_poam_requires_finding(self):
        missing = self.client.post("/api/poam", json={"severity": "High"})
        self.assertIn(missing.status_code, {400, 422})
        empty = self.client.post("/api/poam", json={"finding": "  ", "severity": "High"})
        self.assertEqual(empty.status_code, 400)

    def test_ssp_requires_control_id(self):
        missing = self.client.post("/api/ssp", json={"system_name": "WebPortal"})
        self.assertIn(missing.status_code, {400, 422})
        empty = self.client.post("/api/ssp", json={"control_id": "   "})
        self.assertEqual(empty.status_code, 400)

    def test_poam_happy_path_dry_run(self):
        matches = [
            {
                "id": "SC-8",
                "title": "Transmission Confidentiality and Integrity",
                "text": "Protect the confidentiality of transmitted information.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        with patch.dict("os.environ", {"COUNTGPT_DRY_RUN": "1"}), patch.object(
            countgpt, "STORE_OK", True
        ), patch.object(countgpt.retrieve, "retrieve", return_value=matches):
            res = self.client.post(
                "/api/poam",
                json={
                    "finding": "Weak cipher suite on the public web server",
                    "severity": "High",
                    "system_name": "WebPortal",
                    "detector_source": "ACAS/Nessus",
                    "discovery_date": "2026-09-01",
                    "control_id": "SC-8",
                    "status": "Open",
                },
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("draft", data)
        self.assertIn("SC-8", data["draft"])
        self.assertEqual(data["matches"][0]["id"], "SC-8")
        self.assertEqual(data["meta"]["mode"], "poam")
        self.assertEqual(data["meta"]["severity_timeline_days"], 30)
        self.assertTrue(data["meta"]["dry_run"])
        self.assertIn("ACAS/Nessus", data["meta"]["question"])

    def test_ssp_happy_path_dry_run(self):
        matches = [
            {
                "id": "AU-2",
                "title": "Event Logging",
                "text": "Identify the types of events that the system is capable of logging.",
                "score": 1.0,
                "source": "id:exact",
            }
        ]
        with patch.dict("os.environ", {"COUNTGPT_DRY_RUN": "1"}), patch.object(
            countgpt, "STORE_OK", True
        ), patch.object(countgpt.retrieve, "retrieve", return_value=matches):
            res = self.client.post(
                "/api/ssp",
                json={
                    "control_id": "AU-2",
                    "system_name": "WebPortal",
                    "system_context": "DoD web application; SIEM not named.",
                },
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("AU-2", data["draft"])
        self.assertEqual(data["meta"]["mode"], "ssp")
        self.assertIn("AU-2", data["meta"]["retrieve_query"])

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

    def test_guide_page_serves_html(self):
        res = self.client.get("/guide")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("Learning Guide", res.text)
        self.assertIn("SSP vs POA&amp;M", res.text)
        self.assertIn("glossary-search", res.text)
        self.assertIn('href="/"', res.text)
        self.assertIn('href="/workbench"', res.text)
        self.assertIn('href="/guide"', res.text)
        self.assertIn("Chat", res.text)
        self.assertIn("Workbench", res.text)
        self.assertIn("Guide", res.text)
        self.assertIn("/static/guide.js", res.text)
        js = self.client.get("/static/guide.js")
        self.assertEqual(js.status_code, 200)
        self.assertIn("/api/glossary", js.text)

    def test_glossary_api_has_required_keys(self):
        res = self.client.get("/api/glossary")
        self.assertEqual(res.status_code, 200)
        terms = res.json()["terms"]
        ids = {item["id"] for item in terms}
        labels = {item["term"] for item in terms}
        required_ids = {
            "ssp",
            "poam",
            "sar",
            "ato",
            "rmf",
            "nist-800-53",
            "control",
            "control-enhancement",
            "isso",
            "issm",
            "ao",
            "emass",
            "acas",
            "stig",
            "residual-risk",
            "false-positive",
            "risk-adjustment",
            "odp",
            "continuous-monitoring",
        }
        self.assertTrue(required_ids.issubset(ids), f"missing {required_ids - ids}")
        for label in ("SSP", "POA&M", "SAR", "ATO", "RMF", "ISSO", "ACAS", "STIG"):
            self.assertIn(label, labels)
        ssp = next(item for item in terms if item["id"] == "ssp")
        self.assertGreaterEqual(len(ssp["definition"].split()), 20)
        self.assertLessEqual(len(ssp["definition"].split(".")), 6)

    def test_guide_api_has_chapters(self):
        res = self.client.get("/api/guide")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        ids = [chapter["id"] for chapter in data["chapters"]]
        for expected in (
            "what-countgpt-is",
            "nist-800-53",
            "rmf-ato",
            "ssp-vs-poam",
            "roles",
            "severity-timelines",
            "acas-vs-stig",
            "how-countgpt-answers",
            "practice-scenarios",
            "glossary",
        ):
            self.assertIn(expected, ids)
        ssp_chapter = next(c for c in data["chapters"] if c["id"] == "ssp-vs-poam")
        self.assertIn("SSP vs POA&M", ssp_chapter["try_in_chat"])

    def test_field_help_has_required_keys(self):
        res = self.client.get("/api/field-help")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        poam_keys = set(data["poam"])
        ssp_keys = set(data["ssp"])
        required_poam = {
            "severity",
            "finding",
            "system_name",
            "poc",
            "detector_source",
            "discovery_date",
            "control_id",
            "vendor_dependency",
            "status",
        }
        required_ssp = {"control_id", "system_context"}
        self.assertTrue(required_poam.issubset(poam_keys), f"missing {required_poam - poam_keys}")
        self.assertTrue(required_ssp.issubset(ssp_keys), f"missing {required_ssp - ssp_keys}")
        for group in (data["poam"], data["ssp"]):
            for key, tip in group.items():
                sentences = [part for part in tip["body"].replace("?", ".").split(".") if part.strip()]
                self.assertGreaterEqual(len(sentences), 2, key)
                self.assertLessEqual(len(sentences), 4, key)
                self.assertIn("title", tip)

    def test_scenarios_api_and_static_shape(self):
        res = self.client.get("/api/scenarios")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("fictional"))
        items = data["scenarios"]
        self.assertGreaterEqual(len(items), 6)
        self.assertLessEqual(len(items), 10)
        slugs = {item["slug"] for item in items}
        self.assertIn("acas-high-weak-cipher", slugs)
        self.assertTrue(any(item["mode"] == "poam" for item in items))
        self.assertTrue(any(item["mode"] == "ssp" for item in items))
        for item in items:
            self.assertIn(item["difficulty"], {"intro", "intermediate"})
            self.assertIn(item["mode"], {"poam", "ssp"})
            self.assertTrue(item["title"])
            self.assertTrue(item["learning_goal"])
            self.assertIsInstance(item["fields"], dict)
            self.assertGreaterEqual(len(item["what_good_looks_like"]), 3)
        one = self.client.get("/api/scenarios/acas-high-weak-cipher")
        self.assertEqual(one.status_code, 200)
        self.assertEqual(one.json()["mode"], "poam")
        self.assertEqual(one.json()["fields"]["severity"], "High")
        missing = self.client.get("/api/scenarios/not-a-real-slug")
        self.assertEqual(missing.status_code, 404)

    def test_workbench_documents_scenario_query_param(self):
        html = self.client.get("/workbench")
        self.assertEqual(html.status_code, 200)
        self.assertIn("scenario-select", html.text)
        self.assertIn('data-help="poam.severity"', html.text)
        self.assertIn("Why this field?", html.text)
        self.assertIn("Practice / fictional", html.text)
        js = self.client.get("/static/workbench.js")
        self.assertEqual(js.status_code, 200)
        # /workbench?scenario=<slug> prefills the form and does not auto-generate.
        self.assertIn('params.get("scenario")', js.text)
        self.assertIn("/api/scenarios", js.text)
        self.assertIn("/api/field-help", js.text)

    def test_guide_lists_practice_scenarios(self):
        res = self.client.get("/guide")
        self.assertEqual(res.status_code, 200)
        self.assertIn("practice-scenarios", res.text)
        self.assertIn("Practice / fictional", res.text)
        self.assertIn("/workbench?scenario=", res.text)
        js = self.client.get("/static/guide.js")
        self.assertEqual(js.status_code, 200)
        self.assertIn("/api/scenarios", js.text)


if __name__ == "__main__":
    unittest.main()
