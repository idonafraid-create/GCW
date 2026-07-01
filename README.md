# GCW

Evidence-driven website cloning, technical teardown, and creative reconstruction.

<p align="center">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<img src="./assets/banner.webp" alt="GCW — evidence-driven website cloning" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

Found a website worth learning from? GCW helps an agent discover how it actually works, reproduce the important parts as a runnable local project, and verify the result in a real browser.

GCW prefers official source and observable runtime evidence over plausible-looking AI guesses. It keeps deployed artifacts, inferred behavior, and your editable implementation clearly separated.

> Find evidence before implementation. Make it run before refactoring. Compare before polishing.

## What you can do

| Goal | Result |
|---|---|
| Learn how a site works | A technical teardown with evidence and transferable techniques |
| Clone an excellent site | A runnable local project with route, responsive, interaction and visual checks |
| Rebuild it as your own | Design DNA, replacement guidance and an original editable implementation |
| Recover an owned deployed site | A verified replay or maintainable rebuild when source is unavailable |

GCW covers static pages, React/Vue/Next content sites, multi-page marketing sites, animation-heavy experiences, and Canvas/WebGL/WebGPU frontends. Authentication, private server logic, payment, permissions and proprietary APIs are outside the default boundary.

Ordinary websites are first-class use cases. GCW's distinctive strength is that the same workflow can continue into motion-heavy, interaction-heavy and GPU-rendered sites without abandoning evidence or browser verification.

## How it works

1. **Choose the goal** — teardown, faithful clone, creative rebuild, or production recovery.
2. **Find the real implementation** — search official repositories, source maps and public deployment evidence before rebuilding.
3. **Recon the site** — map routes, resources, breakpoints, interactions and advanced rendering surfaces.
4. **Choose a path** — reuse licensed source, preserve a simple static site, rebuild templates, capture fixtures, or recover a render pipeline.
5. **Build locally** — keep the reference separate while producing editable code.
6. **Verify in a browser** — compare routes and matched desktop/mobile interaction states.
7. **Deliver the learning** — leave a teardown, Design DNA, replacement guide or clone report when useful.

<img src="./assets/features.webp" alt="GCW workflow: public evidence, local reconstruction, verification, and deployment" width="100%">

## Quick start

### 1. Install GCW

Clone this repository as the canonical source:

```bash
git clone https://github.com/idonafraid-create/GCW.git /path/to/GCW
```

Link it into the singular `.agent/skills` directory used by this workspace.

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

### 2. Verify the toolkit

```bash
cd /path/to/GCW
npm install
npm run install:browser
python -m pip install -r requirements.txt
npm run check
```

`npm run check` verifies runtime dependencies and companion-skill discovery. A passing environment check does not prove that a particular clone is complete.

Before publishing changes to GCW itself, run the complete release suite:

```bash
npm run verify
```

This runs syntax checks, local HTTP/Chromium workflow tests, URL and credential-boundary tests, image-diff gates, CI-installer tests, and the environment check.

### 3. Ask for the outcome you want

```text
Use $gcw to study this site, explain its real implementation, and produce a technical teardown: https://example.com/
```

```text
Use $gcw to create a faithful local clone of this authorized public site: https://example.com/
```

```text
Use $gcw to extract the design DNA and rebuild this reference with my own content: https://example.com/
```

The skill performs a short preflight before choosing the tools and scope.

## Advanced analysis

GCW can coordinate two companion skills when a project needs deeper analysis:

- [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor) for Canvas, WebGL, WebGPU, shaders and render pipelines.
- [design-dna](https://github.com/zanwei/design-dna) for typography, spacing, palette, layout, motion and visual language.

Install them in the same singular `.agent/skills` root. GCW's inventory, route checks and screenshot comparison scripts work without them; advanced GPU forensics and structured design extraction do not.

## What GCW can leave behind

- A runnable local project and production build command
- `TEARDOWN.md` with verified implementation findings
- `DESIGN_DNA.json` for a creative rebuild
- `REPLACE_GUIDE.md` for text, media, color, font, model and data changes
- `CLONE_REPORT.md` with source-versus-local differences and known gaps
- Route and resource inventory
- Matched desktop/mobile screenshots, numeric diffs and visual reports
- Optional GitHub Actions screenshot regression

The selected mode determines which outputs are useful. A one-off teardown should not be forced through production-recovery paperwork.

## Toolkit

| Script | Purpose |
|---|---|
| `init_reconstruction.py` | Create a non-destructive `.gcw/` project record |
| `site_inventory.mjs` | Inventory public routes, resources, fonts and rendering surfaces |
| `capture_compare.mjs` | Capture matched source and candidate states |
| `batch_image_diff.py` | Generate metrics, diff images and Markdown/JSON reports |
| `route_smoke.py` | Check preview routes and representative text |
| `install_ci.py` | Install the GCW visual-regression runner and workflow |
| `blender_replace_text.py` | Optional playbook for text baked into GLTF/GLB geometry |

Read [SKILL.md](./SKILL.md) for the agent workflow. The [references](./references/) directory defines clone modes, production-recovery strategies, QA scenarios, tooling and special cases.

## Visual verification

Define source and candidate scenarios, then capture and compare matched states:

```bash
node scripts/capture_compare.mjs \
  --config /project/.gcw/capture-scenarios.json \
  --output /project/.gcw/results

python scripts/batch_image_diff.py \
  /project/.gcw/results \
  --diff-dir /project/.gcw/results/diff
```

GCW can align random seed, JavaScript time, viewport, DPR, route, pointer, scroll and readiness. GPU drivers, video, cross-origin frames, workers and compositor timing can still introduce noise; record those regions instead of weakening every threshold.

## Requirements

- Python 3.10+
- Node.js 20+
- Pillow
- Playwright and Chromium
- Blender 4.x only for the optional baked-3D-text playbook

## Safety and reuse

Use GCW only when the target is owned by the user, licensed for the intended reuse, or explicitly authorized.

- Do not bypass authentication, passcodes, paywalls or other access controls.
- Use the final canonical URL; credential-bearing URLs and cross-origin document redirects are rejected before browser capture.
- Check code and asset licenses separately before publishing a clone or adaptation.
- Remove tracking and original brand residue from creative rebuilds.
- Do not commit credentials found in public bundles or configuration.
- Mark technical conclusions as `SOURCE`, `PARTIAL` or `GUESS` when certainty matters.

## Acknowledgments

GCW coordinates the independently maintained `web-shader-extractor` and `design-dna` workflows; it does not vendor their source. See the upstream repositories for current licenses and updates.

## License

GCW is available under the [MIT License](./LICENSE).
