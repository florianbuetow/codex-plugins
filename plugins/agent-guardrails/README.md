# Agent Guardrails

> Generated for Codex from the canonical source plugin. Run `just update` at the marketplace root to refresh it.

Run this workflow from Codex. Behavioral guardrails for Claude Code agents. Nine battle-tested rules (no-guessing, no-stalling, no-preference-asking, no-false-completion, no-skipping, no-dismissing, no-cosmetic, no-caveats, no-flagging) enforced via a Stop hook bash script. Includes analyze, install, test, and update skills for data-driven tuning.

> **Compatibility scope:** This plugin runs as a Codex skill but intentionally operates on Claude Code files, sessions, processes, or service behavior. Those source-domain references are preserved rather than relabeled as unsupported Codex runtime behavior.

## Install with Codex

Register the repository marketplace with `codex plugin marketplace add .`, then run `codex plugin add agent-guardrails@florianbuetow-codex-plugins` or install it from **Florian Buetow Codex Plugins** in the Plugins Directory. Invoke its workflows with `$<skill-name>`.

---

Behavioral guardrails for Claude Code agents. Nine battle-tested rules enforced via a Stop hook bash script, with skills for data-driven analysis and tuning.

## How It Works

Guardrails are enforced by a single bash script registered as a Claude Code [Stop hook](https://developers.openai.com/codex/hooks). When the assistant finishes a response, the script checks the output against regex patterns and blocks responses that contain anti-patterns.

**No external plugin dependencies** — just bash, jq, and grep.

```
Assistant response -> Stop hook -> stop-guardrails.sh -> block / allow
```

## Rules

| Rule | What It Catches |
|------|----------------|
| `no-guessing` | Hedging, guessing, unverified claims ("probably", "I think", "this should work") |
| `no-stalling` | Padding before action ("before I proceed", "a few things to consider") |
| `no-preference-asking` | Delegating decisions to the user ("would you prefer", "shall I") |
| `no-false-completion` | Claiming completion without evidence ("all done", "fully implemented") |
| `no-skipping` | Skipping work or hand-waving ("the rest looks fine", "for brevity") |
| `no-dismissing` | Dismissing issues without investigation ("not a real bug", "can be ignored", "just a warning") |
| `no-cosmetic` | Calling anything cosmetic ("cosmetic", "cosmetically") |
| `no-caveats` | Reporting caveats instead of acting on them ("one caveat", "with the caveat that") |
| `no-flagging` | Flagging issues instead of resolving them ("just to flag", "flagging this", "I have flagged") |

## Quick Start

```
$agent-guardrails:install     # Install all nine rules into your project
$agent-guardrails:analyze     # Scan session logs for anti-patterns
$agent-guardrails:update      # Tune rules based on real usage data
```

### Install

Copies a bundled bash script to `.claude/hooks/stop-guardrails.sh` and registers it in `.claude/settings.local.json`. Specify rule names to install a subset, or run with no arguments for all nine.

### Analyze

Scans recent Claude Code session logs for anti-pattern frequency. Produces a ranked report with match counts, example excerpts, and recommendations for which rules to install.

### Update

Re-analyzes session logs against your installed rules. Identifies false positives (pattern too aggressive), false negatives (pattern too lenient), and uncovered gaps. Applies refinements to the bash script directly.

## Files

After installation, your project will have:

```
.claude/
  hooks/
    stop-guardrails.sh      # The enforcement script (edit to customize)
  settings.local.json        # Stop hook configuration
```

## Customization

Edit `.claude/hooks/stop-guardrails.sh` directly. Each rule is a grep block:

```bash
# no-guessing
if echo "$message" | grep -qiE '(pattern...)'; then
  blocked+=("**no-guessing**: Message...")
fi
```

Add, remove, or modify blocks as needed. Changes take effect immediately.

## License

[MIT](LICENSE)
