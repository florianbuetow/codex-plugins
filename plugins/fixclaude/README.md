# Fixclaude

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Reverse the built-in Claude Code limitations discovered in the source code leak. Installs production-grade agent directives that override verification gates, context decay, brevity mandates, and silent truncation — the same fixes Anthropic uses internally.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add fixclaude@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.

---

Reverse the built-in Claude Code limitations discovered in the source code leak.

Installs production-grade agent directives that override verification gates,
context decay, brevity mandates, and silent truncation -- the same fixes
Anthropic uses internally but gates behind employee-only flags.

## What It Fixes

Based on reverse-engineering the Claude Code source against real agent logs
([original analysis by @fakeguru](https://x.com/iamfakeguru/status/2038965567269249484)):

| # | Problem | Root Cause | Override |
|---|---------|-----------|----------|
| 1 | "Done!" with 40 type errors | Verification gated to employees (`USER_TYPE=ant`) | Forced verification loop |
| 2 | Hallucinations after ~15 messages | Auto-compaction nukes context at ~167K tokens | Step 0 cleanup + phased execution |
| 3 | Band-aid fixes, no real solutions | System prompt mandates minimal intervention | Senior dev quality override |
| 4 | Context decay on large refactors | Users default to single-agent sequential | Sub-agent swarming (5-8 files/agent) |
| 5 | Edits reference code it never saw | File reads capped at 2,000 lines | Chunked reads with offset/limit |
| 6 | grep finds 3 results, there are 47 | Tool results truncated to 2,000-byte preview | Narrow scoping + truncation awareness |
| 7 | Rename misses dynamic imports | grep is text matching, not an AST | Multi-search mandate per reference type |

## Commands

| Command | What it does |
|---------|-------------|
| `$fixclaude` | Auto-detect and install (routes to init or update) |
| `$fixclaude:init` | Create a new CLAUDE.md with full production-grade directives |
| `$fixclaude:update` | Augment an existing CLAUDE.md with missing overrides |
| `$fixclaude:analyze` | Gap analysis: check your CLAUDE.md against all 7 findings |

All commands handle CLAUDE.md symlinks transparently (e.g., CLAUDE.md -> AGENTS.md).

## CLAUDE.md Template

The directives installed by `init` cover 9 areas:

1. **Pre-Work** -- Step 0 cleanup, phased execution, spec-based development
2. **Understanding Intent** -- Follow references, work from raw data, one-word mode
3. **Code Quality** -- Senior dev override, forced verification, write human code
4. **Context Management** -- Sub-agent swarming, context decay awareness, file read budget
5. **File System as State** -- Use disk for memory, intermediate results, progressive disclosure
6. **Edit Safety** -- Edit integrity, no semantic search assumptions, one source of truth
7. **Prompt Cache Awareness** -- Avoid cache invalidation, use /compact and context-log.md
8. **Self-Improvement** -- Mistake logging, bug autopsy, failure recovery
9. **Housekeeping** -- Autonomous bug fixing, parallel batch changes, file hygiene

## Attribution

The CLAUDE.md template content is based on work by
[fakeguru](https://github.com/iamfakeguru/claude-md), released under the MIT License.
Copyright (c) 2026 fakeguru.

## License

[MIT](LICENSE)
