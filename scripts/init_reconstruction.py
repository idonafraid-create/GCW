#!/usr/bin/env python3
"""Create non-destructive GCW evidence scaffolding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from url_safety import validate_public_url, validate_relative_route


EVIDENCE_DIRS = ("screenshots", "dom", "network", "runtime", "source", "gpu")


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--authorization", choices=("unconfirmed", "owned", "licensed", "authorized"), default="unconfirmed")
    args = parser.parse_args()

    try:
        validate_public_url(args.url, "--url")
        for route in args.route:
            validate_relative_route(route, "--route")
    except ValueError as error:
        parser.error(str(error))
    parsed = urlparse(args.url)

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        parser.error(f"workspace does not exist: {workspace}")

    root = workspace / ".gcw"
    evidence = root / "evidence"
    for name in EVIDENCE_DIRS:
        (evidence / name).mkdir(parents=True, exist_ok=True)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "config").mkdir(parents=True, exist_ok=True)

    routes = args.route or [parsed.path or "/"]
    state = {
        "schemaVersion": 3,
        "skill": "gcw",
        "sourceUrl": args.url,
        "permissionBoundary": args.authorization,
        "routes": routes,
        "state": "SCOPE",
        "gates": {
            "scope": False,
            "discovery": False,
            "targetLock": False,
            "replayReady": False,
            "baselineVerified": False,
            "projectVerified": False,
            "automationReady": False,
        },
        "cloneMode": "",
        "implementationPath": "",
        "recoveryStrategy": "",
        "blockingUnknowns": [],
        "evidence": [],
    }

    scenarios = {
        "sourceUrl": args.url.rstrip("/"),
        "candidateUrl": "http://127.0.0.1:4173",
        "browserExecutable": "",
        "seed": 20260630,
        "scenarios": [
            {
                "id": "desktop-top",
                "route": routes[0],
                "viewport": {"width": 1280, "height": 720},
                "deviceScaleFactor": 1,
                "clockMode": "controlled",
                "clockStepMs": 16,
                "readyTimeoutMs": 30000,
                "readyFunction": "document.readyState === 'complete'",
                "readyDelayMs": 2000,
                "phaseMs": 0,
                "scroll": {"x": 0, "y": 0},
                "pointer": {"x": 640, "y": 360},
            }
        ],
    }

    created = []
    files = {
        root / "run-state.json": json.dumps(state, indent=2) + "\n",
        root / "known-gaps.md": "# Known gaps\n\n| Gap | Severity | Evidence | Impact | Next step |\n|---|---|---|---|---|\n",
        root / "qa-matrix.md": "# QA matrix\n\n| Scenario | Source | Candidate | Conditions | Result |\n|---|---|---|---|---|\n",
        root / "config" / "capture-scenarios.json": json.dumps(scenarios, indent=2) + "\n",
    }
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(str(path.relative_to(root)))

    print(json.dumps({"root": str(root), "created": created}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
