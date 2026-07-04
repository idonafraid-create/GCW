#!/usr/bin/env python3
"""Advance a GCW project through explicit workflow gates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TRANSITIONS = {
    "TEARDOWN_PHASE": {"FAITHFUL_CLONE", "COMPLETE"},
    "FAITHFUL_CLONE": {"REVIEW_GATE"},
    "REVIEW_GATE": {"FAITHFUL_CLONE", "COMPLETE", "CREATIVE_REBUILD"},
    "CREATIVE_REBUILD": {"COMPLETE"},
}

REVIEW_DESTINATIONS = {"A": "FAITHFUL_CLONE", "B": "COMPLETE", "C": "CREATIVE_REBUILD"}
CREATIVE_BRIEF_SECTIONS = (
    "Keep",
    "Remove",
    "Change",
    "New brand, content, and features",
    "Innovation direction",
    "Final acceptance target",
)


def require_nonempty_file(path: Path, label: str) -> str:
    if not path.is_file():
        raise ValueError(f"{label} is required: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"{label} must not be empty: {path}")
    return text


def validate_creative_brief(path: Path) -> None:
    text = require_nonempty_file(path, "CREATIVE_BRIEF.md")
    matches = list(re.finditer(r"^## (.+?)\s*$", text, re.MULTILINE))
    sections = {match.group(1): match for match in matches}
    missing = [name for name in CREATIVE_BRIEF_SECTIONS if name not in sections]
    if missing:
        raise ValueError(f"CREATIVE_BRIEF.md is missing sections: {', '.join(missing)}")
    for name in CREATIVE_BRIEF_SECTIONS:
        match = sections[name]
        next_start = min((item.start() for item in matches if item.start() > match.start()), default=len(text))
        if not text[match.end():next_start].strip():
            raise ValueError(f"CREATIVE_BRIEF.md section is empty: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--to", required=True, choices=sorted({phase for values in TRANSITIONS.values() for phase in values}))
    parser.add_argument("--decision", choices=sorted(REVIEW_DESTINATIONS))
    args = parser.parse_args()
    root = args.workspace.resolve() / ".gcw"
    state_path = root / "run-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    current = state.get("currentPhase", state.get("state"))
    if args.to not in TRANSITIONS.get(current, set()):
        parser.error(f"invalid transition: {current} -> {args.to}")
    if current == "REVIEW_GATE":
        if args.decision is None:
            parser.error("leaving REVIEW_GATE requires --decision A, B, or C")
        expected = REVIEW_DESTINATIONS[args.decision]
        if args.to != expected:
            parser.error(f"review decision {args.decision} requires --to {expected}")
    elif args.decision is not None:
        parser.error("--decision is only valid when leaving REVIEW_GATE")
    if current == "TEARDOWN_PHASE":
        manifest_path = root / "teardown-manifest.json"
        if not manifest_path.is_file():
            parser.error("leaving TEARDOWN_PHASE requires teardown-manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "passed" or manifest.get("siteSpec", {}).get("status") != "final":
            parser.error("leaving TEARDOWN_PHASE requires scripts/finalize_teardown.py to pass")
    if args.to == "REVIEW_GATE":
        try:
            require_nonempty_file(root / "CLONE_REPORT.md", "CLONE_REPORT.md")
        except ValueError as error:
            parser.error(str(error))
    if args.to == "CREATIVE_REBUILD":
        try:
            validate_creative_brief(root / "CREATIVE_BRIEF.md")
        except ValueError as error:
            parser.error(str(error))
    if current == "REVIEW_GATE":
        decisions = state.setdefault("reviewDecisions", [])
        if not isinstance(decisions, list):
            parser.error("run-state.json reviewDecisions must be an array")
        decisions.append({
            "decision": args.decision,
            "from": current,
            "to": args.to,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        })
    state["currentPhase"] = args.to
    state["state"] = args.to
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"from": current, "to": args.to}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
