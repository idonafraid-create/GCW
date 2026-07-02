#!/usr/bin/env python3
"""Validate companion artifacts and finalize the GCW teardown gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SITE_SPEC_SECTIONS = tuple(str(index) for index in range(1, 13))


def ensure_safe_path(root: Path, path: Path) -> None:
    resolved = path.resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"artifact path leaves .gcw: {path}")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"artifact path must not use symlinks: {path}")
        current = current.parent


def load_json(path: Path, root: Path) -> dict:
    ensure_safe_path(root, path)
    if not path.is_file():
        raise ValueError(f"missing required artifact: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid JSON artifact: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return value


def validate_site_spec(path: Path, root: Path) -> str:
    ensure_safe_path(root, path)
    if not path.is_file():
        raise ValueError(f"missing required artifact: {path}")
    text = path.read_text(encoding="utf-8")
    if "Status: DRAFT" not in text and "Status: FINAL" not in text:
        raise ValueError("SITE_SPEC.md status must be DRAFT or FINAL")
    if "<!-- REQUIRED" in text:
        raise ValueError("SITE_SPEC.md still contains REQUIRED placeholders")
    matches = list(re.finditer(r"^## (\d+)\. .+$", text, re.MULTILINE))
    if tuple(match.group(1) for match in matches) != SITE_SPEC_SECTIONS:
        raise ValueError("SITE_SPEC.md must contain the 12 required numbered sections in order")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if not body:
            raise ValueError(f"SITE_SPEC.md section {match.group(1)} is empty")
    return text


def artifact_entry(root: Path, path: Path, kind: str, source_skill: str) -> dict[str, str]:
    return {
        "id": f"artifact-{kind}",
        "kind": kind,
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sourceSkill": source_skill,
    }


def require_nonempty_json(root: Path, path: Path) -> None:
    value = load_json(path, root)
    if not value:
        raise ValueError(f"required evidence is empty: {path}")


def evidence_files(root: Path, path: Path, suffixes: set[str] | None = None) -> list[Path]:
    files = [item for item in path.rglob("*") if item.is_file() and item.stat().st_size > 0]
    if suffixes is not None:
        files = [item for item in files if item.suffix.lower() in suffixes]
    if not files:
        raise ValueError(f"missing required evidence files under: {path}")
    for item in files:
        ensure_safe_path(root, item)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    root = args.workspace.resolve() / ".gcw"

    manifest_path = root / "teardown-manifest.json"
    manifest = load_json(manifest_path, root)
    site_spec_path = root / "SITE_SPEC.md"
    site_spec = validate_site_spec(site_spec_path, root)

    evidence_root = root / "evidence"
    fixed_json = {
        "site-inventory": evidence_root / "site-inventory.json",
        "route-map": evidence_root / "route-map.json",
        "interaction-states": evidence_root / "interaction-states.json",
    }
    for path in fixed_json.values():
        require_nonempty_json(root, path)
    desktop_screenshots = evidence_files(root, evidence_root / "screenshots" / "desktop", {".png", ".jpg", ".jpeg", ".webp"})
    mobile_screenshots = evidence_files(root, evidence_root / "screenshots" / "mobile", {".png", ".jpg", ".jpeg", ".webp"})
    network_evidence = evidence_files(root, evidence_root / "network")

    design_path = root / "evidence" / "design-dna" / "design-dna.json"
    design = load_json(design_path, root)
    required_design_keys = {"meta", "design_system", "design_style", "visual_effects"}
    if not required_design_keys.issubset(design) or any(not design[key] for key in required_design_keys):
        raise ValueError("design-dna.json must contain non-empty meta, design_system, design_style, and visual_effects")

    shader_root = root / "evidence" / "web-shader-extractor"
    decision_path = shader_root / "gpu-decision.json"
    decision = load_json(decision_path, root)
    gpu_decision = decision.get("decision")
    indexed = [
        *(artifact_entry(root, path, kind, "gcw") for kind, path in fixed_json.items()),
        *(artifact_entry(root, path, f"desktop-screenshot-{index}", "gcw") for index, path in enumerate(desktop_screenshots, 1)),
        *(artifact_entry(root, path, f"mobile-screenshot-{index}", "gcw") for index, path in enumerate(mobile_screenshots, 1)),
        *(artifact_entry(root, path, f"network-evidence-{index}", "gcw") for index, path in enumerate(network_evidence, 1)),
        artifact_entry(root, design_path, "design-dna", "design-dna"),
        artifact_entry(root, decision_path, "gpu-decision", "gcw"),
    ]
    if gpu_decision == "not-applicable":
        if not decision.get("checkedSurfaces") or not decision.get("detectionEvidence"):
            raise ValueError("GPU N/A requires checkedSurfaces and detectionEvidence")
        gpu_status = "not-applicable"
    elif gpu_decision == "required":
        scout_path = shader_root / "scout-card.json"
        replay_path = shader_root / "replay-manifest.json"
        scout = load_json(scout_path, root)
        replay = load_json(replay_path, root)
        if scout.get("lockStatus") != "locked" or scout.get("gateDecision", {}).get("targetLocked") is not True:
            raise ValueError("GPU teardown requires a TARGET_LOCKED scout-card.json")
        if replay.get("gateDecision", {}).get("replayReady") is not True:
            raise ValueError("GPU teardown requires a REPLAY_READY replay-manifest.json")
        if replay.get("unknowns", {}).get("blocking") or replay.get("gateDecision", {}).get("blockers"):
            raise ValueError("GPU teardown cannot finalize with blocking replay unknowns")
        indexed.extend([
            artifact_entry(root, scout_path, "shader-scout-card", "web-shader-extractor"),
            artifact_entry(root, replay_path, "shader-replay-manifest", "web-shader-extractor"),
        ])
        gpu_status = "replay-ready"
    else:
        raise ValueError("gpu-decision.json decision must be required or not-applicable")

    if manifest.get("blockingUnknowns"):
        raise ValueError("teardown-manifest.json has blockingUnknowns")

    finalized_at = datetime.now(timezone.utc).isoformat()
    site_spec_path.write_text(site_spec.replace("Status: DRAFT", "Status: FINAL", 1), encoding="utf-8")
    indexed.append(artifact_entry(root, site_spec_path, "site-spec", "gcw"))
    index_path = root / "evidence" / "evidence-index.json"
    evidence_index = load_json(index_path, root)
    existing = {
        entry.get("id"): entry
        for entry in evidence_index.get("entries", [])
        if isinstance(entry, dict) and not str(entry.get("id", "")).startswith("artifact-")
    }
    existing.update({entry["id"]: entry for entry in indexed})
    evidence_index["entries"] = list(existing.values())
    index_path.write_text(json.dumps(evidence_index, indent=2) + "\n", encoding="utf-8")

    manifest.update({"status": "passed", "finalizedAt": finalized_at})
    manifest["siteSpec"].update({"status": "final"})
    manifest["designDna"].update({"status": "passed"})
    manifest["gpuAnalysis"].update({"decision": gpu_decision, "status": gpu_status})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    state_path = root / "run-state.json"
    state = load_json(state_path, root)
    state["analysisGates"] = {"designDna": "complete", "gpuForensics": gpu_status, "teardown": "passed"}
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "gpuAnalysis": gpu_status, "finalizedAt": finalized_at}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
