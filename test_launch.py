"""CI-friendly checks for one-command launch files (no live Ollama required)."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class LaunchFilesTests(unittest.TestCase):
    def test_start_sh_exists_with_shebang(self):
        script = ROOT / "start.sh"
        self.assertTrue(script.is_file(), "start.sh is missing")
        first = script.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first, "#!/usr/bin/env bash")

    def test_start_sh_is_executable(self):
        mode = (ROOT / "start.sh").stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR, "start.sh should be executable (git file mode)")

    def test_start_sh_bash_n(self):
        script = ROOT / "start.sh"
        result = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_start_sh_covers_required_behavior(self):
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn("OLLAMA_HOST", text)
        self.assertIn("rules_with_embeddings.pkl", text)
        self.assertIn("python setup_data.py", text)
        self.assertIn("llama3.1:8b", text)
        self.assertIn("uvicorn app:app --host", text)
        self.assertIn("START_RELOAD", text)
        self.assertIn("http://127.0.0.1", text)
        self.assertIn("install/start Ollama on Windows and pull llama3.1:8b", text)
        self.assertIn("grep nameserver /etc/resolv.conf", text)

    def test_entrypoint_bash_n(self):
        script = ROOT / "docker" / "entrypoint.sh"
        self.assertTrue(script.is_file())
        result = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_start_ps1_prefers_wsl(self):
        path = ROOT / "start.ps1"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("wsl -e bash start.sh", text)
        self.assertIn("venv is typically WSL", text)
        self.assertIn("http://127.0.0.1:11434", text)
        self.assertIn("uvicorn app:app", text)

    def test_compose_declares_ollama_and_countgpt(self):
        text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("ollama:", text)
        self.assertIn("countgpt:", text)
        self.assertIn("OLLAMA_HOST: http://ollama:11434", text)
        self.assertIn("7860:7860", text)
        self.assertIn("ollama_models:", text)
        self.assertIn("countgpt_data:", text)
        self.assertIn("llama3.1:8b", text)

    def test_dockerfile_is_practical(self):
        text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("FROM python:3.12-slim", text)
        self.assertIn("requirements.txt", text)
        self.assertIn("EXPOSE 7860", text)
        self.assertIn("uvicorn", text)
        self.assertIn("docker/entrypoint.sh", text)

    def test_compose_config_if_docker_available(self):
        docker = shutil.which("docker")
        if not docker:
            self.skipTest("docker not installed")
        compose_file = ROOT / "docker-compose.yml"
        result = subprocess.run(
            [docker, "compose", "-f", str(compose_file), "config", "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 and "compose" in (result.stderr or "").lower():
            compose = shutil.which("docker-compose")
            if not compose:
                self.skipTest("docker compose plugin not available")
            result = subprocess.run(
                [compose, "-f", str(compose_file), "config", "-q"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    os.chdir(ROOT)
    unittest.main()
