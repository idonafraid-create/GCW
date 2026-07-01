# Clone modes

Choose the user's goal before choosing tools. The mode defines what evidence, implementation and deliverables are proportionate.

## TEARDOWN

Use when the user primarily wants to learn how a site works.

- Identify the real stack, page structure, motion system and advanced rendering surfaces.
- Separate transferable techniques from site-specific code, branding and assets.
- Produce `TEARDOWN.md`; a runnable clone is optional.
- Verify every important claim against source or runtime evidence.

## FAITHFUL_CLONE

Use when observable fidelity is the main result.

- Preserve in-scope layout, routes, responsive behavior and interaction states.
- Prefer official reusable source; otherwise reconstruct from public runtime evidence.
- Keep reference artifacts separate from editable code.
- Produce a runnable project and `CLONE_REPORT.md` with known gaps.

## CREATIVE_REBUILD

Use when the user wants to learn from a reference and make a distinct site.

- Extract the useful information architecture, rhythm, interaction grammar and visual principles.
- Replace the original brand, copy and restricted assets.
- Use Design DNA as a specification for a new implementation, not as evidence of byte-level fidelity.
- Produce `DESIGN_DNA.json`, a runnable project and `REPLACE_GUIDE.md` when replacement points are non-obvious.

## PRODUCTION_RECOVERY

Use when an owned deployed site must be recovered because maintainable source is missing or unusable.

- Preserve production artifacts and provenance when they are needed as a recovery oracle.
- Read `recovery-tiers.md` and select the appropriate replay or rebuild strategy.
- Require route, state and deployment verification plus a complete known-gaps record.
- Add CI screenshot regression when the recovered project will be maintained.

## Switching modes

A project may start as `TEARDOWN` and continue as `CREATIVE_REBUILD` or `FAITHFUL_CLONE`. Record the switch instead of silently expanding scope. `PRODUCTION_RECOVERY` is not the default escalation path for ordinary learning projects.
