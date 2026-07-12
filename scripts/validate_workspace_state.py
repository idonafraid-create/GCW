#!/usr/bin/env python3
"""Validate persisted GCW phase, teardown, and formal-review state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from advance_workflow import require_completed_file, validate_quality_gate


POST_TEARDOWN_PHASES = {"FAITHFUL_CLONE", "REVIEW_GATE", "CREATIVE_REBUILD", "COMPLETE"}


def load_object(path: Path, label: str) -> dict:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return value


def validate(workspace: Path) -> list[str]:
    errors: list[str] = []
    root = workspace / ".gcw"
    try:
        state = load_object(root / "run-state.json", "run-state.json")
    except ValueError as error:
        return [str(error)]

    phase = state.get("currentPhase")
    if phase != state.get("state"):
        errors.append(f"run-state phase mismatch: currentPhase={phase!r}, state={state.get('state')!r}")
    if phase not in {"TEARDOWN_PHASE", *POST_TEARDOWN_PHASES}:
        errors.append(f"unsupported current phase: {phase!r}")

    manifest = None
    try:
        manifest = load_object(root / "teardown-manifest.json", "teardown-manifest.json")
    except ValueError as error:
        errors.append(str(error))

    if manifest is not None and manifest.get("status") == "passed":
        if manifest.get("siteSpec", {}).get("status") != "final":
            errors.append("passed teardown requires siteSpec.status final")
        design = manifest.get("designDna", {})
        if design.get("required") is not True or design.get("status") != "passed":
            errors.append("passed teardown requires mandatory Design DNA status passed")
        analysis = state.get("analysisGates", {})
        if analysis.get("designDna") != "complete" or analysis.get("teardown") != "passed":
            errors.append("run-state analysisGates disagree with passed teardown")
        gpu_status = manifest.get("gpuAnalysis", {}).get("status")
        if analysis.get("gpuForensics") != gpu_status:
            errors.append("run-state gpuForensics disagrees with teardown manifest")

    if phase in POST_TEARDOWN_PHASES and (manifest is None or manifest.get("status") != "passed"):
        errors.append(f"phase {phase} requires a passed teardown manifest")

    reviewed = phase in {"REVIEW_GATE", "CREATIVE_REBUILD"} or (
        phase == "COMPLETE"
        and any(
            isinstance(item, dict) and item.get("from") == "REVIEW_GATE"
            for item in state.get("reviewDecisions", [])
        )
    )
    if reviewed:
        try:
            require_completed_file(root / "CLONE_REPORT.md", "CLONE_REPORT.md")
        except ValueError as error:
            errors.append(str(error))
        try:
            validate_quality_gate(workspace, root)
        except ValueError as error:
            errors.append(str(error))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    errors = validate(workspace)
    print(json.dumps({"workspace": str(workspace), "passed": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
