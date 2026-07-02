# Workflow gates

| Gate | Required proof | Blocking failure |
|---|---|---|
| Teardown complete | Passed `teardown-manifest.json`, final `SITE_SPEC.md`, complete Design DNA, and Shader `TARGET_LOCKED` + `REPLAY_READY` or evidence-backed GPU `N/A` | Missing artifact, placeholder, blocking unknown, companion gate, or critical evidence |
| Baseline verified | Build, routes, desktop/mobile/key-state comparison, subsystem fidelity table | Open P0/P1/P2 or unreported approximation |
| Review | Preview, screenshots, Diff, `CLONE_REPORT.md`, Known Gaps | User has not chosen A, B, or C |
| Creative brief | Keep/remove/change/new direction and final acceptance target | Missing explicit user decision |
| Runtime independence | No source-origin requests except explicit legal allowlist | Undeclared source runtime dependency |
| Closeout | Handoff, known gaps, Git status, deploy notes | Skipped work not reported |

Recovery configuration additionally requires provenance/hashes, replay strategy, complete routes, deployment continuity, and long-term regression CI. Do not impose those recovery gates on ordinary reconstruction.

Severity: `P0` cannot run; `P1` wrong target or primary behavior; `P2` visible layout/timing/responsive/input drift; `P3` non-blocking polish. Record facts as `SOURCE`, `PARTIAL`, or `GUESS`.
