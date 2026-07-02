#!/usr/bin/env python3
"""Advance a GCW project through explicit workflow gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TRANSITIONS = {
    "TEARDOWN_PHASE": {"FAITHFUL_CLONE", "COMPLETE"},
    "FAITHFUL_CLONE": {"REVIEW_GATE"},
    "REVIEW_GATE": {"FAITHFUL_CLONE", "COMPLETE", "CREATIVE_REBUILD"},
    "CREATIVE_REBUILD": {"COMPLETE"},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--to", required=True, choices=sorted({phase for values in TRANSITIONS.values() for phase in values}))
    args = parser.parse_args()
    root = args.workspace.resolve() / ".gcw"
    state_path = root / "run-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    current = state.get("currentPhase", state.get("state"))
    if args.to not in TRANSITIONS.get(current, set()):
        parser.error(f"invalid transition: {current} -> {args.to}")
    if args.to == "CREATIVE_REBUILD":
        template = Path(__file__).resolve().parent.parent / "assets" / "creative-brief-template.md"
        brief = root / "CREATIVE_BRIEF.md"
        if not brief.exists():
            brief.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    state["currentPhase"] = args.to
    state["state"] = args.to
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"from": current, "to": args.to}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
