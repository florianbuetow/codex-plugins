---
name: scout
description: "Scout a codebase and produce a ranked map from codebase to tasks, each tagged with a recommended model. Identifies work; does not fix it."
---

## Codex adaptation

This workflow was generated from a Claude Code slash command. Use the arguments in the invoking request wherever the workflow refers to the current request's arguments. When it names a bundled agent, use the matching generated skill and delegate that bounded work to a Codex native subagent.


Run the **codebasescout** pipeline on the target below.

Target / objective:
"""
the current request's arguments
"""

Launch the **scout-router** agent, which orchestrates the team: it guards the target, gates scan-vs-skip, sweeps and scores files by Impact x Opportunity with cheap models, ranks them, groups recurring classes, writes concrete tasks, and tags each task with a recommended model. The deliverable is `.codebasescout/run/tasks.md` -- a ranked map from codebase to tasks with model recommendations.

Hard rule: codebasescout **only identifies work and recommends a model per task. It must not fix, edit, refactor, or modify any code.** If the objective is unclear, infer the most likely one and state your assumption. When the map is ready, present it inline.
