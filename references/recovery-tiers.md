# Recovery tiers

## ARTIFACT_REPLAY

Use exact public HTML, CSS, JavaScript and assets. This is the fastest path to observable fidelity and the preferred independent baseline.

Limits:

- Minified code is not the original authoring source.
- Original server APIs and source history may be unavailable.
- Static hosting may require route documents or navigation adaptation.

## PIPELINE_REPLAY

Reconstruct the active rendering pipeline using recovered shaders, resources, state, timing and input wiring. Use when production artifacts cannot run locally or when GPU code must become editable.

Do not begin from screenshots alone when source/runtime evidence is available.

## EDITABLE_REBUILD

Convert the verified behavior into maintainable components. Keep the artifact replay as an oracle and compare after each projectization step.

An editable rebuild is complete only when it passes the same desktop, mobile, temporal, interaction and route scenarios as the baseline.

## Selection rule

Choose the highest tier supported by evidence. A project may ship artifact replay first and continue toward editable rebuild without discarding the verified baseline.

