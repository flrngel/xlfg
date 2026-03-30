from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestSubagentStopGuard(unittest.TestCase):
    def _run_guard(self, payload: dict) -> tuple[int, str]:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "subagent-stop-guard.mjs"
        proc = subprocess.run(
            ["node", str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout.strip()

    def test_blocks_progress_note_when_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            transcript = root / "agent.jsonl"
            artifact = root / "repo-map.md"
            transcript.write_text(
                f'{{"role":"user","content":"PRIMARY_ARTIFACT: {artifact}\\nWrite findings to {artifact}"}}\n',
                encoding="utf-8",
            )
            code, out = self._run_guard(
                {
                    "agent_type": "xlfg-repo-mapper",
                    "cwd": str(root),
                    "agent_transcript_path": str(transcript),
                    "last_assistant_message": "Let me check the modal patterns first.",
                    "stop_hook_active": False,
                }
            )
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["decision"], "block")
            self.assertIn(str(artifact), data["reason"])

    def test_allows_done_when_artifact_has_final_status(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            transcript = root / "agent.jsonl"
            artifact = root / "repo-map.md"
            artifact.write_text("Status: DONE\n\n# Repo map\n", encoding="utf-8")
            transcript.write_text(
                f'{{"role":"user","content":"PRIMARY_ARTIFACT: {artifact}"}}\n',
                encoding="utf-8",
            )
            code, out = self._run_guard(
                {
                    "agent_type": "xlfg-repo-mapper",
                    "cwd": str(root),
                    "agent_transcript_path": str(transcript),
                    "last_assistant_message": f"DONE {artifact}",
                    "stop_hook_active": False,
                }
            )
            self.assertEqual(code, 0)
            self.assertEqual(out, "")

    def test_blocks_repeated_stop_when_artifact_still_missing(self) -> None:
        """After stopHookActive escape removal, guard blocks even on repeated attempts."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            transcript = root / "agent.jsonl"
            artifact = root / "repo-map.md"
            transcript.write_text(
                f'{{"role":"user","content":"PRIMARY_ARTIFACT: {artifact}"}}\n',
                encoding="utf-8",
            )
            code, out = self._run_guard(
                {
                    "agent_type": "xlfg-repo-mapper",
                    "cwd": str(root),
                    "agent_transcript_path": str(transcript),
                    "last_assistant_message": "Still orienting.",
                    "stop_hook_active": True,
                }
            )
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["decision"], "block")
            self.assertIn(str(artifact), data["reason"])
