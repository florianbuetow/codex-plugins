# Logbook

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Analyze Claude Code session logs to generate per-project time and message reports. Breaks down usage by project and branch, groups branches under their parent project, and produces monthly + yearly markdown reports.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add logbook@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
