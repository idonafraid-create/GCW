# Workflow phases and outcomes

GCW uses one staged workflow, not four parallel modes:

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

`TEARDOWN_PHASE` is mandatory. A study-only task stops there and may be described externally as `TEARDOWN`. `FAITHFUL_CLONE` may be the final outcome or the baseline for later creative work. Never enter `CREATIVE_REBUILD` until the user accepts the baseline at `REVIEW_GATE`.

## Visible preflight

Show `Outcome`, `Current phase`, `Site type`, `Ownership/authorization`, `Source availability`, `Baseline scope`, `Implementation path`, and `Approximate or excluded scope`. Ask one path-changing question when intent or authorization is ambiguous. Record scope changes.

## Faithful implementation paths

| Condition | Path |
|---|---|
| Reusable official source is legally available | `SOURCE_ADAPT` |
| Public evidence is sufficient for a clean implementation | `CLEAN_REBUILD` |
| User confirms ownership/authorization and maintainable source is unavailable | `PRODUCTION_RECOVERY` |

`PRODUCTION_RECOVERY` is a conditional recovery configuration, never a user-facing parallel mode. Read `recovery-tiers.md` and `gates.md` only when both recovery conditions are met.

## Review gate choices

- Fidelity insufficient: return to `FAITHFUL_CLONE`.
- Baseline accepted as final: stop.
- Baseline accepted for innovation: create `.gcw/CREATIVE_BRIEF.md`, then enter `CREATIVE_REBUILD`.
