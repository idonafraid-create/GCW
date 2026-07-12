# Long-running continuity

Use this protocol only for large or multi-session work: multiple page families, GPU rendering, more than five material subsystems, or an expected handoff/context reset. Small work keeps the normal GCW artifacts and does not need extra process.

Copy `assets/progress-template.md` to `.gcw/PROGRESS.md`. Keep one row per independently verifiable subsystem. Update it only when a subsystem starts, becomes verified, or is blocked; link existing evidence instead of duplicating reports.

On resume or handoff:

1. Read `run-state.json`, `SITE_SPEC.md`, `PROGRESS.md`, the latest relevant QA evidence, and `CLONE_REPORT.md` when it exists.
2. Run `python <skill-root>/scripts/validate_workspace_state.py <workspace>`.
3. Re-run the smallest verification that proves the last verified subsystem still holds.
4. Continue only the single `in_progress` subsystem or select the next dependency.

Ask before creating local Git commits. Permission for local checkpoints does not authorize push, tag, release, or deploy. When local commits are allowed, prefer only these checkpoints: after finalized teardown, before a risky rendering/architecture change, and before `REVIEW_GATE`. Add an extra module checkpoint only when it provides a meaningful independent rollback point. Never auto-commit each tweak.
