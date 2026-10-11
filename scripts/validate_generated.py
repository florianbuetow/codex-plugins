#!/usr/bin/env python3
"""Validate generated Codex manifests, marketplace coverage, and skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_object(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(ROOT)}: invalid or missing JSON ({error})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: expected JSON object")
        return {}
    return value


def main(root: Path | None = None) -> int:
    global ROOT
    if root is not None:
        ROOT = root.resolve()
    errors: list[str] = []
    marketplace = load_object(ROOT / ".agents/plugins/marketplace.json", errors)
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        errors.append("marketplace plugins must be an array")
        entries = []
    if not isinstance(marketplace.get("name"), str) or not marketplace["name"].strip():
        errors.append("marketplace name must be non-empty")
    marketplace_interface = marketplace.get("interface")
    if not isinstance(marketplace_interface, dict) or not isinstance(
        marketplace_interface.get("displayName"), str
    ):
        errors.append("marketplace interface.displayName is required")
    entry_names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
    plugin_dirs = sorted(
        path for path in (ROOT / "plugins").iterdir() if path.is_dir()
    ) if (ROOT / "plugins").is_dir() else []
    directory_names = [path.name for path in plugin_dirs]
    if len(entry_names) != len(set(entry_names)):
        errors.append("marketplace contains duplicate plugin names")
    if set(entry_names) != set(directory_names):
        errors.append("marketplace coverage does not match generated plugin directories")
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("marketplace plugin entries must be objects")
            continue
        name = entry.get("name")
        source = entry.get("source")
        policy = entry.get("policy")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            errors.append(f"marketplace plugin name is invalid: {name!r}")
        if source != {"source": "local", "path": f"./plugins/{name}"}:
            errors.append(f"marketplace source is invalid for {name}")
        if not isinstance(policy, dict) or policy.get("installation") not in {
            "NOT_AVAILABLE",
            "AVAILABLE",
            "INSTALLED_BY_DEFAULT",
        } or policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            errors.append(f"marketplace policy is invalid for {name}")
        if not isinstance(entry.get("category"), str) or not entry["category"].strip():
            errors.append(f"marketplace category is invalid for {name}")

    seen_skills: set[tuple[str, str]] = set()
    for plugin_dir in plugin_dirs:
        portable = load_object(plugin_dir / "plugin.json", errors)
        compatibility = load_object(plugin_dir / ".codex-plugin/plugin.json", errors)
        for manifest_path, manifest in (
            (plugin_dir / "plugin.json", portable),
            (plugin_dir / ".codex-plugin/plugin.json", compatibility),
        ):
            label = manifest_path.relative_to(ROOT)
            if manifest_path.name == "plugin.json" and manifest_path.parent.name == ".codex-plugin":
                allowed = {
                    "id",
                    "name",
                    "version",
                    "description",
                    "skills",
                    "apps",
                    "mcpServers",
                    "interface",
                    "author",
                    "homepage",
                    "repository",
                    "license",
                    "keywords",
                }
                unknown = sorted(set(manifest) - allowed)
                if unknown:
                    errors.append(f"{label}: unsupported fields {unknown}")
            if manifest.get("name") != plugin_dir.name:
                errors.append(f"{label}: manifest name does not match directory")
            if not NAME.fullmatch(plugin_dir.name):
                errors.append(f"{label}: plugin identifier is invalid")
            version = manifest.get("version")
            if not isinstance(version, str) or not SEMVER.fullmatch(version):
                errors.append(f"{label}: version is not strict semver")
            if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
                errors.append(f"{label}: description is required")
            author = manifest.get("author")
            if not isinstance(author, dict) or not isinstance(
                author.get("name"), str
            ) or not author["name"].strip():
                errors.append(f"{label}: author.name is required")
        if portable.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
            errors.append(f"{plugin_dir.name}/plugin.json: portable schema is missing")
        interface = compatibility.get("interface")
        required_interface = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
        }
        if not isinstance(interface, dict) or not all(
            isinstance(interface.get(field), str) and interface[field].strip()
            for field in required_interface
        ):
            errors.append(f"{plugin_dir.name}: Codex interface metadata is incomplete")
        elif not isinstance(interface.get("capabilities"), list) or not isinstance(
            interface.get("defaultPrompt"), list
        ) or not interface["defaultPrompt"] or len(interface["defaultPrompt"]) > 3:
            errors.append(f"{plugin_dir.name}: Codex interface arrays are invalid")
        if compatibility.get("skills") is not None and (
            compatibility.get("skills") != "./skills/"
            or not (plugin_dir / "skills").is_dir()
        ):
            errors.append(f"{plugin_dir.name}: skills path is invalid")
        extension = portable.get("extensions", {}).get("com.openai", {})
        if isinstance(extension, dict) and "hooks" in extension:
            if extension["hooks"] != "./hooks/hooks.json" or not (
                plugin_dir / "hooks" / "hooks.json"
            ).is_file():
                errors.append(f"{plugin_dir.name}: hooks path is invalid")
            else:
                hooks_config = load_object(
                    plugin_dir / "hooks" / "hooks.json", errors
                ).get("hooks")
                if not isinstance(hooks_config, dict):
                    errors.append(f"{plugin_dir.name}: hooks config is invalid")
                else:
                    for event, groups in hooks_config.items():
                        if not isinstance(groups, list):
                            errors.append(
                                f"{plugin_dir.name}: hook groups for {event} must be an array"
                            )
                            continue
                        for group in groups:
                            handlers = group.get("hooks") if isinstance(group, dict) else None
                            if not isinstance(handlers, list):
                                errors.append(
                                    f"{plugin_dir.name}: hook handlers for {event} are invalid"
                                )
                                continue
                            for handler in handlers:
                                kind = handler.get("type") if isinstance(handler, dict) else None
                                if kind not in {"command", "mcp_tool"}:
                                    errors.append(
                                        f"{plugin_dir.name}: unsupported {event} hook handler {kind!r}"
                                    )
                                if kind == "command" and not isinstance(
                                    handler.get("command"), str
                                ):
                                    errors.append(
                                        f"{plugin_dir.name}: {event} command hook lacks command"
                                    )

        skills_root = plugin_dir / "skills"
        if not skills_root.is_dir():
            continue
        for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
            skill_path = skill_dir / "SKILL.md"
            if not skill_path.is_file():
                errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
                continue
            text = skill_path.read_text(encoding="utf-8")
            if "CLAUDE_PLUGIN_ROOT" in text:
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: Claude plugin-root variable was not adapted"
                )
            if (
                "$ARGUMENTS" in text
                or "<absolute-plugin-root>" in text
                or "{ABSOLUTE_PATH_TO_PLUGIN}" in text
            ):
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: unresolved Claude runtime placeholder"
                )
            if "Task tool" in text or "subagent_type" in text:
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: Claude subagent contract was not adapted"
                )
            if (
                "$PLUGIN_ROOT" in text
                and "Codex plugin path" not in text
                and "Codex adaptation" not in text
            ):
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: plugin root lacks Codex resolution guidance"
                )
            if re.search(rf"/{re.escape(plugin_dir.name)}:[a-z0-9-]+", text):
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: Claude slash invocation was not adapted"
                )
            match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not match:
                errors.append(f"{skill_path.relative_to(ROOT)}: invalid frontmatter")
                continue
            name_match = re.search(r"^name:\s*([^\n]+)", match.group(1), re.MULTILINE)
            description_match = re.search(
                r"^description:\s*(?:[^\n]+|[>|][-+]?\n(?:[ \t].*\n?)*)",
                match.group(1),
                re.MULTILINE,
            )
            if not name_match or not description_match:
                errors.append(f"{skill_path.relative_to(ROOT)}: name/description required")
                continue
            skill_name = name_match.group(1).strip().strip("\"'")
            if not NAME.fullmatch(skill_name):
                errors.append(f"{skill_path.relative_to(ROOT)}: invalid skill name {skill_name!r}")
            key = (plugin_dir.name, skill_name)
            if key in seen_skills:
                errors.append(f"{plugin_dir.name}: duplicate skill name {skill_name}")
            seen_skills.add(key)

        agents_root = plugin_dir / "agents"
        if agents_root.is_dir():
            for agent_path in sorted(agents_root.glob("*.md")):
                text = agent_path.read_text(encoding="utf-8")
                forbidden = (
                    "CLAUDE_PLUGIN_ROOT",
                    "$ARGUMENTS",
                    "Task tool",
                    "subagent_type",
                    "TodoWrite",
                )
                leftovers = [value for value in forbidden if value in text]
                if leftovers:
                    errors.append(
                        f"{agent_path.relative_to(ROOT)}: unadapted Claude agent contract {leftovers}"
                    )
                if not text.startswith("---\n"):
                    errors.append(
                        f"{agent_path.relative_to(ROOT)}: adapted agent prompt lacks frontmatter"
                    )

    report = load_object(ROOT / "generation-report.json", errors)
    summary = report.get("summary", {})
    if summary.get("plugins") != len(plugin_dirs):
        errors.append("generation report plugin count is stale")
    if summary.get("skills") != len(seen_skills):
        errors.append("generation report skill count is stale")

    readme_path = ROOT / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"README.md: unable to read ({error})")
    else:
        aliases = {"K.I.S.S.": "kiss"}
        section_counts = {name: 0 for name in directory_names}
        for heading in re.findall(r"^## ([^\n]+)\s*$", readme, re.MULTILINE):
            normalized = aliases.get(heading.strip(), heading.strip())
            if normalized in section_counts:
                section_counts[normalized] += 1
        duplicates_or_missing = {
            name: count for name, count in section_counts.items() if count != 1
        }
        if duplicates_or_missing:
            errors.append(
                "README plugin sections must appear exactly once: "
                f"{duplicates_or_missing}"
            )

    if errors:
        print("Generated plugin validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(plugin_dirs)} plugins and {len(seen_skills)} skills")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Generated repository root to validate",
    )
    arguments = parser.parse_args()
    raise SystemExit(main(Path(arguments.root).expanduser()))
