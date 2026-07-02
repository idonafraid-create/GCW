# QA scenarios

Record fixed viewport, DPR, browser/backend, theme, route, crop, readiness, pointer, scroll, seed, and time phase in capture JSON.

| Phase | Required verification |
|---|---|
| `TEARDOWN_PHASE` | Evidence for every claim, mandatory `design-dna`, and completed or evidence-backed `N/A` GPU analysis |
| `FAITHFUL_CLONE` | Desktop, mobile, key interactions, routes, build, numeric and visual Diff |
| `REVIEW_GATE` | Preview, screenshots, Diff, `CLONE_REPORT.md`, Known Gaps |
| `CREATIVE_REBUILD` | Accepted baseline plus final desktop/mobile and critical paths |
| Recovery configuration | Full route/deployment continuity and maintained regression CI |

Verify loading, startup, primary interaction, completion/reset, mute when present, reduced-motion or low-performance behavior, and asset/network failure states. Mark absent capabilities `N/A`.

For random or compositor-driven effects, inject the same deterministic RNG when safe, freeze time only after readiness, and record phase-sensitive regions separately. Inspect Diff images; never accept a single global score as proof.
