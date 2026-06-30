#!/usr/bin/env python3
"""Compare two same-size screenshots and emit deterministic JSON metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance


def percentile_from_histogram(histogram: list[int], percentile: float) -> int:
    target = sum(histogram) * percentile
    seen = 0
    for value, count in enumerate(histogram):
        seen += count
        if seen >= target:
            return value
    return len(histogram) - 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--threshold", type=int, default=4)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()

    source = Image.open(args.source).convert("RGB")
    candidate = Image.open(args.candidate).convert("RGB")
    if source.size != candidate.size:
        parser.error(f"image sizes differ: {source.size} vs {candidate.size}")

    diff = ImageChops.difference(source, candidate)
    pixels = source.width * source.height
    pixel_data = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    changed = sum(1 for rgb in pixel_data if max(rgb) > args.threshold)
    histogram = diff.histogram()
    mean_abs = sum(value * count for value in range(256) for count in (
        histogram[value] + histogram[256 + value] + histogram[512 + value],
    )) / (pixels * 3)
    combined = [histogram[i] + histogram[256 + i] + histogram[512 + i] for i in range(256)]

    if args.diff:
        args.diff.parent.mkdir(parents=True, exist_ok=True)
        ImageEnhance.Contrast(diff).enhance(4).save(args.diff)

    print(json.dumps({
        "width": source.width,
        "height": source.height,
        "threshold": args.threshold,
        "meanAbs": round(mean_abs, 6),
        "changedPct": round(changed * 100 / pixels, 6),
        "p95ChannelDifference": percentile_from_histogram(combined, 0.95),
        "maxChannelDifference": max(i for i, count in enumerate(combined) if count),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
