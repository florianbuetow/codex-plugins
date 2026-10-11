# Intent

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Intent-based task resolution. When stuck, facing ambiguity, or about to ask a clarifying question, first recover the task's underlying intent from available context - the latest prompt, earlier prompts, project goals, plans, and prior corrections - then answer low-risk questions from that intent and make intent-aligned decisions. Escalate to the user only when the ambiguity is material and cannot be resolved from context; and when neither the intent nor a safe default can be inferred at all, an escape hatch stops and names the gap rather than fabricating an answer.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add intent@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
