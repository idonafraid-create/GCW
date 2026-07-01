# Production recovery strategies

These strategies belong to `PRODUCTION_RECOVERY`. They are implementation choices, not the default goals for teardown, faithful-clone or creative-rebuild projects.

## ARTIFACT_REPLAY

Serve exact public HTML, CSS, JavaScript and assets when deployed artifacts are the only reliable runnable implementation.

Use it as an independent regression oracle. Do not call minified deployment artifacts the original authoring source.

Limits:

- Original source names, comments, history and server logic may be unavailable.
- Static hosting may require route documents or navigation adaptation.
- Public availability does not grant permission to redistribute third-party assets.

## PIPELINE_REPLAY

Reconstruct the active rendering pipeline from recovered shaders, resources, state, timing and input wiring. Use when production artifacts cannot run locally or when GPU code must become editable.

Do not begin from screenshots alone when source maps, runtime captures or deployed code are available.

## EDITABLE_REBUILD

Convert verified behavior into maintainable components. Keep the best available replay or captured baseline as an oracle and compare after each projectization step.

An editable rebuild is complete only when it passes the desktop, mobile, temporal, interaction and route scenarios promised in preflight.

## Selection rule

Choose the strategy that produces the required outcome with the strongest available evidence. These strategies may be sequential: establish artifact replay as an oracle, recover a specialized pipeline, then replace sections with editable components. Do not describe them as a universal quality ranking.
