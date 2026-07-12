# ADR 0002: Evidence before candidate and bounded continuity

Status: Accepted
Date: 2026-07-12

## Context

The first SushuFlash dogfood run failed after candidate implementation began before the mandatory GCW teardown and companion results were complete. The agent treated questions about unrelated URL/image-to-code skills as permission to invoke them, delayed mandatory Design DNA, did not promptly apply the conditional Web Shader Extractor decision, captured an unstable loading frame, and stopped while visual QA still failed.

This is not an allowed GCW outcome, but it is a repeatable agent-compliance risk when a long reconstruction relies on conversational memory instead of machine gates and persisted state.

## Decision

- GCW is authoritative when explicitly selected. Questions about adjacent skills do not invoke them, and no adjacent skill replaces `design-dna` or conditionally required `web-shader-extractor`.
- URL-only `CLEAN_REBUILD` cannot begin candidate implementation before teardown finalization and complete public runtime evidence.
- Critical source baselines require repeated ready-state capture. Dynamic regions must be stabilized or classified separately.
- Formal review requires a confirmed `quality-gate.json` with a stable source baseline, passed verification, and no open P0/P1/P2.
- Failed visual or interaction QA keeps work in `FAITHFUL_CLONE` until fixed or explicitly paused/terminated by the user.
- Large or multi-session work uses one compact `PROGRESS.md`, a state validator, and only user-authorized local Git checkpoints. Per-tweak reports and automatic commits are rejected as process overhead.

## Consequences

Quality-critical failures become machine-visible before review, companion substitution is explicitly forbidden, and long work can resume from local evidence without multiplying documentation. The protocol adds one small quality artifact and an optional progress ledger; it does not add a generic crawler, universal interaction engine, or automatic version-control system.
