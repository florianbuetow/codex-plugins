# Communicator

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Communication-style toolkit for Codex. The tldr skill switches Codex into a military-style BLUF (Bottom Line Up Front) mode: extreme brevity, conclusion first, bullets over prose, runnable commands in code blocks, and ruthless cutting of filler, preambles, and hand-holding. Fires on "tldr", "short mode", or "be brief".

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add communicator@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.

---

A communication-style toolkit for Codex. One skill for now.

## Skills

| Skill | Purpose |
|-------|---------|
| `$communicator:tldr` | Switch Codex into a military-style BLUF (Bottom Line Up Front) mode — extreme brevity, no filler. |

## tldr

The `tldr` skill enforces terse, instantly-parseable output:

- **Critical issues first** — real bugs and blockers as a bullet list, not preferences.
- **Actionable next step** — the exact command, file change, or decision needed.
- **Bottom line last** — a one-sentence conclusion, status, or answer on its own line.
- **No filler** — cuts preambles, recaps, meta-commentary, politeness padding, and over-explanation.

### Triggering

The skill fires when you type any of:

- `tldr` or `$tldr`
- `short mode`
- `be brief`
- `concise mode`

…or otherwise ask for terse, no-fluff output. Once active, it shapes the response style until you ask for normal output.
