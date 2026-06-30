---
name: gcw
description: Recover an authorized public production website into a local, deployable and evidence-verified project. Use for GCW (Gao Copy Website), production-site reconstruction, deployed-site recovery after source loss, route and asset archival, WebGL or shader forensics, responsive layout recovery, deterministic source-versus-local screenshots, visual regression, GLTF word replacement, and CI screenshot gates.
---

# GCW — Gao Copy Website

Recover the observable public website into a local project without pretending that minified browser artifacts are the original authoring source. Build an evidence chain, select the correct recovery tier, and prove fidelity across routes, time, pointer, scroll and responsive states.

## Non-negotiable boundaries

- Confirm that the user owns the site or is authorized to reconstruct it.
- Treat authenticated, passcode-only and private content as out of scope unless explicitly authorized.
- Never recover, ship or commit exposed credentials. Record the external dependency and provide a safe fallback.
- Label facts as `SOURCE`, `PARTIAL` or `GUESS`.
- Keep exact production artifacts separate from editable approximations.
- Do not mark complete while any P0, P1 or P2 issue remains open.

## 1. Initialize durable evidence

1. Read the workspace `AGENTS.md`.
2. Run `npm install`, `npm run install:browser` and `npm run check` in the GCW repository when the environment has not been verified on this machine.
3. Record the canonical URL, route scope and permission boundary.
4. Run:

```powershell
python scripts/init_reconstruction.py <workspace> --url <canonical-url>
```

Use the generated `.gcw/` directory for manifests, screenshots, reports and known gaps. Never overwrite existing evidence silently.

## 2. Discover routes, resources and rendering surfaces

Run the automatic inventory when Node.js and Playwright are available:

```powershell
node scripts/site_inventory.mjs --url <canonical-url> --out <workspace>\.gcw\evidence\network\site-inventory.json
```

Then use browser inspection to verify what automation cannot infer reliably:

- DOM roots, fixed overlays and inner scroll containers
- Canvas/WebGL/WebGPU ownership and worker boundaries
- iframes, videos, fonts, audio, models and lazy resources
- public same-origin routes and deep-link behavior
- pointer, scroll, time, resize, theme and storage inputs
- entry/loading state versus stable application state

For Canvas, WebGL, WebGPU, shaders, particles or post-processing, invoke `web-shader-extractor` and wait for target-lock and replay-ready gates. Invoke `design-dna` for typography, spacing, palette, layout and responsive extraction.

## 3. Archive exact public artifacts

- Save public HTML, CSS, JavaScript chunks, route documents, fonts, images, audio, models and shader text.
- Preserve original URL paths required by the runtime.
- Hash critical artifacts and protect byte-identical bundles from line-ending conversion.
- Store source provenance and capture conditions beside each artifact.
- Scan archived JavaScript and configuration for credentials before projectization.

## 4. Choose a recovery tier

Read `references/recovery-tiers.md` and choose the highest evidence-supported tier:

- `ARTIFACT_REPLAY`: serve exact public production artifacts locally.
- `PIPELINE_REPLAY`: rebuild the recovered render graph and runtime wiring.
- `EDITABLE_REBUILD`: replace artifacts with maintainable components that still pass baseline regression.

Prefer a verified artifact replay as the regression oracle before attempting an editable rebuild.

## 5. Recover the build and routes

- Restore every public route in scope, not only the homepage.
- Keep same-origin navigation functional on the chosen static host.
- Record any unavoidable difference caused by unavailable server/RSC behavior.
- Verify the production build and static preview, not only the dev server.
- Run route smoke checks:

```powershell
python scripts/route_smoke.py --base-url <preview-url> --route / --route /example
```

## 6. Run deterministic visual regression

Read `references/qa-scenarios.md` and `references/tooling.md`.

1. Copy `assets/capture-scenarios.example.json` to the project and describe source URL, candidate URL and scenarios.
2. Capture source and candidate in paired pages with the same random seed, viewport, DPR, route, pointer, scroll and frozen JS phase:

```powershell
node scripts/capture_compare.mjs --config <capture-scenarios.json> --output <results-dir>
```

3. Generate numeric metrics, diff images and Markdown/JSON reports:

```powershell
python scripts/batch_image_diff.py <results-dir> --diff-dir <results-dir>\diff
```

Compare source → verified baseline, then baseline → editable project. Keep phase-sensitive compositor regions separate from deterministic failures. Do not hide missing wiring by tuning colors or offsets.

## 7. Replace baked 3D words safely

When visible text is baked into GLTF/GLB geometry, do not search for a JavaScript string. Use Blender to generate a replacement mesh while matching the reference model bounds:

```powershell
blender --background --python scripts/blender_replace_text.py -- `
  --reference <old-model.gltf> --text "NEW WORD" --output <new-model.glb> `
  --font <font-file.ttf>
```

The script provides a repeatable geometry baseline, not automatic recreation of hand-drawn lettering. Validate desktop/mobile framing, origin, material assignment, pointer response and overlap after replacement.

## 8. Install CI screenshot regression

Use the installer to copy the self-contained GCW runner and GitHub Actions template into a target repository:

```powershell
python scripts/install_ci.py <project-root> --source-url <canonical-url>
```

Then edit `.gcw/capture-scenarios.json`, set the source URL, verify the preview command/port in `.github/workflows/gcw-visual-regression.yml`, and commit the generated files. CI must upload screenshots, diffs and reports even when thresholds fail.

## 9. Close out

- Re-run build, route smoke tests and the required QA matrix.
- Record fidelity metrics, phase-sensitive differences and every known gap.
- Leave a clean Git checkpoint; never push without user authorization.
- Write deployment notes and a compact handoff that points to evidence instead of duplicating it.
- State unrecoverable limits: original source names/history/comments, unavailable server logic, private content and external credentials.

## Required outputs

- Reproducible local project and production build command
- Permission boundary and route scope
- Site inventory and resource/network manifest
- Source/asset provenance and hashes
- Recovery-tier decision
- Render/input/output model for advanced surfaces
- Multi-state desktop/mobile QA with numeric diffs
- Known gaps with severity and next evidence required
- Deployment notes, Git checkpoint and handoff
