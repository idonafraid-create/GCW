# SITE_SPEC contract

Every task creates `.gcw/SITE_SPEC.md` as the unique implementation specification. Initialize it as a draft, then finalize it only after the complete teardown sequence. Keep all 12 numbered sections; write `N/A` rather than deleting an inapplicable section.

Fixed evidence is `.gcw/evidence/site-inventory.json`, `route-map.json`, `interaction-states.json`, desktop/mobile screenshots, and `network/`. Add a full route map for multiple page families, state timelines for complex motion, an asset inventory for asset-heavy work, and provenance/hashes/recovery strategy for recovery work.

Run `design-dna` during every teardown and preserve its raw evidence under `.gcw/evidence/design-dna/`. For detected Canvas/WebGL/WebGPU/shader surfaces, run `web-shader-extractor` and preserve its render/input/output evidence under `.gcw/evidence/gpu/`; otherwise record `N/A` with inventory evidence. Integrate these results before finalizing `SITE_SPEC.md`, even when teardown is the final outcome.

Record each subsystem as `Exact`, `Approximate`, `Unknown`, or `Excluded`, with evidence and acceptance criteria. Copy final results into `CLONE_REPORT.md`.
