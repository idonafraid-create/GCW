# ADR 0001: Staged workflow and conditional gates

Status: Accepted  
Date: 2026-07-02

## Context

GCW previously presented teardown, faithful cloning, creative rebuilding, and production recovery as parallel modes. That mixed workflow phases, desired outcomes, and source-availability conditions. It also left evidence depth and phase transitions too dependent on agent judgment.

## Decision

Use one visible staged workflow:

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

- Teardown is mandatory but may be the final outcome.
- Production recovery is an implementation path enabled only for authorized work with unavailable or damaged maintainable source.
- The review gate requires baseline evidence and an explicit A/B/C user decision.
- Design evidence is required for standard and deep teardown; GPU forensics is conditional on detected Canvas, WebGL, WebGPU, or shader surfaces.
- Evidence remains in native companion schemas and is summarized, not duplicated, in SITE_SPEC.
- Runtime independence applies to final clean and creative rebuilds, not teardown itself.

## Consequences

The workflow has one source of truth, phase changes are auditable, and expensive gates apply only when target complexity warrants them. Simple non-GPU pages may opt into the minimal teardown profile while preserving the evidence tree, subsystem fidelity table, and finalization gate.
