# Codebasescout

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Scout a codebase to identify high-value work, plan the fixes (point and architectural), and produce a ranked map from codebase to tasks -- each tagged with a recommended model -- without ever implementing the fix. Cheap-model agents sweep and score every file by Impact x Opportunity (1-5); the router then runs meta-level pattern analysis, plans point and architectural fixes, and recommends a model per task. Team: target guard, skip gate, formula, profile, parallel scorers, ranker, pattern-grouper (meta-level analysis + architectural fix planning), task-writer (point-fix planning), model-recommender. Objectives: bugs, security, tech debt, dead code, performance, conversion.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add codebasescout@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
