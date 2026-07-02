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

Read the workspace `AGENTS.md`, then initialize without overwriting evidence:

```text
python scripts/init_reconstruction.py <workspace> --url <canonical-url> --authorization <owned|licensed|authorized>
```

Read `references/site-spec.md`. Create `.gcw/SITE_SPEC.md` as a draft; do not finalize it until teardown evidence and required companion-skill results have been integrated. Mark absent capabilities `N/A`. Record subsystem-level `Exact`, `Approximate`, `Unknown`, or `Excluded`; never hide differences behind one percentage.

## 3. Gather real evidence

Search official repositories, source maps, framework metadata, and public deployment evidence first. Verify licenses. Keep source, deployed artifacts, and editable implementation separate. GCW rejects credential-bearing URLs and document redirects outside the configured origin.

Run inventory where Playwright is available:

```text
node scripts/site_inventory.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/site-inventory.json
```

Verify routes, breakpoints, DOM roots, overlays, scroll containers, input states, loading/stable states, GPU/media/workers/iframes, and external data manually.

During every `TEARDOWN_PHASE`, invoke `design-dna` and preserve its evidence for typography, color, spacing, layout, responsive rules, motion, and visual language. If `design-dna` is unavailable, stop and tell the user what must be installed; do not substitute an unstructured guess.

If Canvas, WebGL, WebGPU, or shaders are detected, also invoke `web-shader-extractor` and preserve the render/input/output evidence. If the required companion is unavailable, stop before finalization. When reconnaissance confirms no qualifying GPU surface, record GPU analysis as `N/A` with the supporting inventory evidence.

Only after these decisions and calls are complete, integrate their results into `SITE_SPEC.md` and finalize the teardown deliverables. Apply the same contract when teardown is the final outcome; study-only work changes the stopping point, not teardown depth.

## 4. Build the scoped faithful baseline

Restore only agreed pages, components, and states. Preserve deep links and responsive behavior. Replace unavailable services with explicit fixtures. Verify production build and preview, then run route checks:

```text
python scripts/route_smoke.py --base-url <preview-url> --route / --route /example
```

For asset-heavy or offline work, read `references/asset-provenance.md`. For final clean/creative builds, read `references/runtime-independence.md`. Recovery configuration instead reads `references/recovery-tiers.md` and `references/gates.md` and adds provenance, hashes, replay strategy, route/deploy continuity, Known Gaps, and maintained CI.

## 5. Verify matched states

Read `references/qa-scenarios.md` and `references/tooling.md`:

```text
node scripts/capture_compare.mjs --config <capture-scenarios.json> --output <results-dir>
python scripts/batch_image_diff.py <results-dir> --diff-dir <results-dir>/diff
```

Match viewport, DPR, route, pointer, scroll, seed, readiness, and time phase. Inspect screenshots and Diff images. Produce `CLONE_REPORT.md` with subsystem fidelity and Known Gaps. Leave a local `faithful-baseline` checkpoint only when the user permits commits.

## 6. Stop at REVIEW_GATE

Present the baseline, preview, screenshots, Diff, `CLONE_REPORT.md`, and Known Gaps. Do not begin creative changes until the user chooses:

- A: fidelity insufficient; return to `FAITHFUL_CLONE`.
- B: baseline accepted; stop.
- C: baseline accepted for innovation; create `.gcw/CREATIVE_BRIEF.md`, then enter `CREATIVE_REBUILD`.

Use `scripts/advance_workflow.py` to record transitions. Leaving teardown—whether for a faithful baseline or a study-only completion—requires `--design-dna-complete` and `--gpu-analysis <complete|na>`. The creative brief states what to keep, remove, change, add, the innovation direction, and final acceptance target.

## 7. Close out honestly

Re-run promised QA, report skipped checks, and distinguish observed behavior, licensed reuse, and original implementation. Remove tracking and original-brand residue before publishing an adaptation. Never push, tag, release, or deploy without user authorization.
