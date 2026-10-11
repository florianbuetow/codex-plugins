from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync_plugins.py"
SPEC = importlib.util.spec_from_file_location("sync_plugins", SCRIPT)
assert SPEC and SPEC.loader
sync_plugins = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync_plugins
SPEC.loader.exec_module(sync_plugins)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(root: Path) -> str:
    result = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        result.update(path.relative_to(root).as_posix().encode())
        result.update(stat.S_IMODE(path.stat().st_mode).to_bytes(4, "big"))
        result.update(path.read_bytes())
    return result.hexdigest()


class SyncPluginsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.source = base / "claude-code"
        self.output = base / "codex-plugins"
        self.output.mkdir()
        plugin = self.source / "plugins" / "demo-plugin"
        write_json(
            self.source / ".claude-plugin" / "marketplace.json",
            {
                "name": "demo",
                "plugins": [
                    {
                        "name": "demo-plugin",
                        "version": "1.2.3",
                        "description": "Demo workflows",
                        "source": "./plugins/demo-plugin",
                        "category": "development",
                    }
                ],
            },
        )
        write_json(
            plugin / ".claude-plugin" / "plugin.json",
            {
                "name": "demo-plugin",
                "version": "1.2.3",
                "description": "Demo workflows",
                "author": {"name": "Test Author"},
                "license": "MIT",
                "keywords": ["demo"],
            },
        )
        (plugin / "skills" / "existing").mkdir(parents=True)
        (plugin / "skills" / "existing" / "SKILL.md").write_text(
            "---\nname: existing\ndescription: Existing workflow.\n---\n\nKeep me byte-for-byte.\n",
            encoding="utf-8",
        )
        (plugin / "commands").mkdir()
        (plugin / "commands" / "run.md").write_text(
            "---\ndescription: Run the demo.\nargument-hint: '[target]'\n---\n\nTarget: $ARGUMENTS\n",
            encoding="utf-8",
        )
        (plugin / "agents").mkdir()
        (plugin / "agents" / "reviewer.md").write_text(
            "---\nname: reviewer\ndescription: Review things.\nmodel: sonnet\n---\n\nReview carefully.\n",
            encoding="utf-8",
        )
        (plugin / "scripts").mkdir()
        script = plugin / "scripts" / "tool.sh"
        script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        script.chmod(0o755)
        write_json(
            plugin / "hooks" / "hooks.json",
            {
                "hooks": {
                    "PostToolUse": [
                        {
                            "matcher": "Write|Edit",
                            "hooks": [{"type": "prompt", "prompt": "Review the edit."}],
                        },
                        {
                            "matcher": "ExitPlanMode",
                            "hooks": [{"type": "prompt", "prompt": "Review the plan."}],
                        },
                    ]
                }
            },
        )
        (plugin / "README.md").write_text(
            "# Demo Plugin\n\nUse this with Claude Code. Run `/demo:run`.\n",
            encoding="utf-8",
        )
        (plugin / ".DS_Store").write_bytes(b"ignored")
        (self.source / "README.md").write_text(
            "# Claude Code Plugins and Skills\n\n"
            "## solid-principles\n\nSource details for Claude Code.\n\n"
            "## Project Structure\n\nOld structure.\n\n"
            "## FAQ\n\nAsk Claude.\n\n"
            "## Hooks\n\nClaude hooks.\n\n"
            "## License\n\nMIT.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_sync(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--source",
                str(self.source),
                "--output",
                str(self.output),
                *extra,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_generates_codex_layout_without_changing_source(self) -> None:
        before = digest(self.source)
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, digest(self.source))

        plugin = self.output / "plugins" / "demo-plugin"
        portable = json.loads((plugin / "plugin.json").read_text())
        compatibility = json.loads(
            (plugin / ".codex-plugin" / "plugin.json").read_text()
        )
        self.assertEqual(portable["$schema"], sync_plugins.PORTABLE_SCHEMA)
        self.assertEqual(compatibility["skills"], "./skills/")
        self.assertTrue((plugin / "skills" / "run" / "SKILL.md").is_file())
        self.assertEqual(
            (plugin / "skills" / "existing" / "SKILL.md").read_text(),
            "---\nname: existing\ndescription: Existing workflow.\n---\n\nKeep me byte-for-byte.\n",
        )
        self.assertTrue((plugin / "agents" / "reviewer.md").is_file())
        self.assertTrue((plugin / "skills" / "reviewer" / "SKILL.md").is_file())
        self.assertFalse((plugin / "commands").exists())
        self.assertFalse((plugin / ".DS_Store").exists())
        hooks = json.loads((plugin / "hooks" / "hooks.json").read_text())
        handler = hooks["hooks"]["PostToolUse"][0]["hooks"][0]
        self.assertEqual(handler["type"], "command")
        report = json.loads((self.output / "generation-report.json").read_text())
        self.assertEqual(report["summary"]["warnings"], 1)
        self.assertIn("ExitPlanMode", report["warnings"][0])
        converted = (plugin / "skills" / "run" / "SKILL.md").read_text()
        self.assertNotIn("$ARGUMENTS", converted)
        self.assertIn("the current request's arguments", converted)
        plugin_readme = (plugin / "README.md").read_text()
        self.assertNotIn("claude plugin", plugin_readme)
        self.assertIn("Install with Codex", plugin_readme)
        self.assertIn(
            "codex plugin add demo-plugin@florianbuetow-codex-plugins",
            plugin_readme,
        )
        self.assertNotIn("`/demo:run`", plugin_readme)

    def test_generation_is_idempotent_and_check_detects_stale_output(self) -> None:
        first = self.run_sync()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = digest(self.output)
        second = self.run_sync()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(before, digest(self.output))
        current = self.run_sync("--check")
        self.assertEqual(current.returncode, 0, current.stderr)

        readme = self.output / "README.md"
        readme.write_text(readme.read_text() + "stale\n")
        stale = self.run_sync("--check")
        self.assertEqual(stale.returncode, 1)
        self.assertIn("README.md", stale.stderr)

    def test_refuses_to_replace_unmarked_plugin_directory(self) -> None:
        (self.output / "plugins").mkdir()
        (self.output / "plugins" / "personal.txt").write_text("keep")
        result = self.run_sync()
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to replace unmarked directory", result.stderr)
        self.assertEqual(
            (self.output / "plugins" / "personal.txt").read_text(), "keep"
        )

    def test_refuses_wrong_type_for_generated_directory(self) -> None:
        (self.output / "plugins").write_text("personal file\n")
        result = self.run_sync()
        self.assertEqual(result.returncode, 2)
        self.assertIn("wrong-type generated path", result.stderr)
        self.assertEqual((self.output / "plugins").read_text(), "personal file\n")

    def test_check_detects_executable_mode_drift(self) -> None:
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.output / "plugins" / "demo-plugin" / "scripts" / "tool.sh"
        self.assertEqual(stat.S_IMODE(script.stat().st_mode), 0o755)
        script.chmod(0o644)
        stale = self.run_sync("--check")
        self.assertEqual(stale.returncode, 1)
        self.assertIn("plugins", stale.stderr)

    def test_check_reports_missing_output_instead_of_crashing(self) -> None:
        result = self.run_sync("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("plugins", result.stderr)

    def test_refuses_to_replace_unmarked_readme(self) -> None:
        (self.output / "README.md").write_text("# Personal notes\n")
        result = self.run_sync()
        self.assertEqual(result.returncode, 2)
        self.assertIn("unmarked generated file", result.stderr)
        self.assertEqual(
            (self.output / "README.md").read_text(), "# Personal notes\n"
        )

    def test_rejects_source_symlinks(self) -> None:
        plugin = self.source / "plugins" / "demo-plugin"
        outside = Path(self.temp.name) / "outside-secret.txt"
        outside.write_text("do not publish\n")
        (plugin / "secret-link.txt").symlink_to(outside)
        result = self.run_sync()
        self.assertEqual(result.returncode, 2)
        self.assertIn("source symlinks are not allowed", result.stderr)
        self.assertFalse((self.output / "plugins").exists())

    def test_invalid_source_manifest_never_replaces_good_output(self) -> None:
        first = self.run_sync()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = digest(self.output)
        manifest = (
            self.source
            / "plugins"
            / "demo-plugin"
            / ".claude-plugin"
            / "plugin.json"
        )
        payload = json.loads(manifest.read_text())
        payload["version"] = "not-semver"
        write_json(manifest, payload)
        result = self.run_sync()
        self.assertEqual(result.returncode, 2)
        self.assertIn("failed validation", result.stderr)
        self.assertEqual(before, digest(self.output))

    def test_install_transaction_rolls_back_all_managed_paths(self) -> None:
        first = self.run_sync()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = digest(self.output)
        stage = Path(self.temp.name) / "stage"
        stage.mkdir()
        sync_plugins.generate(self.source, stage, str(self.source))
        original_rename = Path.rename

        def fail_second_install(path: Path, target: Path) -> Path:
            if path == stage / ".agents" / "plugins":
                raise OSError("injected install failure")
            return original_rename(path, target)

        with mock.patch.object(Path, "rename", fail_second_install):
            with self.assertRaises(OSError):
                sync_plugins.install_generated(self.output, stage)
        self.assertEqual(before, digest(self.output))
        self.assertFalse(list(self.output.rglob("*.sync-backup-*")))

    def test_warns_instead_of_misconverting_unsupported_prompt_hook_event(self) -> None:
        hooks_path = (
            self.source / "plugins" / "demo-plugin" / "hooks" / "hooks.json"
        )
        hooks = json.loads(hooks_path.read_text())
        hooks["hooks"]["SessionEnd"] = [
            {"hooks": [{"type": "prompt", "prompt": "This cannot steer."}]}
        ]
        write_json(hooks_path, hooks)
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        generated_hooks = json.loads(
            (
                self.output
                / "plugins"
                / "demo-plugin"
                / "hooks"
                / "hooks.json"
            ).read_text()
        )
        self.assertNotIn("SessionEnd", generated_hooks["hooks"])
        report = json.loads((self.output / "generation-report.json").read_text())
        self.assertTrue(
            any("SessionEnd" in warning for warning in report["warnings"])
        )

    def test_adapts_namespaced_and_prefixed_skill_frontmatter(self) -> None:
        skill = (
            self.source
            / "plugins"
            / "demo-plugin"
            / "skills"
            / "existing"
            / "SKILL.md"
        )
        skill.write_text(
            "<!-- license note -->\n"
            "---\n"
            "name: demo-plugin:existing\n"
            "version: 9.9.9\n"
            "description: Existing workflow.\n"
            "disable-model-invocation: true\n"
            "---\n\n"
            "Keep the workflow body.\n",
            encoding="utf-8",
        )
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = (
            self.output
            / "plugins"
            / "demo-plugin"
            / "skills"
            / "existing"
            / "SKILL.md"
        ).read_text()
        self.assertTrue(generated.startswith("---\nname: existing\n"))
        self.assertNotIn("disable-model-invocation", generated)
        self.assertNotIn("version: 9.9.9", generated)
        self.assertIn("<!-- license note -->", generated)
        self.assertIn("Keep the workflow body.", generated)

    def test_adapts_plugin_root_to_an_agent_resolved_shell_variable(self) -> None:
        skill = (
            self.source
            / "plugins"
            / "demo-plugin"
            / "skills"
            / "existing"
            / "SKILL.md"
        )
        skill.write_text(
            "---\nname: existing\ndescription: Existing workflow.\n---\n\n"
            'tool="${CLAUDE_PLUGIN_ROOT}/scripts/tool.py"\n',
            encoding="utf-8",
        )
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = (
            self.output
            / "plugins"
            / "demo-plugin"
            / "skills"
            / "existing"
            / "SKILL.md"
        ).read_text()
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", generated)
        self.assertNotIn("<absolute-plugin-root>", generated)
        self.assertIn("$PLUGIN_ROOT/scripts/tool.py", generated)
        self.assertIn("## Codex plugin path", generated)


if __name__ == "__main__":
    unittest.main()
