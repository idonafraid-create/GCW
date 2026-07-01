# GCW tooling

Use automation for deterministic collection and transformation. Use browser inspection and judgment for target attribution, animation semantics and visual acceptance.

| Tool | Purpose | Main output |
|---|---|---|
| `init_reconstruction.py` | Create non-destructive `.gcw/` evidence scaffolding | run state, known gaps, QA matrix, scenario config |
| `site_inventory.mjs` | Crawl public same-origin routes and record network/surface resources | `site-inventory.json` |
| `capture_compare.mjs` | Capture source/candidate pairs under matched conditions | PNG pairs + capture manifest |
| `image_diff.py` | Compare one same-size screenshot pair | JSON metric and optional diff image |
| `batch_image_diff.py` | Compare every `*.source.png`/`*.candidate.png` pair | JSON, Markdown and diff images |
| `route_smoke.py` | Verify public preview routes respond and optionally contain text | JSON route report |
| `blender_replace_text.py` | Create replacement 3D text matching reference bounds | GLB/GLTF model |
| `install_ci.py` | Install a self-contained GitHub visual-regression harness | `.gcw/` tools and workflow |

## Dependencies

- Python 3.10+
- Pillow for image diff: `python -m pip install Pillow`
- Node.js 20+
- Playwright for crawling/capture: `npm install playwright`
- A Playwright Chromium browser, or set `browserExecutable`/`GCW_BROWSER_EXECUTABLE` to an installed Chrome/Edge executable
- Blender 4.x only for 3D word replacement

Run `npm install`, `npm run install:browser` and `npm run check` from the GCW repository to verify the shared runtime before a recovery. If Blender is installed outside `PATH`, set `GCW_BLENDER_EXECUTABLE` to its full executable path.

## Determinism model

Every capture scenario must define `readySelector` or `readyFunction`. Replace the example `document.readyState === 'complete'` condition with an application-specific observable condition for animated sites, such as the final shell being visible or a loading canvas being removed.

`capture_compare.mjs` launches source and candidate in separate browser processes so heavy WebGL contexts do not starve each other. It injects the same seeded `Math.random`, installs the same virtual clock before navigation, advances both pages in equal 16 ms steps until both satisfy readiness, then advances the same settling and input delay. CSS/compositor animations are disabled during screenshot capture.

The controlled clock uses Playwright's official Clock API: <https://playwright.dev/docs/clock>. If an application cannot initialize while the clock is controlled, set `clockMode` to `realtime` and label the resulting temporal comparison `PARTIAL`.

This greatly reduces dynamic noise but cannot guarantee a zero diff for GPU drivers, video, cross-origin iframes, server timestamps, nondeterministic workers or compositor state created before readiness. Label such regions explicitly instead of loosening every threshold.

## Safety

- Crawl only routes inside the authorized origin unless the user expands scope.
- Use the final canonical URL. GCW performs a manual redirect-chain preflight and rejects document redirects that leave the configured origin.
- Do not submit forms, guess passcodes or bypass access controls.
- Inventory scripts collect URLs and metadata; they do not archive private responses.
- Review manifests for query strings or secrets before committing.
