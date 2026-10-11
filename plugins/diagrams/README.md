# Diagrams

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Diagramming toolkit for Codex. A router skill dispatches diagram requests to format-specific skills: ascii-art (diagrams drawn with extended ASCII box-drawing characters from CP437 — single ┌─┐, double ╔═╗, shading ░▒▓█ — never + - | /, capped at 80 chars with strict row/column alignment), mermaid (flowcharts, sequence, and other Mermaid diagrams), and wardley (Wardley maps in the WTG2 / wardleyToGo DSL, emitted as .wtg2 for rendering to SVG via wtg2svg). Extensible — add a new skill per diagram format and a row to the router table.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add diagrams@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.

---

A diagramming toolkit for Codex. A **router skill** takes a "draw X" request, picks the right
diagram format, and dispatches to a format-specific skill.

## Skills

| Skill | Purpose |
|-------|---------|
| `$diagrams` | Router — detects the requested format and routes to the skill below. |
| `$diagrams:ascii-art` | Text/box-drawing diagrams that render inline (terminal or code block). |
| `$diagrams:mermaid` | Mermaid diagrams (flowchart, sequence, class, ER, state, gantt) for Markdown/docs rendering. |
| `$diagrams:wardley` | Wardley maps in the WTG2 (wardleyToGo) DSL, emitted as `.wtg2` (renders to SVG via `wtg2svg`). |

## ascii-art rules

The ASCII-art skill enforces rules that keep text diagrams clean:

1. **Extended ASCII box-drawing only (CP437 codes > 128), never `+`, `-`, `|`, or `/`.** Draw with
   `┌ ┐ └ ┘ ─ │` and joins `├ ┤ ┬ ┴ ┼`, double-line `╔ ═ ╗ ║ ╚ ╝` for highlighted/outer
   containers, and shading `░ ▒ ▓ █` — not ASCII punctuation.
2. **Maximum width 80 characters**, monospaced fonts only.
3. **Strict alignment.** Verticals must share a column and horizontals a row — the most common
   failure is a line drifting off by a cell; the skill makes alignment a final validation step.

## Adding a format

Add a `skills/<format>/SKILL.md` with a sharp `description:` (that is what triggers routing), then
add a row to the detection table in `skills/diagrams/SKILL.md`.

## Status

Infrastructure and all three skills (`ascii-art`, `mermaid`, `wardley`) are complete.
