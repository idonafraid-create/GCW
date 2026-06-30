# GCW

Recover an authorized deployed website into a local, deployable project with evidence you can inspect.

<p align="center">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<img src="./assets/banner.webp" alt="GCW — evidence-driven website recovery" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

GCW stands for Gao Copy Website. It is an agent skill and a small toolkit for cases where a website owner has lost the source code but still controls the public production site.

GCW does not claim that minified browser artifacts are the original source. It records what came from production, what is only partially known, and what remains an informed guess. The result is a reproducible recovery project plus the evidence needed to test it.

## What GCW recovers

- Public routes, HTML, styles, scripts, fonts, images, audio, models, and shader text
- DOM, Canvas, WebGL, WebGPU, worker, iframe, and media surfaces
- Inputs driven by time, pointer, scroll, viewport, theme, storage, and UI state
- Desktop and mobile states with paired screenshots and numeric image diffs
- Static deployment behavior, route smoke tests, and a screenshot regression workflow for GitHub Actions

Authenticated pages, private server logic, original comments, Git history, and credentials stay outside the recovery boundary.

## Recovery tiers

| Tier | Use it when | Result |
|---|---|---|
| `ARTIFACT_REPLAY` | Public production artifacts still run locally | A byte-preserving baseline that acts as the visual oracle |
| `PIPELINE_REPLAY` | The render graph and runtime wiring can be reconstructed | A recovered WebGL or application pipeline |
| `EDITABLE_REBUILD` | Maintainable source is the goal | Readable components checked against the verified baseline |

<img src="./assets/features.webp" alt="GCW workflow: public evidence, recovery, verification, and deployment" width="100%">

GCW normally establishes an artifact replay first. That prevents an editable rewrite from drifting while it is still being built.

## Quick start

### 1. Install the two companion skills

Install these specialist skills before using GCW for the complete high-fidelity workflow:

```bash
npx skills add https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor
npx skills add zanwei/design-dna
```

`web-shader-extractor` covers Canvas, WebGL, WebGPU, shaders, and render pipelines. `design-dna` covers typography, spacing, palette, layout, responsive behavior, and visual effects. GCW's standalone inventory and comparison scripts can run without them, but the complete creative-site recovery workflow cannot.

If your agent uses a custom skill root, install both folders there. This workspace uses the singular `.agent/skills` path. If an installer proposes `.agents` here, cancel and install manually into `.agent/skills`; do not create a bridge directory.

### 2. Install GCW

Keep this repository as the canonical source and link it into your agent's skill directory with the folder name `gcw`.

Windows PowerShell:

```powershell
New-Item -ItemType Junction `
  -Path "D:\your-workspace\.agent\skills\gcw" `
  -Target "D:\path\to\GCW"
```

macOS or Linux:

```bash
ln -s /path/to/GCW /path/to/your-workspace/.agent/skills/gcw
```

Then invoke the skill in your agent:

```text
Use $gcw to recover this authorized production website into a verified local project: https://example.com/
```

### 3. Create the evidence workspace

```powershell
New-Item -ItemType Directory D:\work\site-recovery
python scripts\init_reconstruction.py D:\work\site-recovery `
  --url https://example.com/
```

GCW creates a `.gcw/` directory for run state, known gaps, QA scenarios, screenshots, manifests, and reports. Existing evidence is not overwritten silently.

### 4. Inventory the public site

```powershell
npm install
npm run install:browser
node scripts\site_inventory.mjs `
  --url https://example.com/ `
  --out D:\work\site-recovery\.gcw\evidence\network\site-inventory.json
```

Review the inventory before archiving resources. Remove secrets from query strings and keep the crawl inside the authorized origin.

## Agent compatibility

GCW can orchestrate the full workflow in an agent that loads `SKILL.md`, can run Python and Node.js, and has the companion skills available. The core scripts also work without an agent, so another automation system can call them directly.

The full workflow requires `web-shader-extractor` and `design-dna`. `browser-qa` is an optional enhancement because GCW already includes Playwright capture, route smoke tests, and numeric image diff tooling. Run `npm run check` to verify the two required skill roots along with Playwright, Chromium, Pillow, and the optional Blender executable. A directory junction or symbolic link is a normal installation method; all linked agents still read the same repository files.

## Visual verification

Define paired source and candidate scenarios in a capture config, then run:

```powershell
node scripts\capture_compare.mjs `
  --config D:\work\site-recovery\.gcw\capture-scenarios.json `
  --output D:\work\site-recovery\.gcw\results

python scripts\batch_image_diff.py `
  D:\work\site-recovery\.gcw\results `
  --diff-dir D:\work\site-recovery\.gcw\results\diff
```

The capture runner uses separate browser processes, a shared random seed, Playwright Clock, matched viewport and DPR, and paired readiness checks. GPU drivers, video, cross-origin iframes, workers, and compositor timing can still introduce noise. Record those regions instead of weakening every threshold.

## Toolkit

| Script | Purpose |
|---|---|
| `init_reconstruction.py` | Create a non-destructive evidence workspace |
| `site_inventory.mjs` | Inventory public routes, resources, fonts, and rendering surfaces |
| `capture_compare.mjs` | Capture matched source and candidate states |
| `batch_image_diff.py` | Generate metrics, diff images, and Markdown or JSON reports |
| `route_smoke.py` | Check public preview routes and expected text |
| `blender_replace_text.py` | Generate replacement GLTF or GLB text against reference bounds |
| `install_ci.py` | Install the GCW runner and GitHub Actions screenshot gate |

Read [SKILL.md](./SKILL.md) for the full workflow. The files in [references](./references/) cover recovery tiers, gates, QA scenarios, and dependencies.

## Requirements

- Python 3.10 or newer
- Node.js 20 or newer
- Pillow for image diffing
- Playwright and a Chromium browser for inventory and capture
- `web-shader-extractor` and `design-dna` for the complete high-fidelity workflow
- Blender 4.x or newer only when replacing baked 3D text

```powershell
python -m pip install -r requirements.txt
npm install
npm run install:browser
npm run check
```

## Validation

GCW separates toolkit validation from website validation. The repository checks its runtime dependencies, script syntax, evidence scaffolding, route smoke tests, image diff reports, CI installer, and optional Blender path.

Each recovered website still needs its own readiness condition, interaction matrix, visual thresholds, and known-gaps report. A passing toolkit check does not prove that a specific recovery is complete.

## Safety and scope

Use GCW only on websites you own or are authorized to recover.

- Do not bypass authentication, passcodes, paywalls, or access controls.
- Do not commit credentials found in public bundles or configuration.
- Keep exact production artifacts separate from editable approximations.
- Label recovered facts as `SOURCE`, `PARTIAL`, or `GUESS`.
- Do not call a recovery complete while a P0, P1, or P2 issue remains open.

## Acknowledgments

GCW uses two companion skills for specialist analysis:

- [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor), maintained by [lixiaolin94](https://github.com/lixiaolin94), provides the WebGL, WebGPU, Canvas, shader, and render-pipeline investigation workflow.
- [design-dna](https://github.com/zanwei/design-dna), maintained by [zanwei](https://github.com/zanwei), provides structured extraction of design tokens, visual style, and effects.

Thank you to both maintainers and their contributors for publishing these skills. GCW calls them as companion workflows and does not vendor their source code. Both upstream projects are available under the MIT License; follow their repositories for current terms and updates.

## License

GCW is available under the [MIT License](./LICENSE).
