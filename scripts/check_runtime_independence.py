#!/usr/bin/env python3
"""Fail when final runtime evidence still requests the source origin."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from url_safety import validate_public_url


def walk_urls(value: object):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_urls(child)
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        yield value


def origin(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(url)
    return parsed.scheme.lower(), (parsed.hostname or "").lower(), parsed.port


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--allow-origin", action="append", default=[])
    args = parser.parse_args()
    try:
        validate_public_url(args.source_url, "--source-url")
        for allowed in args.allow_origin:
            validate_public_url(allowed, "--allow-origin")
    except ValueError as error:
        parser.error(str(error))
    allowed = {origin(item) for item in args.allow_origin}
    source = origin(args.source_url)
    data = json.loads(args.evidence.read_text(encoding="utf-8"))
    blocked = sorted({url for url in walk_urls(data) if origin(url) == source and origin(url) not in allowed})
    report = {"passed": not blocked, "sourceOrigin": source, "blocked": blocked}
    print(json.dumps(report, indent=2))
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
