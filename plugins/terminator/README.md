# Terminator

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Stop hooks that terminate a Claude Code session when the agent's final message contains a kill phrase. Two scripts: single-kill (ends Claude) and double-kill (ends Claude plus the terminal shell that launched it), each bound to its own phrase. Installs at local (project) or global (user) scope; scripts require LOCAL or GLOBAL arg and exit 1 if missing. Contains-match (robust to model preambles), case-sensitivity configurable, and a kill path that walks the process tree to the owning claude (and, for double-kill, the top-most shell ancestor) and never signals pid <= 2. Install, remove, update, info, and whendone skills via a router; composes safely with existing Stop hooks.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add terminator@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.

---

Claude Code Stop hooks that **terminate a session** — and optionally its terminal — when the
agent's final message contains a kill phrase.

## Two scripts, you choose by installing

| Script | On phrase match |
|--------|-----------------|
| `single-kill.sh` | Terminates Claude. Terminal stays open. |
| `double-kill.sh` | Terminates Claude, then the terminal shell that launched it. |

Behaviour is chosen by **which script you install**, each bound to its **own phrase** — not by a
runtime flag. Install one or both.

## Matching

The hook fires when the agent's final message **contains** the configured phrase (case-sensitivity
configurable). Contains-match is used deliberately: models often prepend text like "I'll provide
the requested output," which would defeat a whole-message exact match.

Choose a memorable, rare phrase — a movie quote or a sentence unlikely to appear in normal output.
The install and update skills warn you if you pick something too common; single common words like
`done`, `finished`, or `stop` will cause sessions to terminate at seemingly random moments.

## How termination works

- Walks up the process tree to the owning `claude` process and signals it (SIGTERM, then SIGKILL).
- `double-kill.sh` additionally walks to the **top-most shell ancestor** (the terminal's
  controlling shell — robust to any wrapper/launcher between it and Claude) and signals that too,
  ~1s after Claude.
- **Never signals pid ≤ 2** (init/launchd/kernel) — the one hard safety rule.

> macOS note: killing the shell ends the shell *session*. Whether the Terminal *window* then
> closes depends on the terminal app's profile ("When the shell exits" → "Close the window").
> A process cannot close a GUI window with a signal.

## Usage (skills)

| Skill | Purpose |
|-------|---------|
| `$terminator:install` | Install single-kill and/or double-kill, each with its phrase. |
| `$terminator:update`  | Change a phrase or case sensitivity (live, no restart). |
| `$terminator:remove`  | Uninstall, leaving other Stop hooks intact. |
| `$terminator:whendone`| Arm the session to self-terminate once work is finished. |

## Files it writes (project-local)

```
.claude/hooks/single-kill.sh   and/or   .claude/hooks/double-kill.sh
.claude/terminator.json        # { single_killphrase, double_killphrase, case_sensitive }
.claude/settings.local.json    # Stop hook entries (merged in, never clobbering others)
```

## Requirements

`bash`, `jq`, and standard POSIX tools (`ps`, `kill`). macOS and Linux (the macOS path is
covered by tests; the Linux path uses the same POSIX `ps` interface).
