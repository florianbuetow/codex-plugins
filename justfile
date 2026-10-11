set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

source := env_var_or_default("CLAUDE_CODE_REPO", "../claude-code")

default:
    @just --list

# Regenerate every Codex plugin and README from the read-only Claude source.
update:
    @python3 scripts/sync_plugins.py --source "{{source}}"

# Fail when generated output is stale or structurally invalid.
check:
    @python3 scripts/sync_plugins.py --source "{{source}}" --check
    @python3 scripts/validate_generated.py

# Run the generator regression suite.
test:
    @python3 -m unittest discover -s tests -v

# Regenerate, validate, and run tests.
ci: update check test
    @printf "\033[32m✓ Codex plugin generation is reproducible and valid\033[0m\n"

