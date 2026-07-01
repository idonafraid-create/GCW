---
name: gcw
description: Analyze, reproduce, and adapt public websites into runnable local projects with evidence-based verification. Use for GCW (Gao Copy Website), website cloning, learning from an excellent site, technical teardown, design-DNA extraction, layout or motion reproduction, WebGL/Canvas/shader reverse engineering, creative rebuilds, production-site recovery, route reconstruction, and source-versus-local visual regression.
---

# GCW — Gao Copy Website

Study how a public website actually works, reproduce the parts that matter, and verify the result in a real browser. Prefer real source and observable runtime evidence over plausible-looking AI guesses.

Remember three rules:

1. Find evidence before implementation.
2. Make it run before refactoring.
3. Compare before polishing.

## Boundaries

- Proceed only when the target is owned by the user, licensed for the intended reuse, or explicitly authorized. Ask only when authorization is ambiguous.
- Treat authenticated, passcode-only and private content as out of scope unless explicitly authorized.
- Do not bypass access controls or recover, ship or commit credentials.
- Check code, font, image, model and brand rights separately before public reuse.
- Label uncertain technical claims as `SOURCE`, `PARTIAL` or `GUESS`.
- Do not present deployed bundles as original authoring source.

## 1. Choose the goal before the tools

Read `references/clone-modes.md` and select one primary mode:

- `TEARDOWN`: understand the real design and implementation without promising a rebuild.
- `FAITHFUL_CLONE`: reproduce the observable site as closely as the evidence allows.
- `CREATIVE_REBUILD`: preserve selected structure, rhythm or interaction ideas while replacing the brand and content.
- `PRODUCTION_RECOVERY`: recover an owned deployed site when maintainable source is unavailable.

Record a short preflight:

```markdown
- Goal:
- Site type:
- Source availability:
- Reuse boundary:
- High-confidence scope:
- Approximate or excluded scope:
- Recommended path:
```

Do not make every project pay the cost of production recovery. Use the lightest evidence and verification that can support the selected goal.

## 2. Look for the real implementation first

Before scraping or rebuilding:

- Search the site name, product name, domain owner and deployment slug for an official public repository.
- Inspect source maps, framework metadata and public deployment artifacts.
- Verify repository and asset licenses; public availability is not permission to redeploy.
- Keep original source, deployed artifacts and your editable implementation clearly separated.
- Use the final canonical HTTP(S) URL. GCW rejects credential-bearing URLs and document redirects that leave the configured origin.

When official reusable source exists, start from it. When it does not, continue with runtime reconnaissance and state what remains unknown.

## 3. Initialize the project record

Read the workspace `AGENTS.md`. If this machine has not been verified, run `npm install`, `npm run install:browser` and `npm run check` in the GCW repository.

Create a non-destructive project record:

```text
python scripts/init_reconstruction.py <workspace> --url <canonical-url> --authorization <owned|licensed|authorized>
```

Use `.gcw/` for manifests, screenshots, reports and known gaps. Do not overwrite existing evidence silently.

## 4. Recon the site and classify its surfaces

Run the inventory when Node.js and Playwright are available:

```text
node scripts/site_inventory.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/network/site-inventory.json
```

Then verify what automation cannot infer reliably:

- routes, page families, deep links and responsive breakpoints
- DOM roots, fixed overlays and inner scroll containers
- hover, click, drag, scroll, time, resize, theme and storage states
- Canvas, WebGL, WebGPU, workers, iframes, video, audio and lazy resources
- loading state versus the stable application state
- public APIs and data dependencies that need local fixtures

Use `web-shader-extractor` for Canvas/WebGL/WebGPU ownership, shaders and render pipelines. Use `design-dna` when the goal is to preserve typography, spacing, palette, layout, motion or visual language rather than byte-level artifacts.

## 5. Choose the implementation path

Select the path from evidence and site type:

| Evidence or site type | Default path |
|---|---|
| Official reusable source | Run and adapt the source within its license |
| Simple static site | Preserve public files and URL paths, then remove tracking and replace content |
| Content-heavy React/Vue/Next site | Rebuild page templates and use public or local fixture data |
| Multi-page marketing site | Map routes and page families before building shared templates |
| Interaction-heavy site | Capture states first, then reproduce the state transitions |
| WebGL/Canvas site | Recover the render/input/output model before projectizing it |
| Visual inspiration only | Extract Design DNA and build an original implementation |
| Lost-source production site | Read `references/recovery-tiers.md` and `references/gates.md`, then establish a verified replay oracle |

Do not archive or copy third-party artifacts that the selected mode does not need.

## 6. Build a runnable local project

- Keep a stable reference or evidence record while editing the new project.
- Restore every in-scope route, not only the homepage.
- Preserve navigation and deep-link behavior on the chosen host.
- Replace unavailable server behavior with explicit fixtures or safe fallbacks.
- Verify the production build and static preview, not only the dev server.

Run route checks where applicable:

```text
python scripts/route_smoke.py --base-url <preview-url> --route / --route /example
```

## 7. Verify in a real browser

Read `references/qa-scenarios.md` and `references/tooling.md`.

Define source and candidate scenarios, then capture matched states:

```text
node scripts/capture_compare.mjs --config <capture-scenarios.json> --output <results-dir>
python scripts/batch_image_diff.py <results-dir> --diff-dir <results-dir>/diff
```

Match viewport, DPR, route, pointer, scroll, random seed, readiness and time phase. Inspect the screenshots and diff images; a single global score cannot explain interaction or compositor failures.

Do not hide missing wiring by tuning colors, offsets or animation speed. Keep phase-sensitive regions separate from deterministic failures.

## 8. Deliver the learning, not only the clone

Output only the documents required by the selected mode:

- `TEARDOWN.md`: real implementation, evidence level and transferable techniques
- `DESIGN_DNA.json`: design system, visual language and effects for a creative rebuild
- `REPLACE_GUIDE.md`: where to replace text, media, color, fonts, models and data
- `CLONE_REPORT.md`: source-versus-local comparison, tradeoffs and known gaps
- runnable project, build command and deployment notes

For advanced asset cases such as text baked into GLTF/GLB geometry, read `references/special-cases.md` instead of expanding the main workflow.

## 9. Harden only when needed

For maintained projects or production recovery, install the screenshot regression runner:

```text
python scripts/install_ci.py <project-root> --source-url <canonical-url>
```

CI is optional for a one-off teardown or learning exercise. When installed, it must upload screenshots, diffs and reports even when thresholds fail.

## 10. Close out honestly

- Re-run the build and the QA scenarios promised in preflight.
- Record known gaps and the next evidence needed; never invent successful interactions.
- Remove tracking and original brand residue before publishing an adapted version.
- Leave a clean Git checkpoint; never push without user authorization.
- Distinguish original ideas, reused licensed assets, observed behavior and your own implementation.
