"""Unit tests for the CountGPT SFT JSONL validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_training_data import (
    MIN_RECORDS,
    classify,
    main as validate_main,
    validate,
)


REPO_ROOT = Path(__file__).resolve().parent
DATASET = REPO_ROOT / "training_data.jsonl"
VALIDATOR = REPO_ROOT / "scripts" / "validate_training_data.py"


class TrainingDataFileTests(unittest.TestCase):
    def test_dataset_exists(self):
        self.assertTrue(DATASET.is_file(), f"missing {DATASET}")

    def test_validate_function_passes(self):
        errors, info = validate(DATASET)
        self.assertGreaterEqual(info.get("n", 0), MIN_RECORDS, info)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_cli_exits_zero(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--path", str(DATASET)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stdout + completed.stderr,
        )
        self.assertIn("status: PASS", completed.stdout)

    def test_main_returns_zero(self):
        self.assertEqual(validate_main(["--path", str(DATASET)]), 0)


class ValidatorLogicTests(unittest.TestCase):
    def _write(self, records: list[dict]) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            "w",
            suffix=".jsonl",
            delete=False,
            encoding="utf-8",
        )
        for rec in records:
            tmp.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return Path(tmp.name)

    def test_rejects_empty_output(self):
        path = self._write(
            [{"instruction": "Explain ATO.", "output": "   "}]
        )
        errors, _info = validate(path)
        self.assertTrue(any("output is empty" in e for e in errors), errors)

    def test_rejects_bad_json(self):
        path = Path(tempfile.mkstemp(suffix=".jsonl")[1])
        path.write_text("{not json}\n", encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        errors, _info = validate(path)
        self.assertTrue(any("JSON parse error" in e for e in errors), errors)

    def test_classify_ssp(self):
        rec = {
            "instruction": "Write a control implementation statement for AU-2.",
            "output": "[System Name] logs events. Customer Responsibility: N/A.",
        }
        self.assertEqual(classify(rec), "ssp")

    def test_classify_soc(self):
        rec = {
            "instruction": "A SOC analyst sees a failed login burst. Walk through the triage.",
            "output": "1. Compare to baseline. 2. Escalate if privileged.",
        }
        self.assertEqual(classify(rec), "soc")


if __name__ == "__main__":
    unittest.main()
