# SITE_SPEC and teardown artifact contract

## Authority boundaries

- `.gcw/SITE_SPEC.md` is the single human-readable implementation specification.
- `.gcw/teardown-manifest.json` is the machine-readable teardown gate.
- `.gcw/evidence/evidence-index.json` indexes artifacts and checksums.
- Companion Skill artifacts remain authoritative for their native schemas. SITE_SPEC summarizes and links them; it never reproduces them wholesale.

Initialize SITE_SPEC as a draft and finalize it only after the complete teardown sequence. Standard and deep teardown keep all 12 numbered sections. The opt-in minimal profile is limited to simple non-GPU pages and keeps sections 1, 5, 9, and 12. Remove every `REQUIRED` placeholder and write `N/A` only with supporting evidence.

## Fixed evidence

Every task preserves:

```text
.gcw/evidence/
├─ evidence-index.json
├─ site-inventory.json
├─ route-map.json
├─ source-maps.json
├─ interaction-states.json
├─ screenshots/desktop/
├─ screenshots/mobile/
├─ network/
├─ design-dna/design-dna.json
└─ web-shader-extractor/gpu-decision.json
```

Run `design-dna` during standard and deep teardown and keep its complete three-dimension JSON. It is recommended but non-blocking for minimal teardown. SITE_SPEC section 4 summarizes only implementation-critical Design System, Design Style, and Visual Effects findings.

When a Canvas/WebGL/WebGPU/shader target exists, set `gpu-decision.json.decision` to `required`, run `web-shader-extractor`, and preserve its native `scout-card.json`, `replay-manifest.json`, `run-state.json`, and evidence tree in the same namespace. Before finalizing teardown, `scout-card.json` must be `TARGET_LOCKED`, `replay-manifest.json` must be `REPLAY_READY`, and no blocking replay unknown may remain. Raw Replay and QA belong to the faithful baseline phase.

When reconnaissance confirms no qualifying GPU surface, set the decision to `not-applicable` and record checked surfaces plus detection-evidence paths. Do not create fake Shader artifacts.

## Interaction-state schema

`interaction-states.json` uses schema version 1 and requires at least one observed state. Every state records the route, trigger, expected result, and evidence paths:

```json
{
  "schemaVersion": 1,
  "states": [
    {
      "id": "menu-open",
      "route": "/",
      "trigger": "click header menu button",
      "expected": "navigation overlay is visible",
      "evidence": ["screenshots/mobile/menu-open.png"]
    }
  ]
}
```

## SITE_SPEC synthesis rules

- Design DNA answers what the design looks and feels like.
- Web Shader Extractor answers how the target rendering system actually runs.
- For implementation facts, target-bound Shader evidence outranks qualitative Design DNA inference.
- Record conflicts; never average them.
- Represent every implementation-critical conclusion in the subsystem table. Record both fidelity (`Exact`, `Approximate`, `Unknown`, `Excluded`) and truth (`SOURCE`, `PARTIAL`, `GUESS`).
- Classify unknowns as blocking, important, deferred, or external.

Add full route maps, motion state timelines, asset manifests, provenance/hashes, and recovery strategy only when their documented conditions apply.
