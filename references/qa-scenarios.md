# QA scenarios

Record fixed viewport, DPR, browser/backend, theme, route, crop, readiness, pointer, scroll, seed, and time phase in capture JSON.

Before candidate implementation, capture every critical source scenario twice after fonts and visible images decode and the documented readiness condition passes. If the pair is not stable, correct the wait/seed/virtual-time inputs or record the unstable region as phase-sensitive and exclude it from static global acceptance. Preserve both captures or their Diff as `quality-gate.json` evidence. One early loading or transition frame is never an acceptable baseline.

For an internal GCW dogfood run, copy `assets/dogfood-record.template.md` into the case workspace before teardown. Record timing, human intervention, discovery false positives/misses, verification results, and the roadmap decision. This is an internal quality record, not an end-user deliverable.

| Phase | Required verification |
|---|---|
| `TEARDOWN_PHASE` | Evidence for every claim, mandatory `design-dna`, and completed or evidence-backed `N/A` GPU analysis |
| `FAITHFUL_CLONE` | Desktop, mobile, key interactions, routes, build, numeric and visual Diff |
| `REVIEW_GATE` | Preview, screenshots, Diff, `CLONE_REPORT.md`, Known Gaps |
| `CREATIVE_REBUILD` | Accepted baseline plus final desktop/mobile and critical paths |
| Recovery configuration | Full route/deployment continuity and maintained regression CI |

Verify loading, startup, primary interaction, completion/reset, mute when present, reduced-motion or low-performance behavior, and asset/network failure states. Mark absent capabilities `N/A`.

`detect_interaction_states.mjs` may seed teardown evidence for direct hover/focus styles and common expanded controls. Treat every generated state as a candidate until its before/after screenshots are reviewed; automated discovery does not replace critical-path interaction QA.

For random or compositor-driven effects, inject the same deterministic RNG when safe, freeze time only after readiness, and record phase-sensitive regions separately. Inspect Diff images; never accept a single global score as proof.
