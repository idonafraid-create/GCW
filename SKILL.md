---
name: gcw
description: Analyze, reproduce, recover, and creatively adapt authorized public websites through a staged, evidence-driven workflow. Use for GCW, website teardown or cloning, faithful baselines, design-DNA extraction, WebGL/Canvas/shader reverse engineering, source-loss recovery, route reconstruction, and source-versus-local visual regression.
---

# GCW — Gao Copy Website

Find evidence before implementation. Make it run before refactoring. Compare before polishing.

## Boundaries

- Proceed only for user-owned, licensed, or explicitly authorized targets. Ask when authorization is ambiguous.
- Exclude private/authenticated content unless explicitly authorized. Never bypass access controls or handle credentials.
- Check code, font, image, model, and brand rights separately. Label claims `SOURCE`, `PARTIAL`, or `GUESS`.
- Treat deployed bundles as evidence, not original authoring source.

## 1. Route the workflow visibly

Read `references/clone-modes.md`. Show this preflight before using tools:

```markdown
- Outcome:
- Current phase:
- Site type:
- Ownership/authorization:
- Source availability:
- Baseline scope:
- Implementation path:
- Approximate or excluded scope:
```

Ask one path-changing question when intent or ownership is unclear. Use the single flow `TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD`. A teardown-only outcome stops after the first phase. Never silently expand scope.

Choose the faithful implementation path from evidence: `SOURCE_ADAPT`, `CLEAN_REBUILD`, or `PRODUCTION_RECOVERY`. Enable recovery only when the user confirms ownership/authorization and maintainable source is unavailable.

## 2. Establish the specification

Read workspace agent instructions (`AGENTS.md` or `CLAUDE.md`), if present. Let `<skill-root>` mean the directory containing this SKILL.md, then initialize without overwriting evidence:

```text
python <skill-root>/scripts/init_reconstruction.py <workspace> --url <canonical-url> --authorization <owned|licensed|authorized>
```

Choose `--teardown-depth minimal` only for a simple non-GPU page: it uses a four-section SITE_SPEC and makes Design DNA recommended rather than blocking. `standard` is the default complete 12-section teardown. Use `deep` for complex rendering or recovery evidence; GPU targets cannot use `minimal`.

Read `references/site-spec.md`. Create `.gcw/SITE_SPEC.md` as a draft; do not finalize it until teardown evidence and required companion-skill results have been integrated. Mark absent capabilities `N/A`. Represent every implementation-critical conclusion in the section 9 subsystem table with fidelity and truth labels; never hide differences behind one percentage.

## 3. Gather real evidence

Search official repositories, source maps, framework metadata, and public deployment evidence first. Verify licenses. Keep source, deployed artifacts, and editable implementation separate. GCW rejects credential-bearing URLs and document redirects outside the configured origin.

Run inventory where Playwright is available:

```text
node <skill-root>/scripts/site_inventory.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/site-inventory.json
```

This command also writes `.gcw/evidence/route-map.json`, `.gcw/evidence/network/requests.json`, and `.gcw/evidence/source-maps.json`. Source-map evidence records response-header or comment directives, conventional `.map` probes, reachability, and redacted URLs.

Generate a narrow interaction-state draft where Playwright is available:

```text
node <skill-root>/scripts/detect_interaction_states.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/interaction-states.json
```

The detector records observed `:hover`, `:focus`/`:focus-visible`, and common `aria-expanded` toggles with before/after screenshots. Its output is deliberately `reviewStatus: pending`: remove false positives, add important script-driven states it cannot discover, then set `reviewStatus` to `confirmed`. Finalization rejects an unreviewed generated draft.

Verify routes, breakpoints, DOM roots, overlays, scroll containers, input states, loading/stable states, GPU/media/workers/iframes, and external data manually. Cross-origin CSS, pseudo-element-only changes, canvas state, and multi-step interactions remain manual discovery scope.

During every standard or deep `TEARDOWN_PHASE`, invoke `design-dna` and preserve its complete JSON at `.gcw/evidence/design-dna/design-dna.json`. Minimal teardown recommends the same evidence but does not block finalization when it is absent. Summarize implementation-critical findings in `SITE_SPEC.md`; do not copy the sibling schema into a second GCW document. If required `design-dna` is unavailable, stop and tell the user what must be installed; do not substitute an unstructured guess.

