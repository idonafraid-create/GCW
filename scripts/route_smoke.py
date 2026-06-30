#!/usr/bin/env python3
"""Smoke-test public routes on a GCW preview server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    checks = [{"route": route} for route in args.route]
    if args.manifest:
        loaded = json.loads(args.manifest.read_text(encoding="utf-8"))
        checks.extend(loaded.get("routes", loaded if isinstance(loaded, list) else []))
    if not checks:
        checks = [{"route": "/"}]

    results = []
    for check in checks:
        route = check["route"] if isinstance(check, dict) else str(check)
        expected = check.get("contains") if isinstance(check, dict) else None
        url = urljoin(args.base_url.rstrip("/") + "/", route.lstrip("/"))
        result = {"route": route, "url": url, "status": None, "passed": False, "error": None}
        try:
            request = Request(url, headers={"User-Agent": "GCW route smoke/1.0"})
            with urlopen(request, timeout=args.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                result["status"] = response.status
                result["passed"] = response.status < 400 and (not expected or expected in body)
                if expected and expected not in body:
                    result["error"] = f"expected text not found: {expected}"
        except HTTPError as error:
            result.update(status=error.code, error=str(error))
        except URLError as error:
            result["error"] = str(error)
        results.append(result)

    report = {"baseUrl": args.base_url, "passed": all(item["passed"] for item in results), "routes": results}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

