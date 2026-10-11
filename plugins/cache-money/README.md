# Cache Money

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Keep the Anthropic prompt cache warm during Claude Code sessions — especially during peak hours when usage limits are tighter. Detects your cache TTL (5-min default or 1-hour extended) and schedules pings accordingly, reducing token costs by up to 90% on cached context.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add cache-money@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