If Canvas, WebGL, WebGPU, or shaders are detected, also invoke `web-shader-extractor`. Preserve its native artifacts under `.gcw/evidence/web-shader-extractor/` and reach `TARGET_LOCKED` plus `REPLAY_READY`; teardown does not require Raw Replay or QA Report. If the required companion is unavailable, stop before finalization. When reconnaissance confirms no qualifying GPU surface, set `gpu-decision.json` to `not-applicable` and reference the supporting inventory evidence.

Only after these decisions and calls are complete, integrate their results into `SITE_SPEC.md`, remove every `REQUIRED` placeholder, then run:

```text
python <skill-root>/scripts/finalize_teardown.py <workspace>
```

The finalizer validates companion artifacts, updates `teardown-manifest.json` and `evidence-index.json`, and marks SITE_SPEC final. Apply the same contract when teardown is the final outcome; study-only work changes the stopping point, not teardown depth.

## 4. Build the scoped faithful baseline

Restore only agreed pages, components, and states. Preserve deep links and responsive behavior. Replace unavailable services with explicit fixtures. Verify production build and preview, then run route checks:

```text
python <skill-root>/scripts/route_smoke.py --base-url <preview-url> --route / --route /example
```

SPA HAR fixtures are explicit opt-in. Set a narrow `harFixture.urlFilter` in the reviewed capture config, add third-party API origins to `harFixture.rebaseOrigins` when needed, then record and replay per-scenario fixtures:

```text
node <skill-root>/scripts/capture_compare.mjs --config <capture-scenarios.json> --output <record-results> --record-har <har-dir>
node <skill-root>/scripts/capture_compare.mjs --config <offline-capture-scenarios.json> --output <replay-results> --replay-har <har-dir>
```

Recording strips credential headers/cookies, redacts sensitive query/body fields, and rebases captured service origins to the candidate origin before persisting each HAR. Replay blocks Service Workers, serves HAR matches first, blocks non-local misses, and records fallbacks/blocked requests in `capture-manifest.json`. For a fully offline fixture check, point both replay URLs at the local candidate preview and verify no candidate-side API path appears in `harFixtures.fallbacks`.

For asset-heavy or offline work, read `references/asset-provenance.md` and generate a non-overwriting draft from inventory:

```text
python <skill-root>/scripts/generate_asset_manifest.py <workspace>/.gcw/evidence/site-inventory.json --out <workspace>/.gcw/asset-manifest.json
```

The generator classifies and deduplicates static resources, proposes deterministic local paths, excludes API noise, and redacts unsafe URLs. It writes `reviewStatus: pending`; confirm reuse rights, purpose, attribution, scope, and paths before changing the status to `confirmed` and running `download_assets.py`. It never downloads or overwrites an existing manifest.

For final clean/creative builds, read `references/runtime-independence.md`. Recovery configuration instead reads `references/recovery-tiers.md` and `references/gates.md` and adds provenance, hashes, replay strategy, route/deploy continuity, Known Gaps, and maintained CI.

## 5. Verify matched states

Read `references/qa-scenarios.md` and `references/tooling.md`:

```text
node <skill-root>/scripts/capture_compare.mjs --config <capture-scenarios.json> --output <results-dir>
python <skill-root>/scripts/batch_image_diff.py <results-dir> --diff-dir <results-dir>/diff
```

Match viewport, DPR, route, pointer, scroll, seed, readiness, and time phase. Inspect screenshots and Diff images. Produce `CLONE_REPORT.md` with subsystem fidelity and Known Gaps. Leave a local `faithful-baseline` checkpoint only when the user permits commits.

## 6. Stop at REVIEW_GATE

Present the baseline, preview, screenshots, Diff, `CLONE_REPORT.md`, and Known Gaps. Do not begin creative changes until the user chooses:

- A: fidelity insufficient; return to `FAITHFUL_CLONE`.
- B: baseline accepted; stop.
- C: baseline accepted for innovation; create `.gcw/CREATIVE_BRIEF.md`, then enter `CREATIVE_REBUILD`.

Use `scripts/advance_workflow.py` to record transitions. Entering `REVIEW_GATE` requires a non-empty `CLONE_REPORT.md`; leaving it requires `--decision A|B|C`, and the selected destination must match the list above. Decision C additionally requires a completed `CREATIVE_BRIEF.md`; the script never creates or fills that proof itself. It refuses to leave teardown until `finalize_teardown.py` has passed.

## 7. Close out honestly

Re-run promised QA, report skipped checks, and distinguish observed behavior, licensed reuse, and original implementation. Remove tracking and original-brand residue before publishing an adaptation. Never push, tag, release, or deploy without user authorization.
