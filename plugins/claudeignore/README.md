# Claudeignore

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Generate and maintain .claudeignore files for Claude Code projects. Analyzes repository structure to identify directories that waste context tokens (caches, build artifacts, large non-source directories) and produces a categorized .claudeignore file.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add claudeignore@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
