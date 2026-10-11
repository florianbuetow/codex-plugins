# Clean Code

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Analyze source code against Robert C. Martin's Clean Code across nine dimensions: Meaningful Names, Functions, Comments, Formatting, Objects & Data Structures, Error Handling, Boundaries, Unit Tests (F.I.R.S.T.), and Concurrency. Reports structured, actionable findings rated HIGH / MEDIUM / LOW, each with a code location, a verified book reference, the issue, and a concrete refactoring step. A book reference is quoted verbatim from the bundled Chapter 17 registry - a real heuristic code (G30, N5, C3) where the catalog defines one, otherwise a canonical chapter rule (Ch.7: Don't Ignore Caught Errors) - never a synthesised identifier. Findings route by the smallest refactoring edit that resolves them; class, system and architecture concerns are out of scope. Self-contained: the skill and its references bundle everything it uses.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add clean-code@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
