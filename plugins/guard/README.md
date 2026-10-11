# Guard

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Helper skill for the `guard` CLI (https://github.com/florianbuetow/guard), a file-permission tool that protects files from accidental modification by AI agents via immutable flags and root ownership. Composes guard commands for five intents — init, create-collection, remove-collection, clear-all, info — running registry operations directly and printing `sudo guard` commands for operations that need root.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add guard@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.
