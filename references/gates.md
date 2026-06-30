# Gates

Do not advance when a required artifact is missing.

| Gate | Required proof | Blocking failures |
|---|---|---|
| Scope | Permission boundary, routes, workspace | Unknown authorization or target |
| Discovery | Automatic route/resource inventory plus manual verification | Missing public route or critical resource class |
| Target lock | Surface inventory, ablation, owner/backend | Wrong or ambiguous visual surface |
| Replay ready | Render graph or explicit fallback, assets, inputs, output model | Missing critical shader, resource or wiring |
| Baseline verified | Build, GPU, structural, visual, temporal and interaction checks | Any open P0/P1/P2 |
| Project verified | Baseline-to-project regression and route tests | Regression or broken build |
| Automation ready | Repeatable capture config, deterministic seed/phase and diff report | Manual-only comparison with no recorded conditions |
| Closeout | Handoff, known gaps, Git status, deploy notes | Unreported skipped work |

## Severity

- `P0`: cannot run, render or reach the route.
- `P1`: wrong target, graph, composition or primary interaction.
- `P2`: visible layout, timing, color, responsive or input drift.
- `P3`: non-blocking polish, performance or unavoidable external difference.

Record facts as `SOURCE`, `PARTIAL` or `GUESS`. Never promote a fitted value to `SOURCE`.
